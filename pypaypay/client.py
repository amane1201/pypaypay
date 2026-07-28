from __future__ import annotations
import base64
import hashlib
import os
import re
import secrets
from typing import Any, Dict, List, Optional, Union
from urllib.parse import parse_qs, urlparse

import httpx

from .auth import Tokens, REGULAR_MODE_CLIENT_ID, SANDBOX_MODE_CLIENT_ID
from .exceptions import APIError, AuthError
from .headers import build_headers, new_uuid, DEFAULT_APP_VERSION, DEFAULT_OS_VERSION
from .parsing import parse_envelope
from .raw import RawAPI
from .responses import (
    AttrDict, Balance, BarcodeInfo, Chatroom, CreateLink, LinkInfo,
    P2PCode, Profile, SearchUser, SendMoney,
)
from .web import WebLogin


PROD_BASE_URL = "https://app4.paypay.ne.jp"
SANDBOX_BASE_URL = "https://stg-app4.paypay-corp.co.jp"
LOGIN_PORTAL_BASE = "https://www.paypay.ne.jp/portal/oauth2/l"
LOGIN_REDIRECT_URI = "paypay://oauth2/callback"

# Verification code inside a paypay.me / p2p link URL
_LINK_CODE_RE = re.compile(r"([A-Za-z0-9_-]{10,})/?$")
# TK request id inside https://www.paypay.ne.jp/portal/oauth2/l?id=TKxxxx
_TK_ID_RE = re.compile(r"(TK[A-Za-z0-9_-]+)")
# Sendbird channel id fragment
_SENDBIRD_CHANNEL_RE = re.compile(r"(sendbird_group_channel_[A-Za-z0-9_-]+)")

FORM_URLENCODED = "application/x-www-form-urlencoded"
# The OAuth2 endpoints reject `application/json` with
# 400 C0001 "Malformed header value. [Content-Type : ...]"; they only accept
# form-urlencoded bodies (verified against app4.paypay.ne.jp, 2026-07).
FORM_PATHS = frozenset({
    "bff/v2/oauth2/par",
    "bff/v2/oauth2/token",
    "bff/v2/oauth2/refresh",
})


def _needs_form(path: str) -> bool:
    """True for the endpoints verified to need form encoding — exact match, so
    e.g. ``bff/v2/oauth2/token/exchange`` keeps sending JSON."""
    return path.lstrip("/").rstrip("/") in FORM_PATHS


def _form_body(body: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Flatten a JSON-ish body to form fields (None dropped, bools lowercased)."""
    out: Dict[str, str] = {}
    for k, v in (body or {}).items():
        if v is None:
            continue
        out[k] = "true" if v is True else "false" if v is False else str(v)
    return out


def _pkce_pair() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) for OAuth2 PKCE (S256)."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _normalize_phone(phone: str) -> str:
    """'080-1234-5678' -> '08012345678'; leaves E.164 forms alone."""
    return re.sub(r"[\s-]", "", phone)


class PayPay:
    """Unofficial PayPay client — PayPayOpenPy-compatible surface.

    Construction accepts multiple call shapes:

    * ``PayPay("08012345678", "password")`` — new-device login. Call ``login()``
      then ``login_confirm(url)``.
    * ``PayPay("08012345678", "password", "device-uuid")`` — same, but reusing
      an already-registered device (``login()`` may complete without OTP).
    * ``PayPay(access_token="...")`` — skip login entirely. Pair with
      ``refresh_token=...`` to enable auto refresh.

    Once authenticated, ``pp.access_token`` / ``pp.refresh_token`` /
    ``pp.device_uuid`` / ``pp.client_uuid`` are readable attributes.
    """

    def __init__(
        self,
        phone: Optional[str] = None,
        password: Optional[str] = None,
        device_uuid: Optional[str] = None,
        *,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_uuid: Optional[str] = None,
        sandbox: bool = False,
        base_url: Optional[str] = None,
        timeout: float = 20.0,
        proxy: Optional[Union[str, Dict[str, str]]] = None,
    ) -> None:
        self.phone = _normalize_phone(phone) if phone else None
        self.password = password
        self.tokens = Tokens(access_token=access_token or "", refresh_token=refresh_token)
        self.client_uuid = client_uuid or new_uuid()
        self.device_uuid = device_uuid or self.client_uuid
        self.sandbox = sandbox
        self.oauth_client_id = SANDBOX_MODE_CLIENT_ID if sandbox else REGULAR_MODE_CLIENT_ID
        self.base_url = (base_url or (SANDBOX_BASE_URL if sandbox else PROD_BASE_URL)).rstrip("/")

        proxies = self._normalize_proxy(proxy)
        self._http = httpx.Client(timeout=timeout, proxy=proxies, http2=False)

        self._pkce_verifier: Optional[str] = None
        self._pkce_challenge: Optional[str] = None
        self._auth_state: Optional[str] = None
        self._request_uri: Optional[str] = None  # from oauth2/par
        self._request_uri_expires_in: Optional[int] = None
        self._web_login: Optional[WebLogin] = None
        #: True なら Web 版 API 由来のトークン（otp_login 経由）
        self.web_token = False

        #: 1:1 wrapper for every discovered BFF endpoint.
        self.raw = RawAPI(self)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------
    @property
    def access_token(self) -> str:
        return self.tokens.access_token

    @property
    def refresh_token(self) -> Optional[str]:
        return self.tokens.refresh_token

    def __enter__(self) -> "PayPay":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ------------------------------------------------------------------
    # HTTP core
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_proxy(proxy: Optional[Union[str, Dict[str, str]]]):
        if proxy is None:
            return None
        if isinstance(proxy, dict):
            # httpx <=0.28 supports `proxies={...}`; for a plain str-per-scheme
            # dict, just pick the http entry.
            return proxy.get("all") or proxy.get("http") or proxy.get("https")
        s = proxy
        # Scheme may contain digits ("socks5://"), so don't use [a-z]+ here.
        if s and not re.match(r"^[a-z][a-z0-9+.-]*://", s, re.I):
            s = "http://" + s
        return s

    def _headers(self, *, with_auth: bool = True) -> Dict[str, str]:
        return build_headers(
            client_uuid=self.client_uuid,
            device_uuid=self.device_uuid,
            access_token=self.tokens.access_token if with_auth else None,
            sandbox=self.sandbox,
        )

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        _retry_on_401: bool = True,
        _with_auth: bool = True,
    ) -> Dict[str, Any]:
        headers = self._headers(with_auth=_with_auth)
        if _needs_form(path):
            headers["Content-Type"] = FORM_URLENCODED
            kwargs: Dict[str, Any] = {"data": _form_body(json)}
        else:
            kwargs = {"json": json}

        resp = self._http.request(
            method,
            self._url(path),
            headers=headers,
            params=params,
            **kwargs,
        )
        if resp.status_code == 401 and _retry_on_401 and self.tokens.refresh_token:
            self.token_refresh(self.tokens.refresh_token)
            return self._request(method, path, json=json, params=params,
                                 _retry_on_401=False, _with_auth=_with_auth)
        return self._parse(resp)

    _parse = staticmethod(parse_envelope)

    # ------------------------------------------------------------------
    # OAuth2 / login flow
    # ------------------------------------------------------------------
    def login(self) -> str:
        """Kick off OAuth2 authorization.

        Returns the URL the user should open to complete phone + password + OTP
        verification. After completing it in a browser they get redirected to
        ``paypay://oauth2/callback?code=...`` — pass that URL (or bare id) to
        :meth:`login_confirm`.

        The URL expires quickly (``expiresIn`` on the PAR response is ~60s),
        so open it right away. Requires ``phone`` in the constructor.
        """
        if not self.phone:
            raise AuthError("phone number required to start login()")

        self._pkce_verifier, self._pkce_challenge = _pkce_pair()
        self._auth_state = secrets.token_urlsafe(24)

        body = {
            "clientId": self.oauth_client_id,
            "clientAppVersion": DEFAULT_APP_VERSION,
            "clientOsVersion": DEFAULT_OS_VERSION,
            "clientOsType": "ANDROID",
            "redirectUri": LOGIN_REDIRECT_URI,
            "responseType": "code",
            "state": self._auth_state,
            "codeChallenge": self._pkce_challenge,
            "codeChallengeMethod": "S256",
            "scope": "REGULAR",
            "tokenVersion": "v2",
            "prompt": "login",
            "uiLocales": "ja",
        }
        payload = self._request("POST", "bff/v2/oauth2/par", json=body,
                                _with_auth=False, _retry_on_401=False)
        request_uri = payload.get("requestUri") or payload.get("request_uri") or ""
        self._request_uri = request_uri
        self._request_uri_expires_in = payload.get("expiresIn")

        # Current builds return the RFC 9126 URN form:
        #   urn:ietf:params:oauth:request_uri:<32 chars>
        # Older ones embedded a TKxxxx id, or exposed it as `id`/`requestId`.
        auth_id = payload.get("id") or payload.get("requestId")
        if not auth_id:
            m = _TK_ID_RE.search(request_uri)
            if m:
                auth_id = m.group(1)
            elif ":" in request_uri:
                auth_id = request_uri.rsplit(":", 1)[-1]
        if not auth_id:
            raise AuthError(f"oauth2/par response has no usable id: {payload!r}")

        return f"{LOGIN_PORTAL_BASE}?id={auth_id}"

    # ------------------------------------------------------------------
    # OTP ログイン（Web 版 API）
    # ------------------------------------------------------------------
    def otp_login(self) -> Dict[str, Any]:
        """メアド/電話番号＋パスワードでログインを開始し、OTP を送らせる。

        ブラウザを開かない方の入口。返り値の ``otp_required`` が True なら
        OTP が届いているので :meth:`otp_confirm` に渡す。False なら
        ``access_token`` がもう取れていて、こっちで反映済み。

        使うのは Web 版 API (www.paypay.ne.jp/app) で、BFF の PAR フロー
        （:meth:`login`）とは別系統。
        """
        if not self.phone:
            raise AuthError("phone/mail required to start otp_login()")
        if not self.password:
            raise AuthError("password required to start otp_login()")

        self._web_login = WebLogin(self.phone, self.password,
                                   client_uuid=self.client_uuid, http=self._http)
        payload = self._web_login.start()
        if not payload.get("otp_required"):
            self._apply_web_tokens()
        return payload

    def otp_confirm(self, otp: str) -> Tokens:
        """届いた OTP を入れてトークンを確定する。"""
        if not self._web_login:
            raise AuthError("call otp_login() before otp_confirm()")
        self._web_login.verify(otp)
        return self._apply_web_tokens()

    def otp_resend(self) -> Dict[str, Any]:
        """OTP が来なかったときに送り直す。"""
        if not self._web_login:
            raise AuthError("call otp_login() before otp_resend()")
        return self._web_login.resend()

    def _apply_web_tokens(self) -> Tokens:
        web = self._web_login
        self.tokens = Tokens(access_token=web.access_token or "",
                             refresh_token=web.refresh_token)
        self.web_token = True
        return self.tokens

    def login_confirm(self, url_or_code: str) -> Tokens:
        """Exchange the browser-obtained authorization code (or TK id URL)
        for access/refresh tokens.
        """
        if not self._pkce_verifier:
            raise AuthError("call login() before login_confirm()")

        code = self._extract_auth_code(url_or_code)
        body = {
            "clientId": self.oauth_client_id,
            "redirectUri": LOGIN_REDIRECT_URI,
            "code": code,
            "codeVerifier": self._pkce_verifier,
        }
        payload = self._request("POST", "bff/v2/oauth2/token", json=body,
                                _with_auth=False, _retry_on_401=False)
        self.tokens = Tokens.from_response(payload)
        # Server may return a device_uuid; keep whatever we passed otherwise.
        server_device = payload.get("deviceUUID") or payload.get("deviceUuid")
        if server_device:
            self.device_uuid = server_device
        return self.tokens

    def token_refresh(self, refresh_token: Optional[str] = None) -> Tokens:
        """Refresh access/refresh tokens using ``bff/v2/oauth2/refresh``.

        If ``refresh_token`` is not passed, uses whatever is on the client.
        """
        rt = refresh_token or self.tokens.refresh_token
        if not rt:
            raise AuthError("no refresh_token available")
        self.tokens.refresh_token = rt

        # Goes through _request so the form-urlencoded rule for oauth2 paths
        # applies here too.
        payload = self._request(
            "POST", "bff/v2/oauth2/refresh",
            json={"clientId": self.oauth_client_id, "refreshToken": rt},
            _with_auth=False, _retry_on_401=False,
        )
        self.tokens = Tokens.from_response(payload)
        return self.tokens

    # Backwards-compatible alias
    def refresh_access_token(self) -> Tokens:
        return self.token_refresh()

    @staticmethod
    def _extract_auth_code(url_or_code: str) -> str:
        """Accept a full callback URL, a portal URL, a TK id, or a bare code."""
        s = url_or_code.strip()
        if s.startswith(("http://", "https://", "paypay://")):
            parsed = urlparse(s)
            qs = parse_qs(parsed.query)
            for k in ("code", "authorization_code", "id"):
                if k in qs:
                    return qs[k][0]
            # Path-based TK id
            m = _TK_ID_RE.search(s)
            if m:
                return m.group(1)
        # Bare id / code
        return s

    # ------------------------------------------------------------------
    # Profile / balance
    # ------------------------------------------------------------------
    def get_profile(self) -> Profile:
        payload = self._request("GET", "bff/v1/getUserProfile",
                                params={"includeBeginnerFlag": "true"})
        # Some builds return {'userProfile': {...}}, some flat.
        return Profile(payload)

    def get_balance(self) -> Balance:
        payload = self._request("GET", "bff/v1/getBalanceInfo")
        return Balance(payload)

    # ------------------------------------------------------------------
    # History / chat / notifications
    # ------------------------------------------------------------------
    def get_history(self, size: int = 20, last_sequence: Optional[Any] = None) -> AttrDict:
        params: Dict[str, Any] = {"pageSize": size}
        if last_sequence is not None:
            params["lastSequence"] = last_sequence
        payload = self._request("GET", "bff/v2/getPay2BalanceHistory", params=params)
        return AttrDict(payload)

    def get_point_history(self, size: int = 20,
                          last_sequence: Optional[Any] = None) -> AttrDict:
        params: Dict[str, Any] = {"pageSize": size}
        if last_sequence is not None:
            params["lastSequence"] = last_sequence
        # No dedicated point-history endpoint in the BFF; Yahoo point token
        # is exchanged and the caller is expected to query the point service.
        payload = self._request("GET", "bff/v1/getPay2BalanceCancelledPendingCashBackHistory",
                                params=params)
        return AttrDict(payload)

    def get_chat_rooms(self, size: int = 20) -> AttrDict:
        """P2P home (chat rooms + friend suggestions + banners)."""
        payload = self._request("GET", "p2p/v1/getP2PHomeContent",
                                params={"pageSize": size})
        return AttrDict(payload)

    def get_chat_room_messages(self, chat_room_id: str, size: int = 20) -> AttrDict:
        """Return recent messages for a Sendbird chat room.

        Delegates to ``p2p/v1/getChatRoomHasMessageFromUser`` (BFF-side check)
        plus the Sendbird channel URL. The heavy lifting (actually fetching
        messages) happens against Sendbird's own API; here we surface what the
        BFF exposes.
        """
        # normalise: caller can pass 'sendbird_group_channel_xxx' or just 'xxx'
        m = _SENDBIRD_CHANNEL_RE.search(chat_room_id)
        channel_url = m.group(1) if m else f"sendbird_group_channel_{chat_room_id}"
        payload = self._request(
            "POST", "p2p/v1/getChatRoomHasMessageFromUser",
            json={"channelUrl": channel_url, "pageSize": size},
        )
        payload = dict(payload)
        payload.setdefault("channelUrl", channel_url)
        return AttrDict(payload)

    # ------------------------------------------------------------------
    # P2P — send / receive by link
    # ------------------------------------------------------------------
    @staticmethod
    def extract_verification_code(link_or_code: str) -> str:
        """Normalise a paypay.me / p2p link URL down to its verification code."""
        s = link_or_code.strip()
        if "/" not in s and "?" not in s:
            return s
        m = _LINK_CODE_RE.search(s.split("?", 1)[0])
        if not m:
            raise ValueError(f"could not extract verification code from: {link_or_code!r}")
        return m.group(1)

    def link_check(self, link_or_code: str, web: bool = False) -> LinkInfo:
        """Look up a P2P send-money link by URL or bare verification code.

        ``web=True`` uses the public web resolver (``p2p/v1/resolveLink``)
        which returns slightly less data but works without a valid access
        token in some paths; default is the app BFF endpoint.
        """
        code = self.extract_verification_code(link_or_code)
        if web:
            payload = self._request("GET", "p2p/v1/resolveLink",
                                    params={"verificationCode": code})
        else:
            # POST here returns 400 C0002 "Invalid request method".
            payload = self._request("GET", "bff/v2/getP2PLinkInfo",
                                    params={"verificationCode": code})
        result = LinkInfo(payload)
        result.setdefault("verificationCode", code)
        return result

    def link_receive(
        self,
        link_or_code: str,
        password: Optional[str] = None,
        *,
        link_info: Optional[LinkInfo] = None,
        request_id: Optional[str] = None,
    ) -> AttrDict:
        code = self.extract_verification_code(link_or_code)
        info = link_info if link_info is not None else self.link_check(code)
        order_id = info.order_id if isinstance(info, LinkInfo) else info.get("orderId")
        if not order_id:
            raise APIError("orderId missing from link info", status=200,
                           code="E_NO_ORDER_ID", payload=dict(info))
        body: Dict[str, Any] = {
            "requestId": request_id or new_uuid(),
            "orderId": order_id,
            "verificationCode": code,
        }
        if password is not None:
            body["passcode"] = str(password)
        return AttrDict(self._request("POST", "bff/v2/acceptP2PSendMoneyLink", json=body))

    def link_reject(
        self,
        link_or_code: str,
        *,
        link_info: Optional[LinkInfo] = None,
        request_id: Optional[str] = None,
    ) -> AttrDict:
        code = self.extract_verification_code(link_or_code)
        info = link_info if link_info is not None else self.link_check(code)
        order_id = info.order_id if isinstance(info, LinkInfo) else info.get("orderId")
        if not order_id:
            raise APIError("orderId missing from link info", status=200,
                           code="E_NO_ORDER_ID", payload=dict(info))
        body = {
            "requestId": request_id or new_uuid(),
            "orderId": order_id,
            "verificationCode": code,
        }
        return AttrDict(self._request("POST", "bff/v2/rejectP2PSendMoneyLink", json=body))

    def link_cancel(
        self,
        link_or_code: str,
        *,
        link_info: Optional[LinkInfo] = None,
        request_id: Optional[str] = None,
    ) -> AttrDict:
        code = self.extract_verification_code(link_or_code)
        info = link_info if link_info is not None else self.link_check(code)
        order_id = info.order_id if isinstance(info, LinkInfo) else info.get("orderId")
        channel_url = info.chat_room_id if isinstance(info, LinkInfo) else info.get("chatRoomId")
        if not order_id:
            raise APIError("orderId missing from link info", status=200,
                           code="E_NO_ORDER_ID", payload=dict(info))
        body: Dict[str, Any] = {
            "requestId": request_id or new_uuid(),
            "orderId": order_id,
        }
        if channel_url:
            body["channelUrl"] = channel_url
        return AttrDict(self._request("POST", "bff/v1/cancelP2PSendMoney", json=body))

    def create_link(
        self,
        amount: int,
        passcode: Optional[str] = None,
        *,
        theme: Optional[str] = None,
        user_comment: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> CreateLink:
        body: Dict[str, Any] = {
            "requestId": request_id or new_uuid(),
            "amount": int(amount),
            "socketConnection": None,
        }
        if passcode is not None:
            body["passcode"] = str(passcode)
        if theme is not None:
            body["theme"] = theme
        if user_comment is not None:
            body["userComment"] = user_comment
        payload = self._request("POST", "bff/v2/executeP2PSendMoneyLink", json=body)
        return CreateLink(payload)

    # Backwards-compat name
    def send_money_link(self, amount: int, **kw) -> CreateLink:
        return self.create_link(amount, **kw)

    def cancel_sent_link(self, order_id: str) -> AttrDict:
        return AttrDict(self._request(
            "POST", "bff/v1/cancelP2PSendMoney",
            json={"orderId": order_id, "requestId": new_uuid()},
        ))

    # ------------------------------------------------------------------
    # P2P — direct send / QR / friends
    # ------------------------------------------------------------------
    def create_p2pcode(self, amount: Optional[int] = None) -> P2PCode:
        body: Dict[str, Any] = {"sessionId": new_uuid()}
        if amount is not None:
            body["amount"] = int(amount)
        payload = self._request("POST", "bff/v1/createP2PCode", json=body)
        return P2PCode(payload)

    def send_money(
        self,
        amount: int,
        receiver_id: str,
        *,
        user_comment: Optional[str] = None,
        theme: Optional[str] = None,
        request_id: Optional[str] = None,
        unblock_receiver: bool = False,
    ) -> SendMoney:
        """Direct P2P send to a user (by ``externalUserId``).

        Uses ``p2p/v3/executeP2PSendMoney``.
        """
        body: Dict[str, Any] = {
            "amount": int(amount),
            "externalReceiverId": receiver_id,
            "requestId": request_id or new_uuid(),
        }
        if user_comment is not None:
            body["userComment"] = user_comment
        if theme is not None:
            body["theme"] = theme
        if unblock_receiver:
            body["unblockReceiver"] = True
        payload = self._request("POST", "p2p/v3/executeP2PSendMoney", json=body)
        return SendMoney(payload)

    def send_message(self, chat_room_id: str, message: str) -> AttrDict:
        """Send a text message into a P2P chat room."""
        m = _SENDBIRD_CHANNEL_RE.search(chat_room_id)
        channel_url = m.group(1) if m else f"sendbird_group_channel_{chat_room_id}"
        body = {"channelUrl": channel_url, "message": message}
        return AttrDict(self._request("POST", "p2p/v1/sendP2PMessage", json=body))

    def set_money_priority(self, paypay_money: bool = False) -> AttrDict:
        """Prefer PayPay マネー (``paypay_money=True``) or マネーライト (False)
        when sending money.
        """
        body = {"paymentMethodType": "MONEY" if paypay_money else "MONEY_LIGHT"}
        return AttrDict(self._request("POST", "bff/v1/setPrioritizedPaymentMethod", json=body))

    def search_p2puser(
        self,
        user_id: str,
        is_global: bool = True,
        order: int = 0,
    ) -> SearchUser:
        """Search for a P2P user by PayPay ID (global) or display name (friends).

        Returns the ``order``-th matching user as a :class:`SearchUser`.
        """
        body: Dict[str, Any] = {
            "searchTerm": user_id,
            "searchType": "GLOBAL" if is_global else "FRIENDS",
        }
        payload = self._request("POST", "p2p/v3/searchP2PUser", json=body)
        users: List[Dict[str, Any]] = (
            payload.get("users")
            or payload.get("results")
            or payload.get("userProfiles")
            or []
        )
        if not users:
            raise APIError("no user matched", status=200, code="E_NO_MATCH", payload=payload)
        try:
            hit = users[order]
        except IndexError as e:
            raise APIError(f"only {len(users)} results, order={order} out of range",
                           status=200, code="E_ORDER_OOR", payload=payload) from e
        return SearchUser(hit)

    def initialize_chatroom(self, external_user_id: str) -> Chatroom:
        """Get (or create) a 1:1 chat room with the given external user id."""
        payload = self._request(
            "POST", "p2p/v1/initialiseOneToOneAndLinkChatRoom",
            json={"externalUserId": external_user_id},
        )
        return Chatroom(payload)

    # ------------------------------------------------------------------
    # Merchant QR / barcode / cashout
    # ------------------------------------------------------------------
    def get_barcode_info(self, url_or_code: str) -> BarcodeInfo:
        """Fetch info about a PayPay merchant QR / barcode by URL or raw code."""
        code = url_or_code
        if code.startswith(("http://", "https://")):
            parsed = urlparse(code)
            qs = parse_qs(parsed.query)
            code = qs.get("code", [parsed.path.rstrip("/").split("/")[-1]])[0]
        params = {"code": code}
        payload = self._request("GET", "bff/v2/getBarcodeInfo", params=params)
        return BarcodeInfo(payload)

    def pay_qr_code(self, url_or_code: str,
                    *, amount: Optional[int] = None) -> AttrDict:
        """Complete a merchant QR payment.

        Two-step: fetch barcode info then execute the pre-auth payment. If the
        QR carries a fixed amount, ``amount`` may be omitted.
        """
        info = self.get_barcode_info(url_or_code)
        order_id = info.get("orderId") or info.get("preAuthOrderId")
        pay_amount = amount if amount is not None else info.amount
        if not order_id:
            raise APIError("QR did not yield an orderId", status=200,
                           code="E_NO_ORDER", payload=dict(info))
        body: Dict[str, Any] = {
            "requestId": new_uuid(),
            "orderId": order_id,
            "currency": "JPY",
        }
        if pay_amount is not None:
            body["amount"] = int(pay_amount)
        merchant = info.get("merchantId")
        if merchant:
            body["merchantId"] = merchant
        return AttrDict(self._request("POST", "bff/v2/executePreAuthPayment", json=body))

    def cashout_to_paypaybank(self, amount: int,
                              *, payout_method_id: Optional[str] = None) -> AttrDict:
        """Cash out balance to a linked PayPay 銀行 (Japan Net Bank) account.

        Uses ``bff/v1/saveBankStandingInstruction`` after resolving the
        default payout method via ``bff/v2/getPayoutDisplayInfo`` when
        ``payout_method_id`` isn't supplied.
        """
        if not payout_method_id:
            info = self._request("GET", "bff/v2/getPayoutDisplayInfo")
            methods = info.get("payoutMethods") or []
            for m in methods:
                # Prefer a PayPay bank match; fall back to whatever is default.
                name = (m.get("bankName") or m.get("name") or "").lower()
                if "paypay" in name or m.get("isDefault"):
                    payout_method_id = m.get("payoutMethodId") or m.get("id")
                    break
            if not payout_method_id and methods:
                payout_method_id = methods[0].get("payoutMethodId") or methods[0].get("id")
            if not payout_method_id:
                raise APIError("no payout methods available", status=200,
                               code="E_NO_PAYOUT", payload=info)
        body = {
            "requestId": new_uuid(),
            "payoutMethodId": payout_method_id,
            "amount": int(amount),
        }
        return AttrDict(self._request("POST", "bff/v1/saveBankStandingInstruction", json=body))
