# マイクロビット 体験ワークショップ

共通ルール（すべての教材で同じ）はこちら:

@../workshop-kit/CLAUDE.md

上の読み込みが効かない環境のために、要点だけ再掲します。

- **編集してよいのは `content/` と `site.toml` だけ。** `docs/` は `python build.py` の生成物。
- `docs/assets/` の共通部品と `.gitignore` `.vscode/settings.json` は **workshop-kit が配る**。
  直すときは `../workshop-kit/wskit/` を直す（＝すべての教材に効く）。
- **表（`| … | … |`）はスライドで使えない。** 箇条書きにする。
- コミットメッセージは日本語。`docs/` もコミットに含める。

---

## この教材のきまり

書き方の詳細は [AUTHORING.md](AUTHORING.md)。とくに：

- 章フォルダ名の頭 … **b=基礎編 / a=応用編 / e=拡張編 / mq=ロボットカー編 / c=コーディング編**
- コードの言語は **`js`**（JavaScript）と **`py`**（Python）
- 字下げは**半角スペース4つ・行末のセミコロンなし**（MakeCode が出すコードに合わせる）
- カードの枠色は、基礎/応用/拡張＝`c1`〜`c7`、ロボットカー＝`r1`〜`r3`、コーディング＝`j1`〜`j3`
- **ロボットカー編の章には `level`（入門編/中級編/上級編）を付ける**

## 事実の裏取り

- ブロックの名前・メニューの場所は [MakeCode](https://makecode.microbit.org/) の実画面で確認する
- micro:Maqueen の仕様は [DFRobot の公式 wiki](https://wiki.dfrobot.com/micro_Maqueen_for_micro_bit_SKU_ROB0148) で確認する
- 画面キャプチャは MakeCode の最新UIに合わせて撮り直す（古いUIのままにしない）

## 公開しないもの

- `archive/` … 元の PowerPoint と .hex（`.gitignore` で除外済み）
