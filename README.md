# マイクロビット 体験ワークショップ

子ども向けの **micro:bit / ロボットカー（micro:Maqueen）** プログラミング・ワークショップ教材です。

## 🌐 公開ページ（GitHub Pages）

**https://taikiishii.github.io/microbit-workshop/**

もくじページから各章を開けます。

- 1つのソース（Markdown）から、**Web ページ / 発表スライド / 印刷用 PDF** の3通りに使えます。
  - 各ページ上部の「▶ 発表モード」で全画面プレゼン、「印刷 / PDF」でスライド形式の配布資料になります。

## 新しい資料を作るには

`content/` に Markdown を書いて `python build.py` を実行するだけで、HTML・QRコード・もくじが自動生成されます。
くわしい手順は **[AUTHORING.md](AUTHORING.md)** を参照してください（ひな形は `content/_template.md`）。

## リポジトリ構成（概要）

- `content/` … 各章の **Markdown（編集するのはここ）** と画面キャプチャ
- `templates/`, `build.py` … 変換のしくみ
- `docs/` … `build.py` が生成する公開ファイル（GitHub Pages 配信元。直接編集しない）
- `archive/` … 元の PowerPoint など（`.gitignore` で除外・**非公開**）

## ライセンス

文章・レイアウト・プログラムは **MIT ライセンス**（[docs/LICENSE.txt](docs/LICENSE.txt)）で公開しています。
自由に利用・改変・再配布できますが、作成者は一切の責任を負いません（無保証）。

※ 画面キャプチャ・イラスト・写真などの第三者素材は MIT の対象外で、各提供元の利用規約に従います。

Copyright © 2026 Taiki Ishii
