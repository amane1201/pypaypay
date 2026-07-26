"""Parse BFFImpl (C19344p.java) and extract:
  endpoint -> (kind, body_params, query_params, has_dto)

For each occurrence of "bff/v.../..." in the file, we walk backwards to the
enclosing top-level method (opening brace at column 4) and forward to the
call site. We then look inside that method for Pair("name", ...) tokens and
C5186x.m5547a("name", ...) single-pair maps.

We also detect DTO-typed bodies (constructor call before the endpoint use).
"""
import json
import re
from pathlib import Path

import os

# Override with PAYPAY_BFF_SRC if the decompiled BFFImpl lives elsewhere.
SRC = Path(os.environ.get(
    "PAYPAY_BFF_SRC",
    r"../../jadx_out/sources/jp/p256ne/paypay/libs/bff/C19344p.java",
))
if not SRC.is_absolute():
    SRC = (Path(__file__).parent / SRC).resolve()

OUT = Path(__file__).parent / "endpoints.json"

text = SRC.read_text(encoding="utf-8", errors="ignore")
lines = text.splitlines()

# Locate every method: `public final ... mo\w+(... AbstractC26817c abstractC26817c) {`
method_starts = []
method_re = re.compile(r"^\s{4}public\s+.*\bmo\w+\(")
for i, line in enumerate(lines):
    if method_re.match(line):
        method_starts.append(i)
method_starts.append(len(lines))

# For each method body, find the endpoint string(s).
endpoint_re = re.compile(r'"([a-z][a-z0-9-]*/v[0-9]/[A-Za-z0-9_/]+)"')
pair_re = re.compile(r'new Pair\("([A-Za-z0-9_]+)"')
single_map_re = re.compile(r'C5186x\.m5547a\("([A-Za-z0-9_]+)"')
list_map_re = re.compile(r'C21183o0\.m18227e\((.*?)\);', re.S)
dto_ctor_re = re.compile(r'new (\w+DTO)\(')
PATH = r'([a-z][a-z0-9-]*/v[0-9]/[A-Za-z0-9_/]+)'
call_re = re.compile(
    r'm9729e\("' + PATH + r'",\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*(true|false)'
)
call_get_re = re.compile(
    r'C10278w\.m9722a\([^,]+,\s*"' + PATH + r'",\s*([^,]+)'
)
call_g_re = re.compile(
    r'm9730g\("' + PATH + r'",[^,]+,\s*new C10242a0\([^,]+,\s*"[^"]+",\s*([^,]+),\s*([^,]+)'
)

endpoints: dict = {}

for start, end in zip(method_starts, method_starts[1:]):
    body_lines = lines[start:end]
    body = "\n".join(body_lines)
    for m in endpoint_re.finditer(body):
        ep = m.group(1)
        # Find call kind
        kind = None
        body_arg = None
        query_arg = None
        dto = None
        for c in call_re.finditer(body):
            if c.group(1) == ep:
                kind = "POST"
                body_arg = c.group(2).strip()
                query_arg = c.group(4).strip()
                break
        if kind is None:
            for c in call_get_re.finditer(body):
                if c.group(1) == ep:
                    kind = "GET"
                    body_arg = c.group(2).strip()
                    break
        if kind is None:
            for c in call_g_re.finditer(body):
                if c.group(1) == ep:
                    kind = "POST"
                    body_arg = c.group(3).strip()
                    query_arg = c.group(2).strip()
                    break
        if kind is None:
            kind = "POST"  # fallback

        # Extract param names of body and query variables
        body_params = []
        query_params = []
        # Find variable assignment lines like:
        # Map mapM18227e = C21183o0.m18227e(new Pair("a", x), new Pair("b", y));
        # Map mapM5547a = C5186x.m5547a("k", v);
        # <DtoName> dto = new <DtoName>(...);
        for var_name, target in (("mapM18227e", "body"),
                                 ("mapM5547a", "body"),
                                 ("linkedHashMapM28767a", "body")):
            pass

        # Instead: scan all Pair("name", assignments) in the method — they belong
        # to whichever map var precedes the endpoint call. Since a method usually
        # only calls one endpoint, just aggregate all Pair names.
        pair_names = [m2.group(1) for m2 in pair_re.finditer(body)]
        single_names = [m2.group(1) for m2 in single_map_re.finditer(body)]

        # Distinguish body vs query: single_map_re typically corresponds to the
        # 4th arg (query/header override map). We can't be 100% sure without
        # dataflow analysis; heuristic: if there are two maps, first goes body,
        # second goes query.
        if pair_names and single_names:
            body_params = pair_names
            query_params = single_names
        elif pair_names:
            body_params = pair_names
        elif single_names:
            body_params = single_names

        dto_match = dto_ctor_re.search(body)
        if dto_match and not body_params:
            dto = dto_match.group(1)

        # If this endpoint already recorded with richer info, don't overwrite
        if ep not in endpoints or (
            len(endpoints[ep]["body"]) < len(body_params)
        ):
            endpoints[ep] = {
                "method": kind,
                "body": body_params,
                "query": query_params,
                "dto": dto,
            }

# Sort
endpoints = dict(sorted(endpoints.items()))
OUT.write_text(json.dumps(endpoints, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(endpoints)} endpoints -> {OUT}")
for ep, spec in list(endpoints.items())[:5]:
    print(ep, spec)
