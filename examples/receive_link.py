"""Claim (accept) a PayPay send-money link.

    python examples/receive_link.py https://pay.paypay.ne.jp/xxxxxxxxxx
    python examples/receive_link.py <verification_code> --passcode 1234
"""
import argparse
import json
import os
from paypy import PayPay, LinkPasscodeRequired, LinkAlreadyClaimed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("link", help="link URL or bare verification code")
    ap.add_argument("--passcode", default=None)
    ap.add_argument("--info-only", action="store_true", help="only fetch info, don't claim")
    args = ap.parse_args()

    access = os.environ["PAYPAY_ACCESS_TOKEN"]
    refresh = os.environ.get("PAYPAY_REFRESH_TOKEN")
    with PayPay(access, refresh) as pp:
        info = pp.get_link_info(args.link)
        print("info:", json.dumps(info, ensure_ascii=False, indent=2))
        if args.info_only:
            return
        try:
            result = pp.accept_link(args.link, passcode=args.passcode)
        except LinkPasscodeRequired:
            print("passcode required; re-run with --passcode <code>")
            return
        except LinkAlreadyClaimed:
            print("link already claimed / rejected")
            return
        print("accepted:", json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
