# pypaypay

PayPay の非公式 Python API ラッパーだよ
**高レベル 28 メソッド / raw 193 エンドポイント** — アプリで出来ることはだいたい出来ると思う。

## インストール

```py
pip install pypaypay
```

依存は `httpx` だけ、軽いでしょ

###### インストール名も import 名も `pypaypay`
```py
from pypaypay import PayPay
```

最新版を直で入れたい人はこっち：

```py
pip install git+https://github.com/amane1201/pypaypay
```

ローカルで弄りたい人はこっち：

```py
git clone https://github.com/amane1201/pypaypay
cd pypaypay
pip install -e .
```

## 始める前に確認すること

### これは非公式です
PayPay 株式会社とは縁もゆかりもありません、中の人でもなんでもない。
非公式 API を叩くのは規約的にたぶんアウトなので、**自分のアカウントで、自己責任で**遊んでね。
凍結されても「どんまい」って一緒に言うことしか出来ないよ。

### ログイン失敗は3回まで
超えるとアカウントが一時ロックされる。解除はサポート送りなので、パスワードうろ覚えのまま試行錯誤するのは本当にやめとけ。3回だぞ、3回。

### セッションを作りすぎない
毎回ログインし直すとセッションが積み上がってアカウント凍結の可能性があるっぽい。
**トークンを保存して使い回して**、それだけで寿命が伸びる。

### 日本からしかアクセスできない
海外の VPS からだと普通に弾かれるので、その時はプロキシ挿して。

### Bot 検知がいるらしい
どうやらモバイル API には Bot 検知が存在するっぽくて、引っかかると勝手にログアウトさせられる。
無駄なリクエストを混ぜると回避できるらしい（人間がアプリ触ってたら当然そこそこリクエストするので、それを真似る）。
このモジュールなら `paypay.raw.get_user_profile()` あたりを時々叩いとけばそれっぽくなる。Bot は効率が良いから怪しまれるんだね……。

## Let's Go!

#### example.py

```py
from pypaypay import PayPay

# ① 電話番号＋パスワードで初回ログイン
paypay = PayPay("080-1234-5678", "Gay1919")   # ハイフンはあってもなくてもいい
url = paypay.login()                            # ブラウザで開く URL が返ってくる（約60秒で失効、すぐ開け）
print("これ開いて:", url)
paypay.login_confirm(input("URL?: "))           # コールバック URL そのままでも AB-0000 みたいなのだけでも OK

print(paypay.access_token)      # 90日有効、これを保存しろ
print(paypay.refresh_token)     # これも保存しろ、こっちの方が大事まである
print(paypay.device_uuid)       # 登録デバイス管理用、次回これ渡すと URL 入力を省ける
print(paypay.client_uuid)       # 特に気にしなくていい、ランダムでいいらしい

# ② 2回目以降はトークンぶち込んでログイン作業まるごとスキップ
paypay = PayPay(access_token="トークン", refresh_token="リフレッシュ")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# プロフィールと残高
me = paypay.get_profile()
print(me.name)                  # ユーザー名
print(me.external_user_id)      # 識別用の内部 ID、自分で決めた PayPayID とは別物
print(me.icon)                  # アイコンの URL

bal = paypay.get_balance()
print(bal.all_balance)          # ぜんぶ
print(bal.useable_balance)      # 使える分（ポイント抜き）
print(bal.money_light, bal.money, bal.points)   # ライト / マネー / ポイント

# 履歴とか DM 一覧とか
paypay.get_history(size=20)                     # 支出入の履歴、size は控えめでいい
paypay.get_chat_rooms(size=20)                  # PayPay 内 DM 一覧
paypay.get_chat_room_messages("sendbird_group_channel_なんとか_なんとか")
# ↑ "sendbird_group_channel_" は付けても付けなくても OK、そこは優しい
paypay.get_point_history()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 送金リンク、みんなこれ目当てでしょ
link = paypay.link_check("https://pay.paypay.ne.jp/Zk8mQ2vR7pL4xN3d")  # ID だけでも OK
print(link.amount)              # 合計金額
print(link.money_light, link.money)             # 内訳
print(link.has_password)        # True ならパスワード必須
print(link.chat_room_id)        # 受け取ったあとお礼 DM 送るやつ
print(link.status)              # PENDING / COMPLETED / REJECTED / FAILED
print(link.order_id)
print(link.sender_external_id)  # 送ってきた人の ExternalID

paypay.link_receive("URL / ID どっちでもOK", "必要ならパスワード 1919", link_info=link)
# ↑ link_info を渡すとリンクチェックをスキップするので速い、連打する人は必ず渡せ
paypay.link_reject("URL / ID どっちでもOK", link_info=link)   # 辞退
paypay.link_cancel("URL / ID どっちでもOK", link_info=link)   # 自分が送ったやつの取り消し

# リンク発行
created = paypay.create_link(amount=100, passcode="1919")
print(created.link)             # ↑で作った URL
print(created.chat_room_id)     # ↑で作ったリンクのチャットルーム ID
print(created.order_id)

# 自分宛て入金 QR
qr = paypay.create_p2pcode()    # amount=int で金額固定も出来る
print(qr.p2pcode)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 直接送金と DM
send = paypay.send_money(amount=100, receiver_id="友達の external_user_id")
print(send.chat_room_id)
paypay.send_message(send.chat_room_id, "はい100円")
# ここにテンプレ文を流し込めば受け取り連絡が完全自動になる

paypay.set_money_priority(paypay_money=False)   # False=ライト優先 / True=マネー優先

# ユーザー検索 → チャットルーム
user = paypay.search_p2puser("amane1201")                    # PayPayID でグローバル検索
user = paypay.search_p2puser("あまね", is_global=False, order=0)  # フレンドなら表示名でも
print(user.name, user.icon, user.external_user_id)
room = paypay.initialize_chatroom(user.external_user_id)
paypay.send_message(room.chatroom_id, "テスト")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 加盟店 QR と出金
info = paypay.get_barcode_info("https://qr.paypay.ne.jp/............")
print(info.amount)              # 金額指定なしの請求リンクだと None
print(info.merchant_name)
print(info.external_user_id)    # send_money の receiver_id に流用できる

paypay.pay_qr_code("https://qr.paypay.ne.jp/............")   # amount=int で金額指定も
paypay.cashout_to_paypaybank(100)                           # PayPay 銀行へ出金
```

長いけど使い方はコメントに全部書いといたから、ここだけ読めばだいたい動かせる。

### dict 探し地獄からの卒業

返り値は全部 `dict` のサブクラス。よく使うやつは `.属性` で取れるようにしてあるので、
`payload["walletSummary"]["usableBalance"]["moneyLight"]["amount"]` みたいな**深すぎる階層をスコップで掘る作業**はもう要らない。

```py
me = paypay.get_profile()
me.name          # -> 属性アクセス（欲しいやつはだいたいこれで出る）
me["nickName"]   # -> dict アクセス（生キー）
me.raw           # -> {...} フル dict、生で見たい時用
```

無い属性は例外じゃなく `None` を返すので `if me.icon:` で普通に判定できる。優しい。

## 全部叩ける — `paypay.raw`

高レベルに無いエンドポイントも `paypay.raw.<メソッド名>` で **193 本ぜんぶ**呼べる。
パラメータ名はデコンパイル済のソースから機械抽出したのがキーワード引数で並ぶので IDE 補完が効く。

```py
# BFF 系
paypay.raw.get_user_profile(includeUserScore=True)
paypay.raw.get_kyc_display_info(requestKycTypes=["IDENTIFICATION"])
paypay.raw.get_gv_list(statusFilter="ACTIVE", pageSize=20)
paypay.raw.follow_channel(channelId="xxxx", type="STORE")
paypay.raw.like_feed(feedId="yyyy")

# P2P 系（グループ機能とか割り勘とか）
paypay.raw.create_group_pay()
paypay.raw.get_p2p_friends(pageSize=50)
paypay.raw.block_user(externalUserId="...")

# 抽出漏れフィールドは **extra で足せる、アプリが更新されても待たなくていい
paypay.raw.change_user_profile(nickName="太郎", **{"someNewField": True})
```

全メソッド一覧が欲しかったら：

```py
python -c "from pypaypay.raw import RawAPI; print('\n'.join(sorted(m for m in dir(RawAPI) if not m.startswith('_'))))"
```

`help(paypay.raw.get_gv_list)` すれば元のエンドポイントが docstring に書いてある。迷ったら叩け。

## もう少し詳しく

### ログインは2系統ある

PayPay には API が2つあって、ログインの通し方も別。

| | Web 版 | BFF |
|---|---|---|
| ホスト | `www.paypay.ne.jp/app` | `app4.paypay.ne.jp` |
| ログイン | **メアパス → OTP を入力** | PAR → ブラウザのポータル → callback URL |
| 認証 | `Cookie: token=...` | `Authorization: Bearer ...` |
| クラス | `WebPayPay` | `PayPay` |
| 出来ること | 残高・履歴・リンク受取など一部 | 高レベル 28 + raw 193 ぜんぶ |

高レベル API 28 メソッドと `raw` 193 本は **BFF 向け**。アプリ 5.x がログイン画面を
Web ポータルに丸投げした結果、BFF 側には OTP を検証するエンドポイントがもう無い。
そして **OTP で取れるのは Web 版のトークンで、BFF では通らない**（実機で確認済み）。
つまり「OTP でログインしたい」なら、使えるのは Web 版で叩ける範囲に限られる。

### OTP でログインする（`WebPayPay`）

```py
from pypaypay import WebPayPay

paypay = WebPayPay("08012345678", "パスワード")
if paypay.login()["otp_required"]:     # ここで SMS / メールに OTP が飛ぶ
    paypay.login_otp(input("OTP: "))   # 届かなければ paypay.resend_otp()

print(paypay.access_token)
print(paypay.get_balance().all_balance)
```

`WebPayPay` で使えるのはこれだけ。メソッド名と戻り値は `PayPay` と揃えてあるので、
この範囲なら書き換えずに差し替えられる。

| 使える | 使えない（Web 版 API に無い） |
|---|---|
| `get_profile` `get_balance` `get_history` | `create_link`（リンク発行） |
| `link_check` `link_receive` `link_reject` | `send_money` `send_message` |
| `create_p2pcode` `create_paymentcode` | `link_cancel` `search_p2puser` ほか |

使えない方を呼ぶと通信せずに `APIError(E_WEB_UNSUPPORTED)` で止まる。
**リンク発行や直接送金がしたいなら BFF のトークンが要る**ので、`PayPay.login()` の
ブラウザ方式（下）で取ること。

### ログインのやり方いろいろ

```py
# ① 電話番号＋パスワード（一番普通、ワンタイム URL を踏む）
paypay = PayPay("080-1234-5678", "Gay1919")
paypay.login_confirm(input(paypay.login() + " ← 開いて、戻ってきた URL: "))

# ② 登録済みデバイス UUID がある（URL 入力を省ける）
paypay = PayPay("080-1234-5678", "Gay1919", "登録済みのデバイスUUID", proxy=None)
paypay.login()

# ③ トークンだけ持ってる（ログイン作業まるごとスキップ）
paypay = PayPay(access_token="...", refresh_token="...")

# 手動でリフレッシュしたい時はこれ
paypay.token_refresh("ここにリフレッシュトークン")
print(paypay.access_token)   # ← 更新後のやつが入ってる
print(paypay.refresh_token)
```

`refresh_token` を渡してあると **401 が来たら勝手に叩き直してリトライしてくれる**ので、初回だけ通せば長期間放置できる。えらい。

1アカウント分の身分証は 電話番号 / パスワード / Device_UUID / Client_UUID / アクセストークン / リフレッシュトークン の6点セット。
このうち実際に握っとくべきなのは**アクセストークンとリフレッシュトークンと Device_UUID** の3つで、DB に書き込むならこの3つ。
アクセストークンは **90日** 有効なので、一度通せばしばらく忘れてても動いてる。

###### 電話番号のハイフンはあってもなくても OK
クライアント UUID は常にランダムでいいみたい。アクセストークンをぶち込んでる場合はデバイス UUID もランダムでいいみたい。適当。

### 設定いろいろ

```py
paypay = PayPay(
    access_token="...",
    proxy="127.0.0.1:8888",   # str なら http:// は省略可、dict でもいける
    timeout=20,
    sandbox=False,            # True で stg 環境に向く（使う機会たぶん無い）
)
```

### PayPay の DM

送金・受け取り履歴のところに生えてるチャット。取引で絡んだ相手にだけ喋れる仕様。
リンクチェックすると DM 送信用のチャットルーム ID が付いてくるので、受け取ったら勝手にお礼を投げる、みたいなのが組める。
納品物の詳細を流すもよし、雑に一言だけ返すもよし。無言で回収するより印象は良い。

ID は `sendbird_group_channel_なんとか_なんとか` の形式だけど、`send_message` に渡す時は `sendbird_group_channel_` の部分は無くても OK。

#### もう少し効率化

チャットルーム ID がリンクチェック時しか貰えないのはつらいけど、検索と組み合わせれば何とかなる：

```py
user = paypay.search_p2puser("amane1201")                 # PayPayID で検索
room = paypay.initialize_chatroom(user.external_user_id) # チャットルーム ID を取得
paypay.send_message(room.chatroom_id, "テスト")           # 送信
```

表示名で探す場合は `is_global=False`（表示名検索はフレンドしか出てこない）。
逆にフレンド検索に PayPayID は使えない（NotFound が返る）。統一しろ。

ただし**ユーザー ID 検索はすぐレート制限に入る**ので、連打前提の運用には向かない。基本はリンク受け取り時に降ってくる ID を使って、検索は最後の手段くらいの気持ちで。

#### もちろん DM じゃなく直接送金も出来る

```py
user = paypay.search_p2puser("あまね")
paypay.send_money(100, user.external_user_id)
```

送金は ExternalID だけで済むので、DM より簡単。金だけ投げるのは簡単ってコト。

## エラー

失敗したら例外が飛ぶ。種類で分けて掴まえられるよ：

```py
from pypaypay import APIError, TokenExpiredError, RateLimitedError, LinkAlreadyClaimed

try:
    paypay.link_receive("Zk8mQ2vR7pL4xN3d")
except LinkAlreadyClaimed:
    print("誰かに先を越された")
except RateLimitedError:
    print("落ち着け")
except TokenExpiredError:
    print("トークン死んだ、refresh して")
except APIError as e:
    print("なんか失敗:", e.status, e.code, e.payload)
```

```
PayPayError
├── AuthError
│   └── TokenExpiredError          # 401 / トークン失効 / S0001
├── APIError                       # BFF が resultCode != S0000
│   ├── .status                    #   HTTP ステータス
│   ├── .code                      #   BFF の resultCode
│   └── .payload                   #   レスポンス全文（困ったらこれ print）
├── RateLimitedError               # 429
├── LinkPasscodeRequired           # 受取パスコード必須
└── LinkAlreadyClaimed             # 受取 / 拒否済み
```

処理済みのリンクや無効なリンクを触るとちゃんとエラーにしてあるので、握りつぶさず判別に使って。

## トークンをどう手に入れるか

`login()` → `login_confirm()` で普通に取れる。それが面倒なら：

- **mitmproxy 派**：PayPay アプリのログイン通信を横取りして `bff/v2/oauth2/token` のレスポンスから抜く
- **API 手組み派**：`paypay.raw.oauth2_par(...)` → SMS OTP → `paypay.raw.oauth2_token(...)` を自前で組む（PKCE 必要）

どの道 `refresh_token` さえ生きてれば以後は自動更新なので、初回さえ突破すれば勝ち。

## 動作確認

### メアパスを入れるだけ

[scripts/test_everything.py](scripts/test_everything.py) の頭にある `CONFIG` に
メアド(or 電話番号)とパスワードを書いて、実行するだけ。

```py
py -3 scripts/test_everything.py
```

1. ログイン（**メアパス → OTP が届く → 打ち込む**、ブラウザは開かない）
2. 取れたトークンを `paypay_session.json` に保存（次回以降はログイン不要）
3. 読み取り系ぜんぶ（プロフィール / 残高 / 履歴 / DM / 検索 / リンク解析）
4. 1円の送金リンクを作って → 解析 → DM → キャンセル（お金は戻る、`CONFIG["write"]` で切れる）

OTP で取れるのは Web 版のトークンなので、ログイン直後に
**そのトークンが BFF 側でも通るか**をプローブして表示する。通らなければ Web 版で
叩ける範囲だけ確認する。全部やりたいなら `--browser-login` で BFF 側の PAR フロー
（ブラウザで通して callback URL を貼る）に切り替え。

`CONFIG` を空にしておけば環境変数 `PAYPAY_ID` / `PAYPAY_PASSWORD` から読むので、
パスワードをファイルに残さずに済む。`paypay_session.json` は `.gitignore` 済み。

```py
py -3 scripts/test_everything.py --receive        # CONFIG["link"] を実際に受け取る
py -3 scripts/test_everything.py --no-write       # お金が動くやつを飛ばす
py -3 scripts/test_everything.py --relogin        # 保存済みトークンを捨ててやり直す
py -3 scripts/test_everything.py --browser-login  # BFF 側のトークンを取りに行く
```

受け取りは取り消せないので `--receive`（か `CONFIG["receive"]=True`）が要る。
実行前に金額と送り主を出して確認を取る。

### トークンだけ持ってる場合

```py
# 読み取りだけ（残高・履歴・プロフィール・リンク解析）
py -3 scripts/live_check.py --token <アクセストークン>

# リンク解析とユーザー検索も一緒に
py -3 scripts/live_check.py --token <AT> --link <送金リンク> --user-id <PayPayID>

# 1円の送金リンクを作って→解析して→チャット送って→キャンセル（お金は戻る）
py -3 scripts/live_check.py --token <AT> --write --amount 1
```

お金が動くのは `--write` を付けて確認プロンプトに yes と答えたときだけ。
`pay_qr_code` / `send_money` / `cashout_to_paypaybank` は相手か店舗が必要で
取り消せないので、自動確認からは外してある。

## 余談：どうやって作ったか

APK を [JADX](https://github.com/skylot/jadx) でデコンパイルして、ひたすら読んだ。

- `HeaderInterceptor` 相当のところ → 送ってるヘッダー、`Client-UUID` / `Device-UUID` / `Client-OS-Version` の作り方が丸見えだった
- BFF の実装クラス（難読化後は `C19344p` みたいな味気ない名前）→ **192 本のエンドポイントとパラメータ名が全部そこ**にあった
- OAuth2 の client_id は本番用と sandbox 用が定数で埋まってた、いいの？それで

難読化でメソッド名は潰れてるけどエンドポイント文字列とフィールド名は生で残ってるので、そこを正規表現でさらって `pypaypay/raw.py` を自動生成してる。機械生成なのでメソッド名がちょっとダサいのは勘弁。

アプリのバージョンが変わったら、新しい APK をデコンパイルして：

```py
py -3 scripts/extract_endpoints.py       # BFFImpl から endpoint → param 抽出
py -3 scripts/codegen.py                 # pypaypay/raw.py を再生成
```

パスが違うなら `PAYPAY_BFF_SRC=/path/to/BFFImpl.java` を頭に付けて。
デコンパイルしたのは jp.ne.paypay 5.49.0 (Android)、User-Agent もそれに合わせてある。

## さらに余談

なんで pypaypay なの？って思った？実は深い理由が……無い。py + PayPay で pypaypay、以上。
本当は `paypy` にしたかったんだけど、PyPI の `paypy` は 2012年で時が止まってる別人の遺跡が居座ってて取れなかった。14年前の決済ゲートウェイに負けた。
読み方は「ペイパイ」でも「ペイピー」でも好きにしてくれ。作者も日によって変わる。

## コンタクト / 貢献

バグとか「このメソッド動かんぞ」は GitHub の Issues に投げて。
PR も歓迎、エンドポイント追加はスクリプト再生成なので気軽にどうぞ。
discord idは am6e

## ライセンス

MIT — [LICENSE](LICENSE) 見て好きに使っていいよ。
PayPay の商標とかサービス自体は当然 PayPay 株式会社のもの、このライブラリは無関係の第三者製です。
