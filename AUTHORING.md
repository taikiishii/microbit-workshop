# 資料の作り方 — マイクロビット教材のきまり

> **共通の書き方（Markdownの記法・画像の渡し方・1枚に入る量・ビルド手順）は
> [workshop-kit の AUTHORING.md](https://github.com/taikiishii/workshop-kit/blob/main/AUTHORING.md)
> にあります。まずそちらを読んでください**（ローカルなら `../workshop-kit/AUTHORING.md`）。
>
> このファイルには、**この教材だけのきまり**を書いています。

---

## 章フォルダ名とセクション

章フォルダ名の頭は **b=基礎編 / a=応用編 / e=拡張編 / mq=ロボットカー編 / c=コーディング編**
＋ 連番（例：`b6_mic`, `a1_counter`, `e2_servo`, `mq4_remote`, `c1_javascript`）。

frontmatter の `section` に書く名前と、その中身：

- `基礎編` … micro:bit だけ（外部デバイスなし）
- `応用編` … 変数・くりかえし・条件分岐（micro:bit だけ）
- `拡張編` … 外部デバイスをつなぐ
- `ロボットカー編` … micro:Maqueen（`level` も付ける）
- `コーディング編` … JavaScript / Python の文字のプログラム

カードの枠色 `color` は、セクションによって使う組が違います。

- 基礎編・応用編・拡張編 … `c1`〜`c7`
- ロボットカー編 … `r1`〜`r3`（`level` ラベルの色もこれで決まる）
- コーディング編 … `j1`=JavaScript の黄 / `j2`=Python の青 / `j3`=よてい

定義は `site.toml` の `[palette]` `[palette.level]` `[[sections]]` にあります。

### ロボットカー編の `level`

ロボットカー編の章には難易度ラベルを付けます。`color` と同じ組で色が決まります。

```yaml
color: r1
level: 入門編      # r1=入門編（緑） / r2=中級編（黄） / r3=上級編（赤）
```

## コードの書き方

言語は **`js`**（＝JavaScript）と **`py`**（＝Python）。`javascript` / `python` と書いてもOK。

- **メイクコードが作るコードに合わせて、字下げは半角スペース4つ・行末のセミコロンなし**にすると、
  貼りつけたときに同じ見た目になります
- `basic` `input` `music` `radio` などの MakeCode のグループ名は**青く**表示されます
  （語の一覧は `site.toml` の `[code] namespaces`）

## このリポジトリだけのフォルダ

- `archive/` … 元の PowerPoint など（`.gitignore` で除外・**非公開**）
- `content/_index/license.html` … MakeCode の画面キャプチャなど第三者素材の注記
