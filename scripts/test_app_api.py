"""OTP ログイン → app API (www.paypay.ne.jp/app) の疎通テスト。

ブラウザも WAF も無しで、BFF のプロキシ面をどこまで叩けるか実アカウントで確かめる。
パスワードは聞かれてから入力する（履歴に残さない）。

    py -3 scripts/test_app_api.py --phone 08012345678
"""
from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

from pypaypay import WebPayPay                              # noqa: E402
from pypaypay.exceptions import APIError, AuthError         # noqa: E402


def run(label, fn):
    try:
        r = fn()
        s = r if isinstance(r, (str, int, float)) else type(r).__name__
        print(f"  OK   {label:26} -> {s}")
        return True
    except (APIError, AuthError) as e:
        print(f"  NG   {label:26} -> {type(e).__name__}: {e}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phone", help="電話番号 / メール（省略時は聞く）")
    ap.add_argument("--token", help="既存の Web トークンがあれば（ログインを省く）")
    ap.add_argument("--proxy", help="http://127.0.0.1:8080 とか")
    ap.add_argument("--save", metavar="PATH", help="トークンを JSON 保存")
    ap.add_argument("--raw-sweep", action="store_true",
                    help="全 raw エンドポイントの到達可否を数える")
    args = ap.parse_args()

    if args.token:
        pp = WebPayPay(access_token=args.token, proxy=args.proxy)
    else:
        phone = args.phone or input("電話番号: ").strip()
        password = getpass.getpass("パスワード（表示されません）: ")
        pp = WebPayPay(phone, password, proxy=args.proxy)
        if pp.login().get("otp_required"):
            otp = input("OTP: ").strip()
            pp.login_otp(otp)
        print("access_token:", (pp.access_token or "")[:8] + "…")

    print("\n--- 高レベル ---")
    run("get_profile", lambda: pp.get_profile().name)
    run("get_balance", lambda: pp.get_balance().all_balance)
    run("get_history", lambda: len(pp.get_history(size=3).raw))
    run("get_payment_methods", lambda: type(pp.get_payment_methods()).__name__)
    run("get_payout_info", lambda: type(pp.get_payout_info()).__name__)
    run("create_p2pcode", lambda: type(pp.create_p2pcode()).__name__)
    run("create_paymentcode", lambda: type(pp.create_paymentcode()).__name__)

    print("\n--- raw（BFF プロキシ）---")
    run("raw.get_user_profile", lambda: type(pp.raw.get_user_profile()).__name__)
    run("raw.get_kyc_display_info", lambda: type(pp.raw.get_kyc_display_info()).__name__)
    run("raw.get_gv_list", lambda: type(pp.raw.get_gv_list(statusFilter="ACTIVE", pageSize=5)).__name__)
    run("app_call getServiceStatus", lambda: type(pp.app_call("GET", "getServiceStatus")).__name__)

    print("\n--- 使えないはずのもの（E_WEB_* が出れば正しい）---")
    run("raw.execute_p2p_send_money", lambda: pp.raw.execute_p2p_send_money(amount=1))
    run("send_money(高レベル)", lambda: pp.send_money(1, "x"))

    if args.raw_sweep:
        import importlib
        RawAPI = importlib.import_module("pypaypay.raw").RawAPI
        eps = json.load(open(Path(__file__).with_name("endpoints.json"), encoding="utf-8"))
        reached = unavail = other = 0
        for path, meta in eps.items():
            m = (meta.get("method") or "GET").upper()
            try:
                pp._request(m, path, json={} if m != "GET" else None)
                other += 1
            except APIError as e:
                if e.code in ("E_WEB_UNAVAILABLE", "E_WEB_GATED"):
                    unavail += 1
                else:
                    reached += 1  # C0002 等 = 到達（パラメータ不足なだけ）
            except AuthError:
                reached += 1
        print(f"\n--- raw 到達サマリ ---\n  到達: {reached}  未公開: {unavail}  その他: {other}")

    if args.save:
        Path(args.save).write_text(json.dumps({
            "access_token": pp.access_token, "refresh_token": pp.refresh_token,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nトークンを {args.save} に保存")
    pp.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
