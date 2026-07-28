"""下の CONFIG にメアド(or 電話番号)とパスワードを入れて実行するだけで、
pypaypay の機能をまとめて確認するファイル。

    py -3 scripts/test_everything.py

やること:
  1. ログイン: メアパスを送る → OTP が届く → ここに入力（ブラウザは開かない）
  2. 取れたトークンを paypay_session.json に保存 → 次回以降はログイン不要
  3. 読み取り系ぜんぶ（プロフィール/残高/履歴/DM/検索/リンク解析…）
  4. WRITE=True なら 1円の送金リンクを作って→解析→DM→キャンセル（お金は戻る）

■ PayPay には API が2系統ある
  - Web 版 (www.paypay.ne.jp/app) … メアパス→OTP でトークンが取れる。ここで使う方。
  - BFF   (app4.paypay.ne.jp)     … アプリ 5.x 用。ログインは Web ポータルに
                                     委譲されていて、PAR → ブラウザ → callback URL
                                     を貼る方式でしか通せない（--browser-login）。
  高レベル API は BFF 向けに書いてあるので、OTP で取ったトークンが BFF でも
  通るかどうかをログイン直後にプローブして表示する。

■ ログイン失敗は3回まで
  超えるとアカウントが一時ロックされてサポート送りになる。
  パスワードうろ覚えで走らせないこと。トークンが保存済みならログインは起きない。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

# ======================================================================
# CONFIG — ここだけ書き換えれば動く
# ======================================================================
CONFIG = {
    # ログイン用（メアド or 電話番号）。トークンが保存済みなら空でもいい。
    # ここに直接書くと git に載る事故が起きるので、環境変数の方が安全（下を見て）。
    "id": "",                 # 例: "mail@example.com" / "080-1234-5678"
    "password": "",           # 例: "Gay1919"
    "device_uuid": "",        # 登録済みデバイスがあれば入れる（無ければ空）

    # 任意。入れるとその分もテストする。
    "link": "",               # 解析させたい送金リンク 例: "https://pay.paypay.ne.jp/xxxxxxxx"
    "user_id": "",            # 検索させたい PayPayID 例: "amane1201"

    # ↑の link を実際に受け取るか。取り消せないので既定は False。
    # True か --receive で実行、直前に金額と送り主を出して確認を取る。
    "receive": False,
    "link_passcode": "",      # パスワード付きリンクならここに

    # お金を動かすテスト（作ってすぐキャンセルするので残高は戻る）
    "write": True,
    "amount": 1,              # 円

    "proxy": "",              # 例: "127.0.0.1:8888"（日本国外から叩くとき）
}

# CONFIG を空にしておけば環境変数から読む（パスワードをファイルに残したくない時用）
#   PowerShell:  $env:PAYPAY_ID="080..."; $env:PAYPAY_PASSWORD="..."
for _key, _env in (("id", "PAYPAY_ID"), ("password", "PAYPAY_PASSWORD"),
                   ("device_uuid", "PAYPAY_DEVICE_UUID")):
    if not CONFIG[_key]:
        CONFIG[_key] = os.environ.get(_env, "")

SESSION_FILE = REPO / "paypay_session.json"

import live_check  # noqa: E402
from pypaypay import PayPay, WebPayPay  # noqa: E402
from pypaypay.exceptions import APIError, PayPayError  # noqa: E402


# ======================================================================
# 1. セッション（トークン）の用意
# ======================================================================
def web_client(pp: PayPay) -> WebPayPay:
    """同じトークンと HTTP クライアントを使い回す Web 版クライアント。"""
    return WebPayPay(access_token=pp.access_token,
                     client_uuid=pp.client_uuid, http=pp._http)


def load_session() -> dict:
    if not SESSION_FILE.exists():
        return {}
    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print(f"!! {SESSION_FILE.name} が読めなかったので無視する")
        return {}


def save_session(pp: PayPay) -> None:
    SESSION_FILE.write_text(json.dumps({
        "access_token": pp.access_token,
        "refresh_token": pp.refresh_token,
        "device_uuid": pp.device_uuid,
        "client_uuid": pp.client_uuid,
        "web_token": pp.web_token,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"→ トークンを {SESSION_FILE.name} に保存した（次回はログイン不要）")


def client_from_session(session: dict, proxy) -> PayPay | None:
    if not session.get("access_token"):
        return None
    pp = PayPay(access_token=session["access_token"],
                refresh_token=session.get("refresh_token"),
                device_uuid=session.get("device_uuid"),
                client_uuid=session.get("client_uuid"),
                proxy=proxy)
    pp.web_token = bool(session.get("web_token"))
    try:
        me = pp.get_profile()
        pp.bff_ok = True
        print(f"→ 保存済みトークンでログイン済み（BFF）: {me.name} / {me.external_user_id}")
        return pp
    except PayPayError as e:
        if not pp.web_token:
            print(f"→ 保存済みトークンが使えなかった（{type(e).__name__}: {e}）")
            pp.close()
            return None

    # Web 版で取ったトークンなら、Web 版で生きているか確かめる
    try:
        me = web_client(pp).get_profile()
    except PayPayError as e:
        print(f"→ 保存済みトークンが使えなかった（{type(e).__name__}: {e}）")
        pp.close()
        return None
    pp.bff_ok = False
    print(f"→ 保存済みトークンでログイン済み（Web 版）: {me.name} / {me.external_user_id}")
    return pp


def check_credentials(cfg) -> bool:
    if not cfg["id"] or not cfg["password"]:
        print("!! CONFIG の id / password が空。ログインできないのでここで止める。")
        print("!! （トークンを持ってるなら paypay_session.json に入れるか、")
        print("!!   scripts/live_check.py --token <AT> を使って）")
        return False
    print("ログイン失敗は3回までなので、パスワードが確かでないなら今すぐ中止して。")
    return input("ログインを始める? [yes/N]: ").strip().lower() in ("y", "yes")


def probe_token(pp: PayPay) -> bool:
    """取れたトークンが Web 版 / BFF どっちで通るか確かめる。BFF で通れば True。"""
    print("\n--- このトークンがどこで通るか ---")
    try:
        pp._web_login.probe()
        print("Web 版 (www.paypay.ne.jp/app)  : OK")
    except PayPayError as e:
        print(f"Web 版 (www.paypay.ne.jp/app)  : NG  {type(e).__name__}: {e}")

    try:
        me = pp.get_profile()
        print(f"BFF   (app4.paypay.ne.jp)     : OK  {me.name} / {me.external_user_id}")
        bff_ok = True
    except PayPayError as e:
        print(f"BFF   (app4.paypay.ne.jp)     : NG  {type(e).__name__}: {e}")
        print("→ OTP で取れるのは Web 版のトークンなので、BFF 側の高レベル API は")
        print("  このトークンでは動かない。Web 版用の実装を足すか、ブラウザ方式")
        print("  (--browser-login) で BFF のトークンを取る必要がある。")
        bff_ok = False
    print("---------------------------------\n")
    return bff_ok


def login_with_otp(cfg, proxy) -> PayPay | None:
    """メアパス → OTP → トークン。ブラウザは開かない。"""
    if not check_credentials(cfg):
        return None

    pp = PayPay(cfg["id"], cfg["password"], cfg["device_uuid"] or None, proxy=proxy)
    try:
        started = pp.otp_login()
    except PayPayError as e:
        print(f"\n!! ログイン開始に失敗: {type(e).__name__}: {e}")
        pp.close()
        return None

    if started.get("otp_required"):
        prefix = started.get("otp_prefix") or ""
        print(f"\n→ OTP を送った。SMS / メールを確認して。")
        if prefix:
            print(f"  （届く番号の頭に付いてる記号: {prefix} ／ 入力するのは数字の部分だけ）")
        while True:
            otp = input("OTP: ").strip()
            if not otp:
                print("!! 空だったので中止")
                pp.close()
                return None
            if otp.lower() in ("r", "resend"):
                try:
                    pp.otp_resend()
                    print("→ 送り直した")
                except PayPayError as e:
                    print(f"!! 送り直せなかった: {type(e).__name__}: {e}")
                continue
            try:
                pp.otp_confirm(otp)
                break
            except PayPayError as e:
                print(f"!! OTP が通らなかった: {e}")
                print("!! もう一度入れるか、r で送り直し、空 Enter で中止")
    else:
        print("→ OTP 無しでトークンが取れた")

    print("→ ログイン成功（Web 版トークン）")
    pp.bff_ok = probe_token(pp)
    save_session(pp)
    return pp


def login_with_browser(cfg, proxy) -> PayPay | None:
    """BFF(app4) 側の PAR フロー。ブラウザで通して callback URL を貼る方式。"""
    if not check_credentials(cfg):
        return None

    pp = PayPay(cfg["id"], cfg["password"], cfg["device_uuid"] or None, proxy=proxy)
    url = pp.login()
    print("\nこの URL をブラウザで開いて、メアパスと SMS の認証コードを入れて:")
    print(f"  {url}")
    print("（約60秒で失効するので急いで。開かなかったら手でコピペして）")
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001 - 開けなくても手でコピペすればいい
        pass

    print("\n通し終わると paypay://oauth2/callback?code=... に飛ばされる。")
    print("そのURL（か code の部分だけ）をここに貼って:")
    answer = input("callback URL: ").strip()
    if not answer:
        print("!! 何も入力されなかったので中止")
        pp.close()
        return None

    code = PayPay._extract_auth_code(answer)
    par_id = (pp._request_uri or "").rsplit(":", 1)[-1]
    if par_id and code == par_id:
        print("\n!! それは今こっちが表示した URL（ポータルの ?id=...）で、認可コードじゃない。")
        print("!! ブラウザでログインを完了させたあと、飛ばされる")
        print("!!   paypay://oauth2/callback?code=... の方を貼って。")
        print("!! （PC のブラウザだと paypay:// に飛べずエラー画面になることがある。")
        print("!!   その場合はアドレスバーの URL か、ブロックされたリンクをコピーして）")
        pp.close()
        return None

    try:
        pp.login_confirm(answer)
    except APIError as e:
        print(f"\n!! トークン交換に失敗: [{e.status}/{e.code}] {e}")
        print("!! サーバが返した中身:")
        print(json.dumps(e.payload, indent=2, ensure_ascii=False))
        print("\n!! よくある原因:")
        print("!!  1. 貼った URL が callback ではない（?code= が入ってるか確認）")
        print("!!  2. 時間切れ。表示された URL は約60秒、code も短命なので急いで通す")
        print("!!  3. code は使い捨て。一度使った/失敗したら --relogin でやり直す")
        pp.close()
        return None

    me = pp.get_profile()
    print(f"→ ログイン成功: {me.name} / {me.external_user_id}")
    save_session(pp)
    return pp


def get_client(cfg, args) -> PayPay | None:
    print("=" * 70)
    print("1. ログイン")
    print("=" * 70)
    proxy = cfg["proxy"] or None
    if not args.relogin:
        pp = client_from_session(load_session(), proxy)
        if pp:
            print()
            return pp
    if args.browser_login:
        return login_with_browser(cfg, proxy)
    return login_with_otp(cfg, proxy)


# ======================================================================
# 2. 実アカウントのテスト（live_check.py の中身を使い回す）
# ======================================================================
def run_live_tests(pp: PayPay, cfg, args) -> int:
    print("=" * 70)
    print("2. 実アカウントでのテスト")
    print("=" * 70)
    r = live_check.Runner()
    opts = SimpleNamespace(link=cfg["link"] or None,
                           user_id=cfg["user_id"] or None,
                           amount=cfg["amount"])

    room = live_check.read_only_checks(pp, r, opts)
    live_check.drift_probe(pp, r, room)

    if pp.refresh_token:
        live_check.refresh_check(pp, r)
        save_session(pp)          # refresh でトークンが回るので保存し直す
    else:
        r.skip("token_refresh", "refresh_token を持っていない")

    write = cfg["write"] and not args.no_write
    if write:
        if args.yes or live_check.confirm(cfg["amount"]):
            live_check.write_checks(pp, r, opts)
        else:
            r.skip("create_link 一式", "確認でキャンセルした")
    else:
        r.skip("create_link 一式", "CONFIG['write'] が False（または --no-write）")

    for name in ("link_receive", "pay_qr_code", "get_barcode_info", "send_money",
                 "set_money_priority", "cashout_to_paypaybank"):
        r.skip(name, "相手/店舗が必要、または取り消せないので自動確認しない")

    return r.report()


def confirm_receive(info) -> bool:
    """受け取りは取り消せないので、金額と送り主を出してから聞く。"""
    print(f"\n!! これから {info.amount} 円のリンクを実際に受け取る。取り消せない。")
    print(f"!!   送り主: {info.sender_name} / 状態: {info.status}")
    try:
        return input("受け取る? [yes/N]: ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def run_web_tests(pp: PayPay, cfg, args) -> int:
    """BFF で通らないトークン用。Web 版で出来ることだけ確認する。"""
    print("=" * 70)
    print("2. 実アカウントでのテスト（Web 版 API）")
    print("=" * 70)
    print("BFF(app4) では通らないトークンなので、Web 版で叩ける範囲だけ確認する。")
    print("全部やりたければ --browser-login で BFF 側のトークンを取る。\n")

    web = web_client(pp)
    r = live_check.Runner()

    def profile():
        me = web.get_profile()
        if not me.external_user_id:
            raise AssertionError(f"externalUserId が取れない: {dict(me)}")
        return me, f"{me.name} / {me.external_user_id}"

    r.check("get_profile", profile)

    def balance():
        b = web.get_balance()
        return b, (f"money={b.money} light={b.money_light} point={b.points} "
                   f"all={b.all_balance} usable={b.useable_balance}")

    r.check("get_balance", balance)

    def history():
        h = web.get_history()
        items = h.get("transactions") or h.get("historyList") or h.get("items") or []
        return h, f"{len(items)} 件（キー: {', '.join(list(h)[:4]) or 'なし'}）"

    r.check("get_history", history)

    if cfg["link"]:
        def link_check():
            info = web.link_check(cfg["link"])
            return info, (f"amount={info.amount} status={info.status} "
                          f"from={info.sender_name} passcode={info.has_password}")
        r.check("link_check", link_check)
    else:
        r.skip("link_check", "CONFIG['link'] に送金リンクを入れると確認する")

    def p2pcode():
        code = web.create_p2pcode()
        if not code.p2pcode:
            raise AssertionError(f"p2pCode が取れない: {dict(code)}")
        return code, str(code.p2pcode)

    r.check("create_p2pcode", p2pcode)

    r.skip("create_paymentcode", "paymentMethodId がアカウント固有なので自動確認しない")

    if not cfg["link"]:
        r.skip("link_receive", "CONFIG['link'] に受け取りたいリンクを入れる")
    elif not (args.receive or cfg.get("receive")):
        r.skip("link_receive", "--receive（か CONFIG['receive']=True）で実行。取り消せない")
    else:
        def receive():
            info = web.link_check(cfg["link"])
            if info.status and info.status != "PENDING":
                raise AssertionError(f"もう {info.status} なので受け取れない")
            if not (args.yes or confirm_receive(info)):
                raise AssertionError("確認でキャンセルした")
            passcode = cfg["link_passcode"] or None
            out = web.link_receive(cfg["link"], passcode, link_info=info)
            after = web.link_check(cfg["link"])
            return out, (f"{info.amount} 円 受け取り完了"
                         f"（{info.status} → {after.status}）")
        r.check("link_receive", receive)

    r.skip("link_reject", "受け取りと排他なので自動確認しない（web.link_reject で辞退できる）")
    for name in ("create_link", "send_money", "link_cancel", "send_message",
                 "search_p2puser", "get_chat_rooms", "pay_qr_code",
                 "cashout_to_paypaybank"):
        r.skip(name, "Web 版 API に無い（BFF のトークンが要る）")

    return r.report()


def main() -> int:
    p = argparse.ArgumentParser(description="pypaypay を丸ごとテストする",
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--relogin", action="store_true",
                   help="保存済みトークンを使わずログインからやり直す")
    p.add_argument("--browser-login", action="store_true",
                   help="OTP ではなく BFF の PAR フロー（ブラウザで通して callback URL を貼る）")
    p.add_argument("--receive", action="store_true",
                   help="CONFIG['link'] のリンクを実際に受け取る（取り消せない）")
    p.add_argument("--no-write", action="store_true", help="お金が動くテストを飛ばす")
    p.add_argument("--yes", action="store_true", help="お金が動くテストの確認を飛ばす")
    p.add_argument("--strict", action="store_true",
                   help="NG があったら終了コード 1 を返す（CI 用。既定は常に 0）")
    args = p.parse_args()

    problems: list[str] = []

    pp = get_client(CONFIG, args)
    if pp is None:
        problems.append("ログインできなかった（テストは走っていない）")
    else:
        try:
            if getattr(pp, "bff_ok", True):
                failed = run_live_tests(pp, CONFIG, args)
            else:
                failed = run_web_tests(pp, CONFIG, args)
        finally:
            pp.close()
        if failed:
            problems.append(f"NG が {failed} 件（上のリストの NG 行を見て）")

    print("=" * 70)
    if problems:
        print("まとめ: " + " / ".join(problems))
    else:
        print("まとめ: ぜんぶ OK")
    print("=" * 70)

    return 1 if (problems and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
