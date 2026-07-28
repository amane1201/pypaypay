"""BFF / Web 版で共通の ``{"header": {...}, "payload": {...}}`` 解析。

どちらの API も同じ封筒でレスポンスを返すので、エラー判定はここに集約する。
"""
from __future__ import annotations

from typing import Any, Dict

import httpx

from .exceptions import (
    APIError,
    LinkAlreadyClaimed,
    LinkPasscodeRequired,
    RateLimitedError,
    TokenExpiredError,
)


def parse_envelope(resp: httpx.Response) -> Dict[str, Any]:
    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text}

    status = resp.status_code
    if status == 429:
        raise RateLimitedError("rate limited by PayPay")

    header = body.get("header") if isinstance(body, dict) else None
    result_code = (header or {}).get("resultCode") if isinstance(header, dict) else None
    result_msg = (header or {}).get("resultMessage") if isinstance(header, dict) else None
    lower_msg = (result_msg or "").lower()

    if status == 401:
        raise TokenExpiredError(result_msg or "access token rejected (401)")

    if status >= 400 or (result_code and result_code != "S0000"):
        code = result_code or str(status)
        msg = result_msg or f"HTTP {status}"
        if code in ("S0001", "S9001") or ("token" in lower_msg and "expire" in lower_msg):
            raise TokenExpiredError(msg)
        if "passcode" in lower_msg or code in ("S5001",):
            raise LinkPasscodeRequired(msg)
        if "already" in lower_msg or code in ("S5002", "S5003"):
            raise LinkAlreadyClaimed(msg)
        raise APIError(msg, status=status, code=code, payload=body)

    if not isinstance(body, dict):
        return {"payload": body}
    if "payload" in body:
        payload = body["payload"]
        return payload if isinstance(payload, dict) else {"payload": payload}
    # No payload envelope (or a non-JSON body): hand back what we got
    # rather than dropping it, minus the status header.
    return {k: v for k, v in body.items() if k != "header"}


__all__ = ["parse_envelope"]
