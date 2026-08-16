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
from urllib.parse import parse_qs, urlparse

import httpx

from .exceptions import (
    APIError, AuthError, LinkAlreadyClaimed, LinkPasscodeRequired, RateLimitedError,
)
from .parsing import parse_envelope
from .raw import RawAPI
from .responses import AttrDict, Balance, BarcodeInfo, LinkInfo, P2PCode, Profile

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

# ---------------------------------------------------------------------------
# app API (www.paypay.ne.jp/app) — BFF プロキシ
# ---------------------------------------------------------------------------
# app4.paypay.ne.jp/bff/... と同じバックエンドに、www.paypay.ne.jp/app/... 経由で
# Cookie 認証のまま届く。BFF のパスを app 側に変換して RawAPI をそのまま流用する。
#   bff/vN/X  -> app/vN/bff/X
#   p2p/vN/X  -> app/vN/p2p-api/X
# ただし P2P のリンク/コード系は BFF では bff/v2 名義でも app 側では p2p-api に居る。
_WEB_PATH_OVERRIDE = {
    "bff/v2/getP2PLinkInfo": "app/v2/p2p-api/getP2PLinkInfo",
    "bff/v2/acceptP2PSendMoneyLink": "app/v2/p2p-api/acceptP2PSendMoneyLink",
    "bff/v2/rejectP2PSendMoneyLink": "app/v2/p2p-api/rejectP2PSendMoneyLink",
    "bff/v1/createP2PCode": "app/v1/p2p-api/createP2PCode",
    # 逆コンパイルの BFF は v1 だが、Web ウォレット実物は v4 を叩いている。
    # v1 は app プロキシだと C0002 になる。
    "bff/v1/getGVList": "app/v4/bff/getGVList",
}
_WEB_AREA = {"bff": "bff", "p2p": "p2p-api"}

# 実サーバで叩いて分かった「app 側では使えない」もの（送金・直接送金・チャット・
# チャンネル/フィード）。ネットに投げる前に理由付きで弾く。
_WEB_UNAVAILABLE = {
    # 送金リンクの発行 / 取消はネイティブ署名ヘッダを要求されて C0000 で止まる
    "bff/v2/executeP2PSendMoneyLink": "リンク発行（送金）は app API では封じられている",
    "bff/v1/cancelP2PSendMoney": "送金リンクの取消は app API では封じられている",
    # 直接送金・チャット・ユーザー検索・P2P ホームは app 側に存在しない（404）
    "p2p/v3/executeP2PSendMoney": "直接送金は app API に無い",
    "p2p/v1/sendP2PMessage": "チャット送信は app API に無い",
    "p2p/v3/searchP2PUser": "ユーザー検索は app API に無い",
    "p2p/v1/getP2PHomeContent": "P2P ホームは app API に無い",
    "p2p/v1/initialiseOneToOneAndLinkChatRoom": "チャットルーム作成は app API に無い",
    "p2p/v1/getChatRoomHasMessageFromUser": "チャット確認は app API に無い",
    # チャンネル / フィードは 403 で拒否される
    "bff/v1/followChannel": "チャンネル機能は app API では拒否される（403）",
    "bff/v1/unfollowChannel": "チャンネル機能は app API では拒否される（403）",
    "bff/v1/likeFeed": "フィード機能は app API では拒否される（403）",
    "bff/v1/unlikeFeed": "フィード機能は app API では拒否される（403）",
}

# app 側の全リクエストが送るクライアントヘッダ。Client-Version の 9.9.9 は
# Web ウォレット自身が使っているバージョン下限回避のセンチネル。
APP_CLIENT_TYPE = "PAYPAYWEB"
APP_CLIENT_OS_TYPE = "WEB"
APP_CLIENT_VERSION = "9.9.9"


def bff_path_to_app(path: str) -> str:
    """BFF スタイルのパスを app (www.paypay.ne.jp/app) 側のパスへ変換する。

    既に ``app/...`` や ``/app/...`` ならそのまま。未知の接頭辞は素通し。
    """
    p = path.strip("/")
    if p in _WEB_PATH_OVERRIDE:
        return _WEB_PATH_OVERRIDE[p]
    seg = p.split("/")
    if seg[0] == "app":
        return p
    if len(seg) >= 3 and seg[0] in _WEB_AREA and seg[1].startswith("v"):
        return f"app/{seg[1]}/{_WEB_AREA[seg[0]]}/" + "/".join(seg[2:])
    return "app/" + p

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
    """ログイン (oauth/token) 用の素のヘッダ。"""
    h = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": WEB_USER_AGENT,
        "Content-Type": "application/json",
    }
    if access_token:
        h["Cookie"] = f"token={access_token}"
    return h


def app_headers(
    access_token: Optional[str] = None,
    *,
    client_uuid: Optional[str] = None,
    device_uuid: Optional[str] = None,
) -> Dict[str, str]:
    """app API (www.paypay.ne.jp/app) 用ヘッダ。

    Web ウォレットが送っているクライアントヘッダを足したもの。読み取り系は
    素の :func:`web_headers` でも通るが、一部の書き込み系はこれらを要求する。
    """
    h = web_headers(access_token)
    h.update({
        "Client-Type": APP_CLIENT_TYPE,
        "Client-OS-Type": APP_CLIENT_OS_TYPE,
        "Client-Version": APP_CLIENT_VERSION,
        "System-Locale": "ja",
        "Timezone": "Asia/Tokyo",
        "Origin": WEB_BASE,
        "Referer": f"{WEB_BASE}/app/",
    })
    if client_uuid:
        h["Client-UUID"] = client_uuid
    if device_uuid:
        h["Device-UUID"] = device_uuid
    return h


def _parse_app(resp: httpx.Response) -> Dict[str, Any]:
    """app プロキシ応答の解析。未公開 (404/HTML) やゲート (C0000) を分かりやすく。"""
    if resp.status_code == 429:
        raise RateLimitedError("rate limited by PayPay app API")
    ctype = resp.headers.get("content-type", "")
    if "json" not in ctype:
        raise APIError("このエンドポイントは app API には無い（プロキシ未公開）",
                       status=resp.status_code, code="E_WEB_UNAVAILABLE", payload={})
    try:
        body = resp.json()
    except ValueError:
        raise APIError("app API が JSON を返さなかった",
                       status=resp.status_code, code="E_WEB_UNAVAILABLE", payload={}) from None
    code = (body.get("header") or {}).get("resultCode") if isinstance(body, dict) else None
    if code == "C0000":
        raise APIError("このエンドポイントは app API ではゲートされている"
                       "（ネイティブアプリの署名ヘッダが要る）",
                       status=resp.status_code, code="E_WEB_GATED", payload=body)
    return parse_envelope(resp)


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

        #: 1:1 wrapper for every BFF endpoint reachable through the app proxy.
        #: BFF-only 送金/チャット/チャンネル系は E_WEB_UNAVAILABLE / E_WEB_GATED で弾く。
        self.raw = RawAPI(self)

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
        """BFF スタイル（や app スタイル）のパスを app プロキシへ投げる。

        RawAPI もこれを直接呼ぶので、``bff/...`` / ``p2p/...`` を app 側へ
        変換し、Web で使えないものは通信前に弾く。
        """
        if not self.access_token:
            raise AuthError("先にログインして（access_token が無い）")
        key = path.strip("/")
        reason = _WEB_UNAVAILABLE.get(key)
        if reason:
            raise APIError(reason, status=404, code="E_WEB_UNAVAILABLE", payload={})
        app_path = bff_path_to_app(path)
        resp = self._http.request(
            method, f"{WEB_BASE}/{app_path}",
            headers=app_headers(self.access_token, client_uuid=self.client_uuid),
            json=json, params=params,
        )
        return _parse_app(resp)

    def app_call(self, method: str, endpoint: str, *, json: Any = None,
                 params: Optional[Dict[str, Any]] = None) -> AttrDict:
        """app API を名前で直接叩く逃げ道。

        ``endpoint`` は ``getBalanceInfo`` のような素の名前でも、
        ``bff/v1/getBalanceInfo`` や ``app/v1/bff/getBalanceInfo`` でも受ける。
        素の名前なら ``bff/v1/`` を補って解決する。
        """
        e = endpoint.strip("/")
        if "/" not in e:
            e = f"bff/v1/{e}"
        return AttrDict(self._request(method, e, json=json, params=params))

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
    # 支払い方法 / 残高チャージ元
    # ------------------------------------------------------------------
    def get_payment_methods(self) -> AttrDict:
        """登録済みの支払い方法一覧。"""
        return AttrDict(self._request("GET", "bff/v2/getPaymentMethodList"))

    # ------------------------------------------------------------------
    # 店舗 QR / バーコード決済
    # ------------------------------------------------------------------
    def get_barcode_info(self, url_or_code: str) -> BarcodeInfo:
        """店舗 QR / バーコードの情報を引く。"""
        code = url_or_code
        if code.startswith(("http://", "https://")):
            parsed = urlparse(code)
            qs = parse_qs(parsed.query)
            code = qs.get("code", [parsed.path.rstrip("/").split("/")[-1]])[0]
        return BarcodeInfo(self._request("GET", "bff/v2/getBarcodeInfo",
                                         params={"code": code}))

    def pay_qr_code(self, url_or_code: str,
                    *, amount: Optional[int] = None) -> AttrDict:
        """店舗 QR 決済を実行する（情報取得 → 事前承認決済）。"""
        info = self.get_barcode_info(url_or_code)
        order_id = info.get("orderId") or info.get("preAuthOrderId")
        pay_amount = amount if amount is not None else info.amount
        if not order_id:
            raise APIError("QR did not yield an orderId", status=200,
                           code="E_NO_ORDER", payload=dict(info))
        body: Dict[str, Any] = {"requestId": str(uuid.uuid4()),
                                "orderId": order_id, "currency": "JPY"}
        if pay_amount is not None:
            body["amount"] = int(pay_amount)
        merchant = info.get("merchantId")
        if merchant:
            body["merchantId"] = merchant
        return AttrDict(self._request("POST", "bff/v2/executePreAuthPayment", json=body))

    # ------------------------------------------------------------------
    # 出金（PayPay 銀行へ）
    # ------------------------------------------------------------------
    def get_payout_info(self) -> AttrDict:
        """出金先の一覧。"""
        return AttrDict(self._request("GET", "bff/v2/getPayoutDisplayInfo"))

    def cashout_to_paypaybank(self, amount: int,
                              *, payout_method_id: Optional[str] = None) -> AttrDict:
        """残高を PayPay 銀行へ出金する。``PayPay`` と同じ手順。"""
        if not payout_method_id:
            info = self.get_payout_info()
            methods = info.get("payoutMethods") or []
            for m in methods:
                name = (m.get("bankName") or m.get("name") or "").lower()
                if "paypay" in name or m.get("isDefault"):
                    payout_method_id = m.get("payoutMethodId") or m.get("id")
                    break
            if not payout_method_id and methods:
                payout_method_id = methods[0].get("payoutMethodId") or methods[0].get("id")
            if not payout_method_id:
                raise APIError("no payout methods available", status=200,
                               code="E_NO_PAYOUT", payload=dict(info))
        return AttrDict(self._request("POST", "bff/v1/saveBankStandingInstruction", json={
            "requestId": str(uuid.uuid4()),
            "payoutMethodId": payout_method_id,
            "amount": int(amount),
        }))

    # ------------------------------------------------------------------
    # app API で使えないもの（実サーバで確認済み）
    # ------------------------------------------------------------------
    def _unsupported(self, name: str, why: str):
        raise APIError(
            f"{name} は app API では使えない（{why}）。BFF 側のトークン"
            "（PayPay.login() のブラウザ方式）が要る。",
            status=404, code="E_WEB_UNSUPPORTED", payload={},
        )

    def create_link(self, *a, **kw):
        # executeP2PSendMoneyLink は app プロキシがネイティブ署名ヘッダを要求（C0000）
        self._unsupported("create_link", "送金リンク発行はゲートされている")

    def send_money(self, *a, **kw):
        self._unsupported("send_money", "直接送金は app API に無い")

    def link_cancel(self, *a, **kw):
        self._unsupported("link_cancel", "送金リンク取消はゲートされている")

    def send_message(self, *a, **kw):
        self._unsupported("send_message", "チャットは app API に無い")

    def search_p2puser(self, *a, **kw):
        self._unsupported("search_p2puser", "ユーザー検索は app API に無い")


__all__ = ["WebLogin", "WebPayPay", "web_headers", "app_headers", "jst_now",
           "bff_path_to_app", "WEB_BASE",
           "WEB_TOKEN_PATH", "WEB_OTP_RESEND_PATH", "WEB_PROFILE_PATH",
           "WEB_BALANCE_PATH", "WEB_HISTORY_PATH", "WEB_LINK_INFO_PATH",
           "WEB_LINK_ACCEPT_PATH", "WEB_LINK_REJECT_PATH", "WEB_P2PCODE_PATH",
           "WEB_PAYMENT_CODE_PATH", "WEB_USER_AGENT", "MINIMUM_APP_VERSION"]
