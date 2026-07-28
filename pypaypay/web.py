"""Web 版 PayPay (www.paypay.ne.jp/app) のログイン。

アプリ 5.x の BFF (app4.paypay.ne.jp) は、ログイン画面を Web ポータルに丸投げして
いるので「OTP をここに入力して終わり」が出来ない（PAR → ブラウザ → callback URL）。
一方 Web 版 API には昔ながらの

    POST /app/v1/oauth/token   grant_type=password   → OTP が飛ぶ
    POST /app/v1/oauth/token   grant_type=otp        → アクセストークン

があるので、メアパス＋OTP だけでトークンが取れる。こっちを実装したのがこのモジュール。

    login = WebLogin("08012345678", "password")
    login.start()                    # ここで SMS / メールに OTP が届く
    token = login.verify("123456")

取れるトークンは Web 版のセッショントークンで、Web 側では
``Cookie: token=<...>`` として送る。BFF 側の Bearer トークンと同じものかは
別問題なので、:meth:`WebLogin.probe` で確かめられるようにしてある。
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    APIError, AuthError, LinkAlreadyClaimed, LinkPasscodeRequired, RateLimitedError,
)
from .parsing import parse_envelope
from .responses import AttrDict, Balance, LinkInfo, P2PCode, Profile

WEB_BASE = "https://www.paypay.ne.jp"
WEB_TOKEN_PATH = "/app/v1/oauth/token"
WEB_OTP_RESEND_PATH = "/app/v1/otp/mobile/resend/{ref}"
WEB_PROFILE_PATH = "/app/v1/getUserProfile"
WEB_BALANCE_PATH = "/app/v1/bff/getBalanceInfo"
WEB_HISTORY_PATH = "/app/v2/bff/getPay2BalanceHistory"
WEB_LINK_INFO_PATH = "/app/v2/p2p-api/getP2PLinkInfo"
WEB_LINK_ACCEPT_PATH = "/app/v2/p2p-api/acceptP2PSendMoneyLink"
WEB_LINK_REJECT_PATH = "/app/v2/p2p-api/rejectP2PSendMoneyLink"
WEB_P2PCODE_PATH = "/app/v1/p2p-api/createP2PCode"
WEB_PAYMENT_CODE_PATH = "/app/v2/bff/createPaymentOneTimeCodeForHome"

# 受け取り / 辞退のリクエストが要求する最低クライアントバージョン
MINIMUM_APP_VERSION = "3.45.0"

_LINK_CODE_RE = re.compile(r"([A-Za-z0-9_-]{10,})/?$")
JST = timezone(timedelta(hours=9))


def jst_now() -> str:
    """'2026-07-28T15:04:05+0900' — requestAt が要求する形式。"""
    return datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S%z")

# Web 版はブラウザとして見られるので、端末ヘッダーではなく普通の UA を送る。
WEB_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")


def web_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    h = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": WEB_USER_AGENT,
        "Content-Type": "application/json",
    }
    if access_token:
        h["Cookie"] = f"token={access_token}"
    return h


def _error_message(body: Any) -> str:
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            msg = error.get("message") or error.get("displayMessage")
            code = error.get("code") or error.get("errorCode")
            if msg:
                return f"[{code}] {msg}" if code else str(msg)
        for key in ("message", "displayMessage", "resultMessage"):
            if body.get(key):
                return str(body[key])
    return repr(body)


def _parse(resp: httpx.Response) -> Dict[str, Any]:
    if resp.status_code == 429:
        raise RateLimitedError("rate limited by PayPay web API")
    try:
        body = resp.json()
    except ValueError:
        raise AuthError(f"web API が JSON を返さなかった (HTTP {resp.status_code}): "
                        f"{resp.text[:200]}") from None
    if not isinstance(body, dict):
        raise AuthError(f"web API の応答が想定外: {body!r}")
    if body.get("response_type") == "ErrorResponse" or resp.status_code >= 400:
        raise AuthError(_error_message(body))
    return body


class WebLogin:
    """メアド/電話番号＋パスワード＋OTP で Web 版のトークンを取る。

    ``start()`` → OTP が届く → ``verify(otp)`` → アクセストークン。
    OTP が来なかったら ``resend()``。
    """

    def __init__(
        self,
        username: str,
        password: Optional[str] = None,
        *,
        client_uuid: Optional[str] = None,
        http: Optional[httpx.Client] = None,
        timeout: float = 20.0,
        proxy: Optional[str] = None,
    ) -> None:
        self.username = username
        self.password = password
        # ppaynode / PayPayOpenPy と同じく大文字の UUID を送る
        self.client_uuid = (client_uuid or str(uuid.uuid4())).upper()
        self._owns_http = http is None
        self._http = http or httpx.Client(timeout=timeout, proxy=proxy)

        self.otp_reference_id: Optional[str] = None
        self.otp_prefix: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    # ------------------------------------------------------------------
    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "WebLogin":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------
    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._http.post(f"{WEB_BASE}{path}", headers=web_headers(), json=body)
        return _parse(resp)

    def _store_tokens(self, payload: Dict[str, Any]) -> None:
        self.access_token = payload.get("access_token")
        self.refresh_token = payload.get("refresh_token")

    def _store_otp(self, payload: Dict[str, Any]) -> None:
        self.otp_reference_id = payload.get("otp_reference_id")
        self.otp_prefix = payload.get("otp_prefix")

    # ------------------------------------------------------------------
    def start(self) -> Dict[str, Any]:
        """パスワードでログインを開始する。

        OTP が要るときは ``otp_reference_id`` / ``otp_prefix`` を控えて、その
        payload を返す（``otp_required`` が True になる）。OTP 無しで通った
        場合は ``access_token`` がそのまま入ってくる。
        """
        if not self.password:
            raise AuthError("password required for web login")

        payload = self._post(WEB_TOKEN_PATH, {
            "scope": "SIGN_IN",
            "client_uuid": self.client_uuid,
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "add_otp_prefix": True,
            "language": "ja",
        })
        self._store_tokens(payload)
        self._store_otp(payload)
        if not self.access_token and not self.otp_reference_id:
            raise AuthError(f"ログイン応答に access_token も otp_reference_id も無い: {payload!r}")
        payload = dict(payload)
        payload["otp_required"] = not self.access_token
        return payload

    def verify(self, otp: str) -> str:
        """届いた OTP を入れてアクセストークンを取る。"""
        if not self.otp_reference_id:
            raise AuthError("start() を先に呼んで（otp_reference_id が無い）")

        payload = self._post(WEB_TOKEN_PATH, {
            "scope": "SIGN_IN",
            "client_uuid": self.client_uuid,
            "grant_type": "otp",
            "otp_prefix": self.otp_prefix,
            "otp": str(otp).strip(),
            "otp_reference_id": self.otp_reference_id,
            "username_type": "MOBILE",
            "language": "ja",
        })
        self._store_tokens(payload)
        if not self.access_token:
            raise AuthError(f"OTP 検証に access_token が付いてこなかった: {payload!r}")
        return self.access_token

    def resend(self) -> Dict[str, Any]:
        """OTP を送り直す。"""
        if not self.otp_reference_id:
            raise AuthError("start() を先に呼んで（otp_reference_id が無い）")
        payload = self._post(
            WEB_OTP_RESEND_PATH.format(ref=self.otp_reference_id),
            {"add_otp_prefix": "true"},
        )
        self._store_otp(payload)
        return payload

    # ------------------------------------------------------------------
    def probe(self) -> Dict[str, Any]:
        """取れたトークンが Web 版で通るか確認する（プロフィール取得）。"""
        if not self.access_token:
            raise AuthError("先に verify() でトークンを取って")
        resp = self._http.get(f"{WEB_BASE}{WEB_PROFILE_PATH}",
                              headers=web_headers(self.access_token))
        return _parse(resp)


class WebPayPay:
    """Web 版 API (www.paypay.ne.jp/app) のクライアント。

    OTP でログインできるのが利点。ただし叩けるエンドポイントは BFF より
    ずっと少なくて、送金リンクの *発行* や直接送金は Web 版には無い。
    使えるのは以下だけ:

        get_profile / get_balance / get_history
        link_check / link_receive / link_reject
        create_p2pcode / create_paymentcode

    メソッド名と戻り値の型は :class:`~pypaypay.PayPay` と揃えてあるので、
    この範囲なら書き換えずに差し替えられる。

        pp = WebPayPay("08012345678", "パスワード")
        if pp.login()["otp_required"]:
            pp.login_otp(input("OTP: "))
        print(pp.get_balance().all_balance)
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        access_token: Optional[str] = None,
        client_uuid: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: float = 20.0,
        http: Optional[httpx.Client] = None,
    ) -> None:
        self.username = username
        self.password = password
        self.access_token = access_token
        self._owns_http = http is None
        self._http = http or httpx.Client(timeout=timeout, proxy=proxy)
        self._login = WebLogin(username or "", password,
                               client_uuid=client_uuid, http=self._http)

    @property
    def client_uuid(self) -> str:
        return self._login.client_uuid

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "WebPayPay":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------
    # login
    # ------------------------------------------------------------------
    def login(self) -> Dict[str, Any]:
        """メアパスを送って OTP を飛ばす。``otp_required`` を見て分岐する。"""
        if not self.username:
            raise AuthError("username required to login()")
        payload = self._login.start()
        self.access_token = self._login.access_token
        return payload

    def login_otp(self, otp: str) -> str:
        """届いた OTP を入れてトークンを確定する。"""
        self.access_token = self._login.verify(otp)
        return self.access_token

    def resend_otp(self) -> Dict[str, Any]:
        return self._login.resend()

    @property
    def refresh_token(self) -> Optional[str]:
        return self._login.refresh_token

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, *, json: Any = None,
                 params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.access_token:
            raise AuthError("先にログインして（access_token が無い）")
        resp = self._http.request(method, f"{WEB_BASE}{path}",
                                  headers=web_headers(self.access_token),
                                  json=json, params=params)
        return parse_envelope(resp)

    @staticmethod
    def extract_verification_code(link_or_code: str) -> str:
        s = link_or_code.strip()
        if "/" not in s and "?" not in s:
            return s
        m = _LINK_CODE_RE.search(s.split("?", 1)[0])
        if not m:
            raise ValueError(f"could not extract verification code from: {link_or_code!r}")
        return m.group(1)

    # ------------------------------------------------------------------
    # 読み取り
    # ------------------------------------------------------------------
    def get_profile(self) -> Profile:
        return Profile(self._request("GET", WEB_PROFILE_PATH))

    def get_balance(self) -> Balance:
        return Balance(self._request("GET", WEB_BALANCE_PATH))

    def get_history(self, size: Optional[int] = None) -> AttrDict:
        params = {"pageSize": size} if size is not None else None
        return AttrDict(self._request("GET", WEB_HISTORY_PATH, params=params))

    def link_check(self, link_or_code: str) -> LinkInfo:
        code = self.extract_verification_code(link_or_code)
        payload = self._request("GET", WEB_LINK_INFO_PATH,
                                params={"verificationCode": code})
        info = LinkInfo(payload)
        info.setdefault("verificationCode", code)
        return info

    # ------------------------------------------------------------------
    # リンクの受け取り / 辞退
    # ------------------------------------------------------------------
    @staticmethod
    def _message_bits(info: Dict[str, Any]) -> Dict[str, Any]:
        message = info.get("message") or {}
        data = message.get("data") or {}
        return {
            "requestId": data.get("requestId"),
            "orderId": data.get("orderId") or (info.get("pendingP2PInfo") or {}).get("orderId"),
            "senderMessageId": message.get("messageId"),
            "senderChannelUrl": message.get("chatRoomId"),
        }

    def _guard_pending(self, info: LinkInfo) -> None:
        status = info.status
        if status and status != "PENDING":
            raise LinkAlreadyClaimed(f"すでに 受け取り / 辞退 / キャンセル 済み（{status}）")

    def link_receive(self, link_or_code: str, password: Optional[str] = None,
                     *, link_info: Optional[LinkInfo] = None) -> AttrDict:
        code = self.extract_verification_code(link_or_code)
        info = link_info if link_info is not None else self.link_check(code)
        self._guard_pending(info)
        if info.has_password and password is None:
            raise LinkPasscodeRequired("このリンクにはパスワードが設定されている")

        bits = self._message_bits(info)
        if not bits["orderId"]:
            raise APIError("orderId missing from link info", status=200,
                           code="E_NO_ORDER_ID", payload=dict(info))
        body = {
            "verificationCode": code,
            "client_uuid": self.client_uuid,
            "requestAt": jst_now(),
            "requestId": bits["requestId"] or str(uuid.uuid4()).upper(),
            "orderId": bits["orderId"],
            "senderMessageId": bits["senderMessageId"],
            "senderChannelUrl": bits["senderChannelUrl"],
            "iosMinimumVersion": MINIMUM_APP_VERSION,
            "androidMinimumVersion": MINIMUM_APP_VERSION,
        }
        if password is not None:
            body["passcode"] = str(password)
        return AttrDict(self._request("POST", WEB_LINK_ACCEPT_PATH, json=body))

    def link_reject(self, link_or_code: str,
                    *, link_info: Optional[LinkInfo] = None) -> AttrDict:
        code = self.extract_verification_code(link_or_code)
        info = link_info if link_info is not None else self.link_check(code)
        self._guard_pending(info)

        bits = self._message_bits(info)
        if not bits["orderId"]:
            raise APIError("orderId missing from link info", status=200,
                           code="E_NO_ORDER_ID", payload=dict(info))
        body = {
            "requestAt": jst_now(),
            "orderId": bits["orderId"],
            "verificationCode": code,
            "requestId": str(uuid.uuid4()).upper(),
            "senderMessageId": bits["senderMessageId"],
            "senderChannelUrl": bits["senderChannelUrl"],
            "iosMinimumVersion": MINIMUM_APP_VERSION,
            "androidMinimumVersion": MINIMUM_APP_VERSION,
            "client_uuid": self.client_uuid,
        }
        return AttrDict(self._request("POST", WEB_LINK_REJECT_PATH, json=body))

    # ------------------------------------------------------------------
    # コード生成
    # ------------------------------------------------------------------
    def create_p2pcode(self) -> P2PCode:
        """自分宛て入金 QR。Web 版は金額指定を受け付けない。"""
        return P2PCode(self._request("POST", WEB_P2PCODE_PATH, json={}))

    def create_paymentcode(self, method: str = "WALLET",
                           method_id: str = "106177237") -> AttrDict:
        """店頭支払い用のワンタイムコード。"""
        return AttrDict(self._request("POST", WEB_PAYMENT_CODE_PATH, json={
            "paymentMethodType": method,
            "paymentMethodId": method_id,
            "paymentCodeSessionId": str(uuid.uuid4()),
        }))

    # ------------------------------------------------------------------
    # Web 版には無いもの
    # ------------------------------------------------------------------
    def _unsupported(self, name: str):
        raise APIError(
            f"{name} は Web 版 API には無い。BFF 側のトークン"
            "（PayPay.login() のブラウザ方式）が要る。",
            status=404, code="E_WEB_UNSUPPORTED", payload={},
        )

    def create_link(self, *a, **kw):
        self._unsupported("create_link")

    def send_money(self, *a, **kw):
        self._unsupported("send_money")

    def link_cancel(self, *a, **kw):
        self._unsupported("link_cancel")

    def send_message(self, *a, **kw):
        self._unsupported("send_message")

    def search_p2puser(self, *a, **kw):
        self._unsupported("search_p2puser")


__all__ = ["WebLogin", "WebPayPay", "web_headers", "jst_now", "WEB_BASE",
           "WEB_TOKEN_PATH", "WEB_OTP_RESEND_PATH", "WEB_PROFILE_PATH",
           "WEB_BALANCE_PATH", "WEB_HISTORY_PATH", "WEB_LINK_INFO_PATH",
           "WEB_LINK_ACCEPT_PATH", "WEB_LINK_REJECT_PATH", "WEB_P2PCODE_PATH",
           "WEB_PAYMENT_CODE_PATH", "WEB_USER_AGENT", "MINIMUM_APP_VERSION"]
