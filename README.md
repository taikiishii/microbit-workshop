# マイクロビット 体験ワークショップ

子ども向けの **micro:bit / ロボットカー（micro:Maqueen）** プログラミング・ワークショップ教材です。
ブロックだけでなく、**JavaScript / Python のコーディング編**もあります（コードはワンクリックでコピーできます）。

## 🌐 公開ページ（GitHub Pages）

**https://taikiishii.github.io/microbit-workshop/**

もくじページから各章を開けます。

- 1つのソース（Markdown）から、**Web ページ / 発表スライド / 印刷用 PDF** の3通りに使えます。
  - 各ページ上部の「▶ 発表モード」で全画面プレゼン、「印刷 / PDF」でスライド形式の配布資料になります。

## 新しい資料を作るには

`content/` に Markdown を書いて `python build.py` を実行するだけで、HTML・QRコード・もくじが自動生成されます。

- この教材だけのきまり … **[AUTHORING.md](AUTHORING.md)**
- 共通の書き方（記法・画像・1枚に入る量） … **[workshop-kit の AUTHORING.md](https://github.com/taikiishii/workshop-kit/blob/main/AUTHORING.md)**

ビルドのしくみ（CSS・JavaScript・テンプレート・変換スクリプト）は、
ほかのワークショップ教材と共有している **[workshop-kit](https://github.com/taikiishii/workshop-kit)** にあります。
はじめての1回だけ、となりのフォルダに置いて入れてください。

```bash
git clone https://github.com/taikiishii/workshop-kit.git ../workshop-kit
pip install -e ../workshop-kit
```

## リポジトリ構成（概要）

**1つの章 = 1つのフォルダ**（`content/` と `docs/` が対称）。

- `site.toml` … **この教材だけの設定**（公開URL・セクション・カードの色・コードで青くする語）
- `content/<章>/` … 各章の **`index.md`（編集するのはここ）** と `image/index/`（画面キャプチャ）
- `content/_index/` … もくじページに足すブロック（`license.html`）
- `build.py` … workshop-kit を呼ぶだけの数行
- `docs/<章>/` … `build.py` が生成する `index.html` / `qr.svg` / `image/index/`（GitHub Pages 配信元。直接編集しない）
- `docs/assets/` … 共通部品（workshop-kit から配置）＋ `site-theme.css` / `site-config.js`（`site.toml` から生成）
- `archive/` … 元の PowerPoint など（`.gitignore` で除外・**非公開**）

## ライセンス

文章・レイアウト・プログラムは **MIT ライセンス**（[docs/LICENSE.txt](docs/LICENSE.txt)）で公開しています。
自由に利用・改変・再配布できますが、作成者は一切の責任を負いません（無保証）。

※ 画面キャプチャ・イラスト・写真などの第三者素材は MIT の対象外で、各提供元の利用規約に従います。

Copyright © 2026 Taiki Ishii
