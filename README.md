# paypy

非公式 PayPay Python ラッパー。名前は「ペイパイ」でも「ペイピー」でも好きに呼んで。

APK を jadx でカチ割って BFF (`app4.paypay.ne.jp`) の仕様を機械抽出したので、**エンドポイント 192 本 全部叩ける**。

> ⚠️ 公式じゃないし公式サポートも無い。ToS 違反な自動化に使ったら普通に凍結されるので、**自分の口座に対する研究・自動化専用**にしてね。垢banされたら「どんまい」くらいしか言えないよ。

## インストール

```bash
# GitHub から直接(推奨)
pip install git+https://github.com/amane1201/paypy

# ローカルで開発するなら
git clone https://github.com/amane1201/paypy
cd paypy
pip install -e .

```

## ログインまわり


```python
from paypy import PayPay

# 1) 電話番号 + パスワードで新規デバイスログイン
paypay = PayPay("090-1234-5678", "Gay1919")  # ハイフンはあってもなくてもいい
url = paypay.login()                            # portal URL が返ってくる
print("これブラウザで開いて:", url)
paypay.login_confirm(input("URL?: "))            # コールバック URL でも AN-1201 だけでも OK
print(paypay.access_token)                      # 90 日生きるやつ
print(paypay.refresh_token)
print(paypay.device_uuid)                       # 登録デバイス管理用
print(paypay.client_uuid)                       # 特に気にしなくていい

# 2) 登録済みデバイス UUID を渡す(2 回目以降は URL 入力を省ける)
paypay = PayPay("080-1234-5678", "Gay1919", "登録済みのデバイスUUID", proxy=None)
paypay.login()
print(paypay.access_token)
# URL の入力は要らない

# 3) アクセストークンだけ持ってるならログインまるごとスキップ
paypay = PayPay(access_token="アクセストークン")

# 90 日経ってトークン切れたら refresh
paypay.token_refresh("ここにリフレッシュトークン")
print(paypay.access_token)   # ← 更新後のやつが入ってる
print(paypay.refresh_token)
```

`proxy` は `dict` でも `str` でもいける。`str` は `http://` 省略可(`"host:8080"` でも OK)。
`refresh_token` があれば 401 くらったとき勝手に叩き直してリトライしてくれる。

## プロフィール / 残高

```python
me = paypay.get_profile()
print(me.name)                # ユーザー名
print(me.external_user_id)    # 内部 ID(PayPayID とは別物)
print(me.icon)                # アイコン URL

bal = paypay.get_balance()
print(bal.all_balance)        # ぜんぶ
print(bal.useable_balance)    # 使える分
print(bal.money_light)        # マネーライト
print(bal.money)              # マネー
print(bal.points)             # ポイント
```

## 履歴 / チャット / 通知

```python
paypay.get_history(size=20)                                       # 支出入履歴
paypay.get_chat_rooms(size=20)                                    # PayPay 内 DM 一覧
paypay.get_chat_room_messages(chat_room_id="sendbird_group_channel_xxx_yyy")
# ↑ "sendbird_group_channel_" は付けても付けなくても OK
paypay.get_point_history()
```

## 送金リンク

一番よく使うやつ。

```python
# 情報だけ見る(web=True で公開 API 経由)
info = paypay.link_check("https://pay.paypay.ne.jp/KT975hvzbH1EulTr")
print(info.amount)         # 合計金額
print(info.money_light)    # ライト分
print(info.money)          # マネー分
print(info.has_password)   # True ならパスワード必須
print(info.chat_room_id)   # 受取後にメッセ送るあれ
print(info.status)         # PENDING / COMPLEATED / REJECTED / FAILED
print(info.order_id)

# 受取
paypay.link_receive("URLでもIDでも", "パスワード必要なら 4602", link_info=info)
# ↑ link_info を渡すと再チェックしないので速い

paypay.link_reject("URLでもIDでも", link_info=info)   # 辞退
paypay.link_cancel("URLでもIDでも", link_info=info)   # 自分が送ったやつ取消(やっと出来るようになった)

# 発行
create_link = paypay.create_link(amount=100, passcode="4602")
print(create_link.link)          # URL
print(create_link.chat_room_id)  # 発行時に付くチャットルーム

# 自分宛て入金 QR
qr = paypay.create_p2pcode()             # 金額指定するなら amount=int
print(qr.p2pcode)
```

## 直接送金 / DM

リンクじゃなく相手 ID を直接指定する版。

```python
send = paypay.send_money(amount=100, receiver_id="受取人のexternal_user_id")
print(send.chat_room_id)

paypay.send_message(chat_room_id="DMのID", message="100円くれてありがとう!")
# 商用ならここに「お買い上げありがとうございます」的なテンプレを流し込むと捗る

paypay.set_money_priority(paypay_money=False)   # False=マネーライト優先 / True=マネー優先
```

## ユーザー検索 / チャット初期化

```python
# PayPayID でグローバル検索(すぐレート制限に入るので連打注意)
u = paypay.search_p2puser(user_id="ユーザーID")
print(u.name, u.icon, u.external_user_id)

# フレンド内なら表示名でも探せる。同名がいたら order で n 番目を取る
u = paypay.search_p2puser(user_id="表示名", is_global=False, order=0)
print(u.icon, u.external_user_id)

# ExternalID から DM 用チャットルームを取得
room = paypay.initialize_chatroom("ExternalID")
print(room.chatroom_id)
```

## 加盟店 QR / 出金

```python
info = paypay.get_barcode_info("https://qr.paypay.ne.jp/............")
print(info.amount)             # 金額指定なしの請求リンクだと None
print(info.external_user_id)   # send_money の receiver_id に流用できる

paypay.pay_qr_code(url)                # QR 決済実行
paypay.cashout_to_paypaybank(100)      # PayPay 銀行へ出金
```

## 全 API 網羅 — `pp.raw`

高レベルに無いエンドポイントも **192 個全部** `paypay.raw.<method>` で呼べる。パラメータ名は decompile 済のソースから自動抽出したやつが keyword-only で並ぶので IDE 補完が効く。

```python
# BFF 系
paypay.raw.get_user_profile(includeUserScore=True)
paypay.raw.get_kyc_display_info(requestKycTypes=["IDENTIFICATION"])
paypay.raw.get_gv_list(statusFilter="ACTIVE", pageSize=20)
paypay.raw.follow_channel(channelId="xxxx", type="STORE")
paypay.raw.like_feed(feedId="yyyy")

# P2P 系(グループ機能とか、割り勘とか)
paypay.raw.create_group_pay(...)
paypay.raw.get_p2p_friends(pageSize=50)
paypay.raw.block_user(externalUserId="...")

# 抽出漏れフィールドは **extra で足せる
paypay.raw.change_user_profile(nickName="太郎", **{"someNewField": True})
```

全メソッド一覧が欲しかったら:
```bash
python -c "from paypy.raw import RawAPI; print('\n'.join(sorted(m for m in dir(RawAPI) if not m.startswith('_'))))"
```

## レスポンスの触り方

戻り値は全部 `dict` のサブクラス。`.attr` でも `["key"]` でも読めるし、生 dict は `.raw` で拾える。

```python
me = paypay.get_profile()
me.name          # -> 属性アクセス
me["nickName"]   # -> dict アクセス(生キー)
me.raw           # -> {...} フル dict
```

無い属性は例外じゃなく `None` を返すので `if me.icon:` で普通に判定できる。

## 例外

```
PayPayError
├── AuthError
│   └── TokenExpiredError          # 401 / トークン失効
├── APIError                       # BFF が resultCode != S0000
│   ├── .status                    #   HTTP ステータス
│   ├── .code                      #   BFF resultCode
│   └── .payload                   #   レスポンス全文
├── RateLimitedError               # 429
├── LinkPasscodeRequired           # 受取パスコード必須
└── LinkAlreadyClaimed             # 受取/拒否済み
```

## トークンをどう手に入れるか

`login()` → `login_confirm()` を通せば普通に取れる。それが面倒なら:
- **mitmproxy 派**: PayPay アプリのログイン通信を横取りして `bff/v2/oauth2/token` のレスポンスから抜く
- **API 手組み派**: `paypay.raw.oauth2_par(...)` → SMS OTP → `paypay.raw.oauth2_token(...)` を自前で組む(PKCE 必要)

`refresh_token` さえ生きてれば以後は自動更新なので、初回だけ通せば長期間放置できる。

## アプリのバージョンが変わったら

新しい APK を jadx でデコンパイルしたあと:

```bash
py -3 scripts/extract_endpoints.py       # BFFImpl から endpoint→param 抽出
py -3 scripts/codegen.py                 # paypy/raw.py を再生成
```

デフォルトパスは `../../jadx_out/sources/.../C19344p.java` を仮定。違う場所なら:
```bash
PAYPAY_BFF_SRC=/path/to/BFFImpl.java py -3 scripts/extract_endpoints.py
```

## 公開する側の人向け

GitHub に push すれば `pip install git+https://github.com/<owner>/paypy` が **その時点で使える**。追加作業なし。特定バージョンを固定したいときはタグを切る:

```bash
git tag v0.2.0
git push origin v0.2.0
# → pip install git+https://github.com/amane1201/paypy@v0.2.0
```

PyPI (`pip install paypy`) にしたい場合は 1 回だけ手作業:

```bash
# 1. アカウント作成 & API トークン発行(pypi.org)
# 2. ~/.pypirc に token 保存(または twine が env 変数から拾う)
# 3. ビルド + アップロード
py -3 -m pip install --upgrade build twine
py -3 -m build                       # dist/paypy-0.2.0-*.whl と .tar.gz が出る
py -3 -m twine upload dist/*         # 認証は API token
```

以後は `pyproject.toml` の `version` を上げて `python -m build && twine upload dist/*` 繰り返すだけ。名前 `paypy` は現時点で PyPI に空き(2026-07-26 確認)、早い者勝ちなので押さえるなら早めに。

## ライセンス

MIT。ただし PayPay の商標とかサービス自体は当然 PayPay 株式会社(ソフトバンク/LINEヤフー系)のもの。このライブラリは無関係の第三者製。
