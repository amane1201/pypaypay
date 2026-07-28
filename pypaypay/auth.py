from __future__ import annotations
from dataclasses import dataclass
import time
from typing import Optional


REGULAR_MODE_CLIENT_ID = "pay2-mobile-app-client"
SANDBOX_MODE_CLIENT_ID = "pay2-mobile-app-sandbox-client"


@dataclass
class Tokens:
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: float = 0.0
    token_type: str = "Bearer"

    @classmethod
    def from_response(cls, payload: dict, *, now: float | None = None) -> "Tokens":
        now = now if now is not None else time.time()
        expires_in = int(payload.get("expiresIn") or payload.get("expires_in") or 0)
        return cls(
            access_token=payload.get("accessToken") or payload["access_token"],
            refresh_token=payload.get("refreshToken") or payload.get("refresh_token"),
            expires_at=(now + expires_in) if expires_in else 0.0,
            token_type=payload.get("tokenType") or payload.get("token_type") or "Bearer",
        )

    @property
    def is_expired(self) -> bool:
        # 60s safety window
        return bool(self.expires_at) and time.time() >= self.expires_at - 60
