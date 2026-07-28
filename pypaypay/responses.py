"""Attribute-style wrappers for BFF response payloads.

Each wrapper subclass adds convenience properties that flatten the nested
BFF payload into what a caller usually wants (name, amount, chatRoomId,
etc.). The raw payload is always available via ``.raw``.
"""
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional


def _dig(d: Any, *keys: str) -> Any:
    """Return d[keys[0]][keys[1]]... or None if any step misses."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
        if cur is None:
            return None
    return cur


def _first(d: Any, keys: Iterable[str]) -> Any:
    for k in keys:
        v = _dig(d, *k.split(".")) if "." in k else (d.get(k) if isinstance(d, dict) else None)
        if v is not None:
            return v
    return None


class AttrDict(dict):
    """dict + attribute access. Missing keys return None, don't raise."""

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return self.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    @property
    def raw(self) -> Dict[str, Any]:
        return dict(self)


class Profile(AttrDict):
    """BFF は camelCase、Web 版は snake_case のフラットな形で返してくる。"""

    @property
    def name(self) -> Optional[str]:
        return _first(self, ["nickName", "userProfile.nickName", "displayName",
                             "display_name"])

    @property
    def external_user_id(self) -> Optional[str]:
        return _first(self, ["externalUserId", "userProfile.externalUserId",
                             "external_id"])

    @property
    def icon(self) -> Optional[str]:
        return _first(self, [
            "avatarImageUrl", "avatarImage.url",
            "userProfile.avatarImage.url", "userProfile.avatarImageUrl",
            "photo_url",
        ])

    @property
    def phone(self) -> Optional[str]:
        """Web 版だけ返してくる電話番号。BFF 側は None。"""
        return _first(self, ["mobile", "phoneNumber"])


class Balance(AttrDict):
    """BFF と Web 版で階層が違うので、どちらの形でも拾えるようにしてある。"""

    @property
    def money(self) -> int:
        return int(_first(self, ["walletSummary.usableBalance.money.amount",
                                 "walletSummary.money.amount",
                                 "walletDetail.emoneyBalanceInfo.balance",
                                 "money.amount", "moneyAmount"]) or 0)

    @property
    def money_light(self) -> int:
        return int(_first(self, ["walletSummary.usableBalance.moneyLight.amount",
                                 "walletSummary.moneyLight.amount",
                                 "walletDetail.prepaidBalanceInfo.balance",
                                 "moneyLight.amount", "moneyLightAmount"]) or 0)

    @property
    def points(self) -> int:
        return int(_first(self, ["walletSummary.usableBalance.point.amount",
                                 "walletSummary.point.amount",
                                 "walletDetail.cashBackBalanceInfo.balance",
                                 "point.amount", "pointAmount"]) or 0)

    @property
    def all_balance(self) -> int:
        v = _first(self, ["walletSummary.allTotalBalanceInfo.balance"])
        if v is not None:
            return int(v)
        return self.money + self.money_light + self.points

    @property
    def useable_balance(self) -> int:
        """Sum of money + money_light (points not spendable via P2P)."""
        v = _first(self, ["walletSummary.usableBalanceInfoWithoutCashback.balance"])
        if v is not None:
            return int(v)
        return self.money + self.money_light

    usable_balance = useable_balance


class LinkInfo(AttrDict):
    """BFF と Web 版で階層が違うので、どちらの形でも拾えるようにしてある。"""

    @property
    def amount(self) -> Optional[int]:
        v = _first(self, ["pendingP2PInfo.amount", "sendMoneyLink.amount",
                          "amount", "orderAmount"])
        return int(v) if v is not None else None

    @property
    def money(self) -> Optional[int]:
        v = _first(self, ["pendingP2PInfo.moneyAmount", "sendMoneyLink.moneyAmount",
                          "message.data.subWalletSplit.senderEmoneyAmount",
                          "moneyAmount"])
        return int(v) if v is not None else None

    @property
    def money_light(self) -> Optional[int]:
        v = _first(self, ["pendingP2PInfo.moneyLightAmount",
                          "sendMoneyLink.moneyLightAmount",
                          "message.data.subWalletSplit.senderPrepaidAmount",
                          "moneyLightAmount"])
        return int(v) if v is not None else None

    @property
    def has_password(self) -> bool:
        v = _first(self, ["pendingP2PInfo.isSetPasscode",
                          "sendMoneyLink.isSetPasscode",
                          "isSetPasscode", "hasPasscode"])
        return bool(v)

    @property
    def chat_room_id(self) -> Optional[str]:
        return _first(self, ["chatRoomId", "sendMoneyLink.chatRoomId",
                             "message.chatRoomId",
                             "pendingP2PInfo.chatRoomId"])

    @property
    def status(self) -> Optional[str]:
        return _first(self, ["orderStatus", "status",
                             "pendingP2PInfo.orderStatus",
                             "message.data.status",
                             "sendMoneyLink.orderStatus"])

    @property
    def order_id(self) -> Optional[str]:
        return _first(self, ["orderId", "pendingP2PInfo.orderId",
                             "message.data.orderId",
                             "sendMoneyLink.orderId"])

    @property
    def sender_external_id(self) -> Optional[str]:
        return _first(self, ["sender.externalUserId", "sender.externalId",
                             "pendingP2PInfo.sender.externalUserId",
                             "senderExternalId"])

    @property
    def sender_name(self) -> Optional[str]:
        return _first(self, ["sender.displayName", "sender.nickName",
                             "pendingP2PInfo.sender.displayName"])

    @property
    def sender_icon(self) -> Optional[str]:
        return _first(self, ["sender.photoUrl", "sender.avatarImageUrl",
                             "pendingP2PInfo.sender.photoUrl"])


class CreateLink(AttrDict):
    @property
    def link(self) -> Optional[str]:
        return _first(self, ["link", "shareLink", "linkUrl",
                             "sendMoneyLink.link"])

    @property
    def order_id(self) -> Optional[str]:
        return _first(self, ["orderId", "sendMoneyLink.orderId"])

    @property
    def chat_room_id(self) -> Optional[str]:
        return _first(self, ["chatRoomId", "sendMoneyLink.chatRoomId"])


class P2PCode(AttrDict):
    @property
    def p2pcode(self) -> Optional[str]:
        return _first(self, ["p2pCode", "p2pcode", "shareLink", "link",
                             "qrCodeUrl", "p2pCodeUrl"])


class SendMoney(AttrDict):
    @property
    def order_id(self) -> Optional[str]:
        return _first(self, ["orderId"])

    @property
    def chat_room_id(self) -> Optional[str]:
        return _first(self, ["chatRoomId"])


class SearchUser(AttrDict):
    @property
    def name(self) -> Optional[str]:
        return _first(self, ["nickName", "displayName", "user.nickName"])

    @property
    def icon(self) -> Optional[str]:
        return _first(self, ["avatarImageUrl", "avatarImage.url",
                             "user.avatarImage.url"])

    @property
    def external_user_id(self) -> Optional[str]:
        return _first(self, ["externalUserId", "user.externalUserId"])


class Chatroom(AttrDict):
    @property
    def chatroom_id(self) -> Optional[str]:
        return _first(self, ["chatRoomId", "channelUrl", "chatRoom.chatRoomId",
                             "channel.channelUrl"])

    chat_room_id = chatroom_id  # alias


class BarcodeInfo(AttrDict):
    @property
    def amount(self) -> Optional[int]:
        v = _first(self, ["amount", "orderInfo.amount",
                          "paymentInfo.amount", "paymentAmount"])
        return int(v) if v is not None else None

    @property
    def external_user_id(self) -> Optional[str]:
        return _first(self, ["externalUserId", "merchantUserExternalId",
                             "receiverExternalUserId",
                             "user.externalUserId", "paymentInfo.externalUserId"])

    @property
    def merchant_name(self) -> Optional[str]:
        return _first(self, ["merchantName", "orderInfo.merchantName"])
