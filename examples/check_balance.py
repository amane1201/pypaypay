"""Usage:
    python examples/check_balance.py

Set PAYPAY_ACCESS_TOKEN (and optionally PAYPAY_REFRESH_TOKEN) in the env.
"""
import os
import json
from pypaypay import PayPay


def main() -> None:
    access = os.environ["PAYPAY_ACCESS_TOKEN"]
    refresh = os.environ.get("PAYPAY_REFRESH_TOKEN")
    with PayPay(access, refresh) as pp:
        print(json.dumps(pp.get_balance(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
