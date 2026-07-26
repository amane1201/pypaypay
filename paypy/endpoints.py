"""BFF endpoint paths verified against the decompiled PayPay Android app
(jp.ne.paypay.libs.bff.BFFImpl / C19344p.java).

All are relative to the base URL, e.g. ``https://app4.paypay.ne.jp``.
"""

# Wallet / balance
GET_BALANCE_INFO = "bff/v1/getBalanceInfo"
GET_WALLET_DISPLAY_INFO = "bff/v2/getWalletDisplayInfo"
GET_PAY2_BALANCE_HISTORY = "bff/v2/getPay2BalanceHistory"
GET_PAY2_BALANCE_CANCELLED_PENDING_CASHBACK_HISTORY = (
    "bff/v1/getPay2BalanceCancelledPendingCashBackHistory"
)

# P2P — send/receive by link
EXECUTE_P2P_SEND_MONEY_LINK = "bff/v2/executeP2PSendMoneyLink"
GET_P2P_LINK_INFO = "bff/v2/getP2PLinkInfo"
ACCEPT_P2P_SEND_MONEY_LINK = "bff/v2/acceptP2PSendMoneyLink"
REJECT_P2P_SEND_MONEY_LINK = "bff/v2/rejectP2PSendMoneyLink"
CANCEL_P2P_SEND_MONEY = "bff/v1/cancelP2PSendMoney"

# P2P — direct (user-to-user, not link based)
ACCEPT_P2P_SEND_MONEY = "bff/v1/acceptP2PSendMoney"
REJECT_P2P_SEND_MONEY = "bff/v1/rejectP2PSendMoney"

# Auth
OAUTH2_TOKEN = "bff/v2/oauth2/token"
OAUTH2_REFRESH = "bff/v2/oauth2/refresh"
OAUTH2_PAR = "bff/v2/oauth2/par"
