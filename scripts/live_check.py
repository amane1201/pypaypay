"""実アカウントで pypaypay の各機能を叩いて確認するチェッカー。

デフォルトは読み取りだけ。お金が動く操作は --write を付けたときだけ走る。

    # 読み取りのみ（残高・履歴・プロフィールなど）
    py -3 scripts/live_check.py --token <アクセストークン>

    # リンクの解析も一緒に
    py -3 scripts/live_check.py --token <AT> --link https://pay.paypay.ne.jp/xxxxxxxx

    # 送金リンク作成 → 解析 → チャット送信 → キャンセル（1円が一往復する）
    py -3 scripts/live_check.py --token <AT> --write --amount 1

トークンは環境変数 PAYPAY_ACCESS_TOKEN / PAYPAY_REFRESH_TOKEN でも渡せる。

ここで確認できないもの（相手か店舗が必要／取り消せない）:
  link_receive, pay_qr_code, get_barcode_info, send_money, cashout_to_paypaybank
"""
from __future__ import annotations

import argparse
import os
import sys
import traceback
import unicodedata
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pypaypay import PayPay  # noqa: E402
from pypaypay.exceptions import APIError, PayPayError  # noqa: E402

OK = "OK  "
NG = "NG  "
SKIP = "--  "


def _width(s: str) -> int:
    """Display width, counting full-width (CJK) characters as 2 columns."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


class Runner:
    def __init__(self) -> None:
        self.results: List[Tuple[str, str, str]] = []

    def check(self, name: str, fn: Callable[[], Any]) -> Any:
        try:
            summary = fn()
        except PayPayError as e:
            code = f" [{e.code}]" if isinstance(e, APIError) and e.code else ""
            self.results.append((NG, name, f"{type(e).__name__}{code}: {e}"))
            return None
        except Exception as e:  # noqa: BLE001 - a checker should never explode
            self.results.append((NG, name, f"{type(e).__name__}: {e}"))
            if os.environ.get("LIVE_CHECK_TRACEBACK"):
                traceback.print_exc()
            return None
        value, text = summary if isinstance(summary, tuple) else (summary, summary)
        self.results.append((OK, name, str(text)))
        return value

    def skip(self, name: str, why: str) -> None:
        self.results.append((SKIP, name, why))

    def report(self) -> int:
        width = max(_width(n) for _, n, _ in self.results)
        print()
        for status, name, detail in self.results:
            pad = " " * (width - _width(name))
            print(f"{status}{name}{pad}  {detail}")
        failed = [r for r in self.results if r[0] == NG]
        skipped = [r for r in self.results if r[0] == SKIP]
        print(f"\n{len(self.results) - len(failed) - len(skipped)} ok / "
              f"{len(failed)} failed / {len(skipped)} skipped")
        return len(failed)


# ----------------------------------------------------------------------
# read-only
# ----------------------------------------------------------------------
def read_only_checks(pp: PayPay, r: Runner, args) -> Optional[str]:
    """全部の読み取り系を叩いて、掴めたチャットルーム ID を返す。"""
    def profile():
        me = pp.get_profile()
        if not me.external_user_id:
            raise AssertionError(f"externalUserId が取れない: {dict(me)}")
        return me, f"{me.name} / {me.external_user_id}"

    me = r.check("get_profile", profile)

    def balance():
        b = pp.get_balance()
        return b, (f"money={b.money} light={b.money_light} point={b.points} "
                   f"usable={b.useable_balance}")

    r.check("get_balance", balance)

    def history():
        h = pp.get_history(size=3)
        items = h.get("transactions") or h.get("historyList") or h.get("items") or []
        return h, f"{len(items)} 件（キー: {', '.join(list(h)[:4]) or 'なし'}）"

    r.check("get_history", history)

    def point_history():
        h = pp.get_point_history(size=3)
        return h, f"キー: {', '.join(list(h)[:4]) or 'なし'}"

    r.check("get_point_history", point_history)

    def chat_rooms():
        rooms = pp.get_chat_rooms(size=3)
        lst = rooms.get("chatRooms") or rooms.get("rooms") or []
        return rooms, f"{len(lst)} ルーム（キー: {', '.join(list(rooms)[:4]) or 'なし'}）"

    r.check("get_chat_rooms", chat_rooms)

    if args.user_id:
        def search():
            hit = pp.search_p2puser(args.user_id)
            return hit, f"{hit.name} / {hit.external_user_id}"
        r.check("search_p2puser", search)
    else:
        r.skip("search_p2puser", "--user-id <PayPayID> を渡すと確認する")

    if args.link:
        def link_check():
            info = pp.link_check(args.link)
            return info, (f"amount={info.amount} status={info.status} "
                          f"passcode={info.has_password} order={info.order_id}")
        r.check("link_check", link_check)

        def link_check_web():
            info = pp.link_check(args.link, web=True)
            return info, f"amount={info.amount} status={info.status}"
        r.check("link_check(web=True)", link_check_web)
    else:
        r.skip("link_check", "--link <送金リンク> を渡すと確認する")
        r.skip("link_check(web=True)", "--link <送金リンク> を渡すと確認する")

    if me and me.external_user_id:
        def chatroom():
            room = pp.initialize_chatroom(me.external_user_id)
            return room, f"chatRoomId={room.chatroom_id}"
        room = r.check("initialize_chatroom(自分)", chatroom)
    else:
        r.skip("initialize_chatroom", "get_profile が失敗したので実行できない")
        room = None

    if room and room.chatroom_id:
        def messages():
            out = pp.get_chat_room_messages(room.chatroom_id, size=3)
            return out, f"channelUrl={out.channelUrl}"
        r.check("get_chat_room_messages", messages)
        return room.chatroom_id

    r.skip("get_chat_room_messages", "チャットルーム ID が取れなかった")
    return None


def refresh_check(pp: PayPay, r: Runner) -> None:
    def refresh():
        before = pp.access_token
        tokens = pp.token_refresh()
        if not tokens.access_token:
            raise AssertionError(f"accessToken が空: {tokens}")
        changed = "新しいトークンに更新された" if tokens.access_token != before else "同じトークンが返った"
        return tokens, f"{changed} / refresh_token={'あり' if tokens.refresh_token else 'なし'}"

    r.check("token_refresh", refresh)


def drift_probe(pp: PayPay, r: Runner, room: Optional[str]) -> None:
    """client と raw で HTTP メソッドが食い違っている所を実機で確定させる。

    両方 OK なら好きな方でいい。片方だけ通ったら、そっちが正解。
    """
    for verb in ("GET", "POST"):
        def probe(verb=verb):
            payload = pp._request(verb, "bff/v1/getBalanceInfo")
            return payload, f"{verb} 成功（キー: {', '.join(list(payload)[:3]) or 'なし'}）"
        r.check(f"probe getBalanceInfo [{verb}]", probe)

    if not room:
        for verb in ("GET", "POST"):
            r.skip(f"probe getChatRoomHasMessageFromUser [{verb}]",
                   "チャットルーム ID が取れなかった")
        return

    for verb in ("GET", "POST"):
        def probe_room(verb=verb):
            kw = ({"params": {"channelUrl": room, "pageSize": 1}} if verb == "GET"
                  else {"json": {"channelUrl": room, "pageSize": 1}})
            payload = pp._request(verb, "p2p/v1/getChatRoomHasMessageFromUser", **kw)
            return payload, f"{verb} 成功（キー: {', '.join(list(payload)[:3]) or 'なし'}）"
        r.check(f"probe getChatRoomHasMessageFromUser [{verb}]", probe_room)


# ----------------------------------------------------------------------
# write (money moves)
# ----------------------------------------------------------------------
def write_checks(pp: PayPay, r: Runner, args) -> None:
    amount = args.amount

    def create():
        link = pp.create_link(amount, user_comment="pypaypay live_check")
        if not link.link or not link.order_id:
            raise AssertionError(f"link/orderId が取れない: {dict(link)}")
        return link, f"{link.link} (order={link.order_id})"

    link = r.check(f"create_link({amount}円)", create)
    if not link:
        for name in ("link_check(作ったリンク)", "send_message", "link_cancel"):
            r.skip(name, "create_link が失敗した")
        return

    def check_created():
        info = pp.link_check(link.link)
        if info.order_id != link.order_id:
            raise AssertionError(f"orderId が一致しない: {info.order_id} != {link.order_id}")
        if info.amount != amount:
            raise AssertionError(f"amount が一致しない: {info.amount} != {amount}")
        return info, f"amount={info.amount} status={info.status} order={info.order_id}"

    info = r.check("link_check(作ったリンク)", check_created)

    room = (link.chat_room_id or (info.chat_room_id if info else None))
    if room:
        def message():
            out = pp.send_message(room, "pypaypay live_check")
            return out, f"送信 OK（キー: {', '.join(list(out)[:3]) or 'なし'}）"
        r.check("send_message", message)
    else:
        r.skip("send_message", "chatRoomId が取れなかった")

    def cancel():
        out = pp.link_cancel(link.link, link_info=info)
        return out, f"キャンセル OK（キー: {', '.join(list(out)[:3]) or 'なし'}）"

    cancelled = r.check("link_cancel", cancel)
    if cancelled is None:
        print(f"\n!! {amount}円のリンクが残っている: {link.link}")
        print("!! アプリか link_cancel で自分で取り消して。")


def confirm(amount: int) -> bool:
    print(f"--write: {amount}円の送金リンクを作って、チャット送信して、"
          "そのままキャンセルします（お金は戻ります）。")
    try:
        return input("実行する? [yes/N]: ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--token", default=os.environ.get("PAYPAY_ACCESS_TOKEN"),
                   help="アクセストークン（環境変数 PAYPAY_ACCESS_TOKEN でも可）")
    p.add_argument("--refresh", default=os.environ.get("PAYPAY_REFRESH_TOKEN"),
                   help="リフレッシュトークン（環境変数 PAYPAY_REFRESH_TOKEN でも可）")
    p.add_argument("--link", help="link_check に食わせる送金リンク")
    p.add_argument("--user-id", help="search_p2puser に食わせる PayPayID")
    p.add_argument("--refresh-check", action="store_true",
                   help="token_refresh も叩く（リフレッシュトークンが回転する）")
    p.add_argument("--probe-drift", action="store_true",
                   help="getBalanceInfo を GET/POST 両方で叩いてどちらが正しいか確かめる")
    p.add_argument("--write", action="store_true",
                   help="送金リンク作成→キャンセルまで実行する（お金が一往復する）")
    p.add_argument("--amount", type=int, default=1, help="--write で作る金額（既定 1 円）")
    p.add_argument("--yes", action="store_true", help="--write の確認を飛ばす")
    p.add_argument("--proxy", help="http://host:port など")
    args = p.parse_args()

    if not args.token:
        p.error("--token か環境変数 PAYPAY_ACCESS_TOKEN が必要")

    r = Runner()
    with PayPay(access_token=args.token, refresh_token=args.refresh,
                proxy=args.proxy) as pp:
        print(f"base_url = {pp.base_url}")
        room = read_only_checks(pp, r, args)

        if args.probe_drift:
            drift_probe(pp, r, room)
        else:
            r.skip("probe (verb ドリフト)", "--probe-drift で GET/POST を比較する")

        if args.refresh_check:
            if args.refresh:
                refresh_check(pp, r)
            else:
                r.skip("token_refresh", "--refresh <リフレッシュトークン> が無い")
        else:
            r.skip("token_refresh", "--refresh-check で実行（トークンが回転する）")

        if args.write:
            if args.yes or confirm(args.amount):
                write_checks(pp, r, args)
            else:
                r.skip("create_link 一式", "確認でキャンセルした")
        else:
            r.skip("create_link 一式", "--write で実行（お金が一往復する）")

    for name in ("link_receive", "pay_qr_code", "get_barcode_info", "send_money",
                 "set_money_priority", "cashout_to_paypaybank"):
        r.skip(name, "相手/店舗が必要、または取り消せないので自動確認しない")

    return r.report()


if __name__ == "__main__":
    raise SystemExit(main())
