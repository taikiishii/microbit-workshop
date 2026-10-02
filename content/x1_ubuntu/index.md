---
id: x1
slug: ubuntu
section: 付録
emoji: 🐧
num: 1
color: c5
nav_title: ① Ubuntu で使う
card_title: Ubuntu で使う
desc: Ubuntu のパソコンに Chromium と USB の許可（udev）を設定して、MakeCode や CreateAI からマイクロビットに直接書きこめるようにする。セットアップする大人むけ。
wip: 実機確認まち
---

{cover}
# ① Ubuntu で使う

MakeCode からマイクロビットに直接書きこむまで

*セットアップする大人むけ*

---

# この章について
**Ubuntu** のパソコンで MakeCode を使うための準備です。端末（ターミナル）でコマンドを順に実行します。

1. Chromium を入れて、USB を許可する
2. 書きこみの許可（udev）を設定する
3. `plugdev` グループに入っているか確かめる
4. MakeCode でつないでみる

> Ubuntu 22.04 以降は、ほぼ同じ手順です。管理者のパスワード（`sudo`）が要ります。
> この設定をすると、**CreateAI**（AI編）の「接続」も同じように使えます。

---

# 1. Chromium を入れる

:::

MakeCode がマイクロビットに直接書きこむには **WebUSB** という機能を使います。

- Ubuntu に最初から入っている **Firefox は WebUSB が使えない**
- **Chromium** を入れる（Ubuntu では **snap** で配られている）
- snap はそのままだと USB 機器にさわれないので、`raw-usb` という許可を**手でつなぐ**

> `raw-usb` は自動ではつながりません（すべての USB 機器にさわれるようになるため）。

:::

```bash 1. Chromium を入れて USB を許可する
sudo snap install chromium
sudo snap connect chromium:raw-usb
```

---

# 2. 書きこみの許可（udev）

:::

Linux では、USB 機器を使うのに**許可**が要ります。micro:bit の**公式サポート**にある設定を入れます。

- マイクロビットの番号は **0d28**（V1・V2 とも同じ）
- `plugdev` グループの人が使えるようになる
- **Chromium を閉じてから**実行する

:::

```bash 2. udev ルールを入れる
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0d28", MODE="0664", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/50-microbit.rules
sudo udevadm control --reload-rules
```

---

# 3. plugdev グループを確かめる

:::

udev ルールは「`plugdev` グループの人」に許可を出します。使う人がこのグループに入っているか確かめます。

- 表示に `plugdev` があれば OK
- なければ、2行目で追加して**ログインしなおす**

> ⚠ グループの変更は、**ログインしなおすまで効きません**。

:::

```bash 3. グループを確かめる（なければ追加）
groups    # 表示に plugdev があるか確かめる
sudo usermod -aG plugdev $USER
```

---

# 4. MakeCode でつないでみる

1. ログインしなおしたら、マイクロビットを USB で**さしなおす**
2. Chromium で `https://makecode.microbit.org/` をひらく
3. 左下の「**・・・**」→「**デバイスを接続する**」→「**次へ**」→「**ペア**」
4. `BBC micro:bit CMSIS-DAP` をえらんで「**接続**」
5. 「**ダウンロード**」で、そのまま書きこまれれば成功

> 手順は基礎編「はじめてのマイクロビット」と同じです。

---

# うまくいかないとき

- **一覧に `BBC micro:bit CMSIS-DAP` が出ない** → Chromium で開いているか確かめる（Firefox は不可）／`snap connections chromium` で `raw-usb` がつながっているか確かめる（手順 1）
- **えらんでも接続に失敗する** → udev ルールを確かめ（手順 2）、マイクロビットをさしなおす
- **まだ失敗する** → `groups` に `plugdev` がなければ手順 3 のあとログインしなおす
- **どうしてもつながらない** → 「ダウンロード」で保存した `.hex` ファイルを、ファイルの画面で **MICROBIT** ドライブにコピーする（この方法は設定なしで使える）

> この設定はパソコン1台につき1回です。ワークショップの前にすませておきましょう。
