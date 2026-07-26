"""Create a send-money share link.

    python examples/send_link.py 1 --passcode 1234
"""
import argparse
import json
import os
from paypy import PayPay


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("amount", type=int, help="JPY amount to send")
    ap.add_argument("--passcode", default=None)
    ap.add_argument("--comment", default=None)
    args = ap.parse_args()

    access = os.environ["PAYPAY_ACCESS_TOKEN"]
    refresh = os.environ.get("PAYPAY_REFRESH_TOKEN")
    with PayPay(access, refresh) as pp:
        result = pp.send_money_link(
            args.amount, passcode=args.passcode, user_comment=args.comment
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
