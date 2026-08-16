"""BFF ログイン（PAR → ブラウザ → callback）を実アカウントで通すテスト。

``paypay://`` を HKCU に一時登録して、ブラウザから戻ってくるコールバック URL を
自動で拾う。終わったら登録は消す（``--keep`` で残せる）。

    py -3 scripts/test_bff_login.py --phone 08012345678

パスワードは引数で渡さず、聞かれてから入力する（履歴に残さないため）。
"""
from __future__ import annotations

import argparse
import getpass
import json
import sys
import time
import webbrowser
import winreg
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# VS Code のターミナルは UTF-8 なのに Windows の Python は cp932 で書くので化ける
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

from pypaypay import PayPay                                   # noqa: E402
from pypaypay.exceptions import APIError, AuthError           # noqa: E402

HANDLER = Path(__file__).with_name("catch_callback.py")
CALLBACK_FILE = Path(__file__).with_name(".callback.txt")
SCHEME = "paypay"
KEY = rf"Software\Classes\{SCHEME}"


# ----------------------------------------------------------------------
# paypay:// ハンドラの登録 / 解除
# ----------------------------------------------------------------------
def handler_command() -> str:
    """コンソールを出さない pythonw があればそっちを使う。"""
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else exe
    return f'"{runner}" "{HANDLER}" "%1"'


def already_registered() -> bool:
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY).Close()
        return True
    except FileNotFoundError:
        return False


def register() -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY) as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "URL:PayPay Protocol")
        winreg.SetValueEx(k, "URL Protocol", 0, winreg.REG_SZ, "")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY + r"\shell\open\command") as k:
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, handler_command())


def unregister() -> None:
    for sub in (r"\shell\open\command", r"\shell\open", r"\shell", ""):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, KEY + sub)
        except FileNotFoundError:
            pass


# ----------------------------------------------------------------------
def wait_for_callback(timeout: float) -> str | None:
    """ハンドラが書き出す .callback.txt を待つ。手で貼りたい人向けに Enter も見る。"""
    deadline = time.monotonic() + timeout
    print(f"\nコールバック待ち（最大 {int(timeout)} 秒）… "
          f"ブラウザで「開きますか?」が出たら『開く』を押してください")
    print("（自動で拾えなかったら Ctrl+C → URL を手で貼り付け）")
    while time.monotonic() < deadline:
        if CALLBACK_FILE.exists():
            url = CALLBACK_FILE.read_text(encoding="utf-8").strip()
            if url:
                CALLBACK_FILE.unlink(missing_ok=True)
                return url
        time.sleep(0.4)
    return None


def mask(s: str | None, keep: int = 6) -> str:
    if not s:
        return "(なし)"
    return f"{s[:keep]}…{s[-4:]} (len={len(s)})"


def probe(pp: PayPay) -> None:
    """取れたトークンが本当に BFF で通るか叩いて確かめる。"""
    print("\n--- BFF 疎通確認 ---")
    checks = [
        ("get_profile", lambda: pp.get_profile().name),
        ("get_balance", lambda: pp.get_balance().all_balance),
        ("get_history", lambda: len(pp.get_history(size=3).raw)),
        ("raw.get_user_profile", lambda: type(pp.raw.get_user_profile()).__name__),
    ]
    for name, fn in checks:
        try:
            print(f"  {name:22} OK  -> {fn()!r}")
        except (APIError, AuthError) as e:
            print(f"  {name:22} NG  -> {type(e).__name__}: {e}")

    print("\n--- リフレッシュ確認 ---")
    if not pp.refresh_token:
        print("  refresh_token が無いのでスキップ")
        return
    old = pp.access_token
    try:
        pp.token_refresh()
        print(f"  token_refresh          OK  -> access_token {'更新された' if pp.access_token != old else '同じ値が返った'}")
        print(f"  再度 get_profile       OK  -> {pp.get_profile().name!r}")
    except (APIError, AuthError) as e:
        print(f"  token_refresh          NG  -> {type(e).__name__}: {e}")


# ----------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phone", help="電話番号（省略時は聞く）")
    ap.add_argument("--device-uuid", help="登録済みデバイス UUID があれば")
    ap.add_argument("--proxy", help="http://127.0.0.1:8080 とか（mitm で覗きたい時）")
    ap.add_argument("--timeout", type=float, default=300.0, help="コールバック待ち秒数")
    ap.add_argument("--keep", action="store_true", help="テスト後も paypay:// 登録を残す")
    ap.add_argument("--manual", action="store_true",
                    help="レジストリを触らず、URL を手で貼り付ける")
    ap.add_argument("--save", metavar="PATH", help="取れたトークンを JSON で保存")
    args = ap.parse_args()

    phone = args.phone or input("電話番号: ").strip()
    password = getpass.getpass("パスワード（表示されません）: ")

    created = False
    if not args.manual:
        if already_registered():
            print(f"paypay:// は既に登録済み。上書きせずそのまま使います")
        else:
            register()
            created = True
            print(f"paypay:// を HKCU に登録しました -> {handler_command()}")

    CALLBACK_FILE.unlink(missing_ok=True)
    pp = PayPay(phone, password, args.device_uuid, proxy=args.proxy)

    try:
        # --- ① PAR ---
        url = pp.login()
        print("\n--- ① oauth2/par ---")
        print(f"  request_uri : {pp._request_uri}")
        print(f"  expiresIn   : {pp._request_uri_expires_in} 秒")
        print(f"  開く URL    : {url}")

        # --- ② ブラウザ ---
        if args.manual:
            callback = input("\nログイン後の paypay://... を貼り付け: ").strip()
        else:
            print("\n--- ② ブラウザ ---")
            webbrowser.open(url)
            callback = wait_for_callback(args.timeout)
            if not callback:
                print("  タイムアウト。URL を手で貼るなら下にどうぞ（Enter で中止）")
                callback = input("  paypay://...: ").strip()
        if not callback:
            print("中止しました")
            return 1
        print(f"  受け取った callback: {callback[:60]}…")

        # --- ③ token 交換 ---
        print("\n--- ③ oauth2/token ---")
        pp.login_confirm(callback)
        print(f"  access_token  : {mask(pp.access_token)}")
        print(f"  refresh_token : {mask(pp.refresh_token)}")
        print(f"  device_uuid   : {pp.device_uuid}")
        print(f"  client_uuid   : {pp.client_uuid}")

        probe(pp)

        if args.save:
            Path(args.save).write_text(json.dumps({
                "access_token": pp.access_token,
                "refresh_token": pp.refresh_token,
                "device_uuid": pp.device_uuid,
                "client_uuid": pp.client_uuid,
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\nトークンを {args.save} に保存しました（.gitignore 済みの場所に置いて）")

        print("\n=> BFF ログイン成功")
        return 0

    except (AuthError, APIError) as e:
        print(f"\n=> 失敗: {type(e).__name__}: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n中断しました")
        return 130
    finally:
        pp.close()
        CALLBACK_FILE.unlink(missing_ok=True)
        if created and not args.keep:
            unregister()
            print("paypay:// の登録を解除しました")
        elif created:
            print(f"paypay:// の登録は残してあります（消すなら: "
                  f"reg delete HKCU\\Software\\Classes\\{SCHEME} /f）")


if __name__ == "__main__":
    raise SystemExit(main())
