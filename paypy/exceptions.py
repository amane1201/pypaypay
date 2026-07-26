from __future__ import annotations
from typing import Any, Optional


class PayPayError(Exception):
    """Base class for all paypy errors."""


class AuthError(PayPayError):
    """Authentication / authorization failure."""


class TokenExpiredError(AuthError):
    """Access token expired or invalid; refresh required."""


class LinkPasscodeRequired(PayPayError):
    """Receiving a passcode-protected link without providing the code."""


class LinkAlreadyClaimed(PayPayError):
    """The link has already been accepted or rejected."""


class RateLimitedError(PayPayError):
    """Server responded with 429 or an equivalent BFF result code."""


class APIError(PayPayError):
    """Generic BFF error with the raw response payload attached."""

    def __init__(self, message: str, *, status: int, code: Optional[str] = None,
                 payload: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.payload = payload

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.status}/{self.code}] {self.args[0]}"
