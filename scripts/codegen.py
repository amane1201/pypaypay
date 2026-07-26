"""Generate paypy/raw.py from endpoints.json.

Each endpoint becomes a method on RawAPI. The method name is a snake_case
transform of the last URL segment. Parameters detected from the decompiled
source are surfaced as explicit keyword-only args (all default to None);
callers may also pass **extra to add fields the extractor didn't catch.

GET endpoints send captured params as query string. POST endpoints send them
as JSON body. When the extractor caught both, POST endpoints put "body" as
JSON and "query" as query params.
"""
import json
import re
from pathlib import Path

SPEC = Path(__file__).parent / "endpoints.json"
OUT = (Path(__file__).parent / "../paypy/raw.py").resolve()

# Manually add endpoints that live outside BFFImpl.
EXTRA = {
    # oauth2/refresh — io1/C14933n.java
    "bff/v2/oauth2/refresh": {
        "method": "POST",
        "body": ["clientId", "refreshToken"],
        "query": [],
        "dto": None,
    },
    # genai-bff (P2P chat AI helpers) — sn1/*.java
    "genai-bff/api/v1/chatroom/getChatroom": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/chatroom/getHistoryMessages": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/consent/user": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/feedback": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/sse/getStreamId": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/p2p/getImage": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/p2p/getImages": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/p2p/health": {
        "method": "GET", "body": [], "query": [], "dto": None,
    },
    "genai-bff/api/v1/sse/p2p/getStreamId": {
        "method": "POST", "body": [], "query": [], "dto": None,
    },
}


_ACRONYMS = [
    ("P2P", "P2p"),
    ("PayPay", "Paypay"),
    ("PayPal", "Paypal"),
    ("GVList", "GvList"),
    ("KYC", "Kyc"),
    ("URL", "Url"),
    ("ATM", "Atm"),
    ("SMS", "Sms"),
    ("OTP", "Otp"),
    ("OTT", "Ott"),
    ("NRI", "Nri"),
    ("BMS", "Bms"),
    ("3d", "Threed"),
]


def camel_to_snake(name: str) -> str:
    for old, new in _ACRONYMS:
        name = name.replace(old, new)
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return re.sub(r"__+", "_", s)


def endpoint_to_method(path: str) -> str:
    # "bff/v1/acceptP2PSendMoney" -> "accept_p2p_send_money"
    # "bff/v2/oauth2/token/exchange" -> "oauth2_token_exchange"
    # "p2p/v3/searchP2PUser" -> "search_p2p_user"
    # "p2p/v1/getP2PGroupChatRoom" -> "get_p2p_group_chat_room"
    # "kyc/v1/app/nri/auth" -> "kyc_app_nri_auth"
    # "genai-bff/api/v1/p2p/health" -> "genai_p2p_health"
    tail = re.sub(r"^(bff|p2p)/v[0-9]/", "", path)
    tail = tail.replace("kyc/v1/", "kyc_")
    tail = tail.replace("genai-bff/api/v1/", "genai/")
    tail = tail.replace("-", "_").replace("/", "_")
    return camel_to_snake(tail)


def render(spec: dict) -> str:
    lines = [
        '"""Auto-generated raw API surface for paypy.\n\n'
        "Every method is a thin wrapper around a single PayPay BFF endpoint.\n"
        "Parameter names come from the decompiled Android app; pass None to omit.\n"
        "Additional fields can be supplied via ``**extra``.\n\n"
        "DO NOT EDIT — regenerate with scripts/codegen if the app is updated.\n"
        '"""',
        "from __future__ import annotations",
        "from typing import Any, Dict, Optional",
        "",
        "",
        "class RawAPI:",
        '    """Thin 1:1 wrapper over every discovered BFF endpoint.',
        "",
        "    Bound to a PayPay client via ``pp.raw``. Each method returns the",
        "    parsed ``payload`` dict from the BFF response.",
        '    """',
        "",
        "    def __init__(self, client) -> None:",
        "        self._c = client",
        "",
    ]

    all_spec = {**spec, **EXTRA}
    # Detect name collisions (v1 vs v2 endpoints with the same tail) and
    # suffix the v2 method with _v2 to keep both callable.
    name_counts: dict = {}
    for path in all_spec:
        name_counts.setdefault(endpoint_to_method(path), []).append(path)
    renamed: dict = {}
    for name, paths in name_counts.items():
        if len(paths) < 2:
            continue
        for p in paths:
            if "/v2/" in p:
                renamed[p] = name + "_v2"

    for path, s in sorted(all_spec.items()):
        method = s["method"]
        body_params = s.get("body") or []
        query_params = s.get("query") or []
        dto = s.get("dto")

        py_name = renamed.get(path, endpoint_to_method(path))

        # For GET, treat body list as query params (heuristic: BFFImpl reuses
        # Pair() names for both).
        if method == "GET":
            q = list(dict.fromkeys(body_params + query_params))
            b: list = []
        else:
            b = list(body_params)
            q = list(query_params)

        arg_specs = []
        for name in b + [x for x in q if x not in b]:
            arg_specs.append(f"{name}: Optional[Any] = None")
        sig = "self, *, " + ", ".join(arg_specs + ["**extra: Any"]) if arg_specs else "self, **extra: Any"

        lines.append(f"    def {py_name}({sig}) -> Dict[str, Any]:")
        docparts = [f'"""``{method} {path}``']
        if dto:
            docparts.append(f"        Body is a typed ``{dto}`` in the app; pass fields via **extra.")
        if b:
            docparts.append("        Body: " + ", ".join(b))
        if q:
            docparts.append("        Query: " + ", ".join(q))
        docparts.append('"""')
        lines.append("        " + "\n        ".join(docparts))

        if method == "GET":
            # All params are query
            if q:
                lines.append("        params: Dict[str, Any] = {}")
                for n in q:
                    lines.append(f"        if {n} is not None: params[{n!r}] = {n}")
                lines.append("        params.update({k: v for k, v in extra.items() if v is not None})")
                lines.append(f'        return self._c._request("GET", {path!r}, params=params)')
            else:
                lines.append("        params = {k: v for k, v in extra.items() if v is not None}")
                lines.append(f'        return self._c._request("GET", {path!r}, params=params or None)')
        else:
            if b or q:
                if b:
                    lines.append("        body: Dict[str, Any] = {}")
                    for n in b:
                        lines.append(f"        if {n} is not None: body[{n!r}] = {n}")
                    lines.append("        body.update(extra)")
                else:
                    lines.append("        body: Dict[str, Any] = dict(extra)")
                if q:
                    lines.append("        params: Dict[str, Any] = {}")
                    for n in q:
                        lines.append(f"        if {n} is not None: params[{n!r}] = {n}")
                    lines.append(f'        return self._c._request("POST", {path!r}, json=body, params=params or None)')
                else:
                    lines.append(f'        return self._c._request("POST", {path!r}, json=body)')
            else:
                # No captured params — body is either empty {} or a DTO the caller supplies via **extra
                lines.append("        body: Dict[str, Any] = dict(extra)")
                lines.append(f'        return self._c._request("POST", {path!r}, json=body)')

        lines.append("")

    lines.append("")
    lines.append("__all__ = ['RawAPI']")
    return "\n".join(lines)


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    code = render(spec)
    OUT.write_text(code, encoding="utf-8")
    total = len(spec) + len(EXTRA)
    print(f"wrote {OUT} with {total} generated methods")


if __name__ == "__main__":
    main()
