"""``paypay://`` プロトコルハンドラの実体。

ブラウザが ``paypay://oauth2/callback?code=...`` を開こうとした時に Windows から
起動され、渡された URL を隣の ``.callback.txt`` に書き出すだけのスクリプト。
登録 / 解除は :mod:`test_bff_login` がやる。
"""
import sys
from pathlib import Path

OUT = Path(__file__).with_name(".callback.txt")


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        OUT.write_text(url, encoding="utf-8")
    except Exception as e:  # ハンドラ側で落ちても呼び出し元に出せないのでログに残す
        Path(__file__).with_name(".callback.err").write_text(repr(e), encoding="utf-8")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
