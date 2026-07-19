#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py  --  content/*.md から docs/ の教材サイトを生成するビルドスクリプト

使い方:
    python build.py

やること:
  1. content/*.md（フロントマター付き Markdown）を1章ずつ読む
  2. templates/chapter.html に流し込んで docs/<id>_<slug>.html を生成
  3. 章ごとの QR コード（docs/assets/img/qr/<id>.svg）を生成
  4. content/<id>/img/ の画像を docs/assets/img/<id>/ にコピー（大きい画像は縮小）
  5. 全章のフロントマターから docs/index.html（もくじ）を生成

依存: segno（QR生成）, Pillow（画像縮小・任意）
      pip install segno pillow
"""

import os, re, sys, shutil, html

# Windows コンソール等での文字化け・エンコードエラーを防ぐ
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
DOCS = os.path.join(ROOT, "docs")
TPL = os.path.join(ROOT, "templates")

# ---- 設定 -----------------------------------------------------------------
BASE_URL = "https://taikiishii.github.io/microbit-workshop/"
MAX_IMG_WIDTH = 1400  # これより横が大きい画像は縮小してコピー

# セクションの定義（表示順・見出し・ページタイトルの接尾辞）
SECTIONS = [
    ("基礎編",        dict(cls="s-basic", title="🔰 基礎編",
                         sub="マイクロビットを使いこなそう",
                         suffix=" — マイクロビットワークショップ")),
    ("拡張編",        dict(cls="s-ext", title="🔌 拡張編",
                         sub="外部デバイスをつないで広げよう",
                         suffix=" — マイクロビットワークショップ")),
    ("ロボットカー編", dict(cls="s-robot", title="🚗 ロボットカー編（micro:Maqueen）",
                         sub="",
                         suffix=" — ロボットカー虎の巻")),
]
SECTION_MAP = dict(SECTIONS)


def parse_frontmatter(text):
    """先頭の --- ... --- をフロントマター(dict)として取り出し、(meta, body) を返す。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    # 2つ目の '---' を探す
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta = {}
    for ln in lines[1:end]:
        if not ln.strip() or ln.strip().startswith("#"):
            continue
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    body = "\n".join(lines[end + 1:]).strip("\n")
    return meta, body


def make_qr(url, out_path):
    import segno
    q = segno.make(url, error="m")
    q.save(out_path, kind="svg", dark="#123a36", light="#ffffff",
           border=4, xmldecl=False, svgns=True, nl=False)


def copy_images(cid, body):
    """body 内の img/xxx を assets/img/<cid>/xxx に書き換え、実ファイルをコピー。"""
    srcdir = os.path.join(CONTENT, cid, "img")
    refs = set(re.findall(r"\]\(img/([^)]+)\)", body))
    if refs:
        dstdir = os.path.join(DOCS, "assets", "img", cid)
        os.makedirs(dstdir, exist_ok=True)
        for name in sorted(refs):
            src = os.path.join(srcdir, name)
            dst = os.path.join(dstdir, name)
            if not os.path.exists(src):
                print("  [!] 画像が見つかりません: content/%s/img/%s" % (cid, name))
                continue
            _copy_or_resize(src, dst)
        body = body.replace("](img/", "](assets/img/%s/" % cid)
    return body


def _copy_or_resize(src, dst):
    try:
        from PIL import Image
        im = Image.open(src)
        if im.width > MAX_IMG_WIDTH:
            h = int(im.height * MAX_IMG_WIDTH / im.width)
            im = im.resize((MAX_IMG_WIDTH, h))
            im.save(dst)
            return
    except Exception:
        pass
    shutil.copy2(src, dst)


def build_chapter(meta, body, chapter_tpl):
    cid = meta["id"]
    slug = meta["slug"]
    out_name = "%s_%s.html" % (cid, slug)
    sec = SECTION_MAP.get(meta["section"], {})
    suffix = sec.get("suffix", "")

    # 画像 img/ を assets/img/<id>/ に書き換え＋コピー
    body = copy_images(cid, body)

    # 表紙に QR を自動挿入（最初の {cover} の直後）
    qr_rel = "assets/img/qr/%s.svg" % cid
    if "{cover}" in body and "{qr:" not in body:
        body = body.replace("{cover}", "{cover}\n{qr: %s}" % qr_rel, 1)

    # QR 生成
    os.makedirs(os.path.join(DOCS, "assets", "img", "qr"), exist_ok=True)
    make_qr(BASE_URL + out_name, os.path.join(DOCS, "assets", "img", "qr", "%s.svg" % cid))

    page_title = meta["nav_title"] + suffix
    out = (chapter_tpl
           .replace("{{PAGE_TITLE}}", page_title)
           .replace("{{NAV_TITLE}}", meta["nav_title"])
           .replace("{{BODY}}", body))
    with open(os.path.join(DOCS, out_name), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    return out_name


def card_html(meta, out_name):
    color = meta.get("color", "")
    num = html.escape(meta.get("num", ""))
    emoji = meta.get("emoji", "")
    title = html.escape(meta.get("card_title", ""))
    desc = html.escape(meta.get("desc", ""))
    level = meta.get("level")
    level_html = ('<span class="level">%s</span>\n        ' % html.escape(level)) if level else ""
    return (
        '      <a class="card %s" href="%s">\n'
        '        <div class="face"><span class="num">%s</span><span class="emoji">%s</span></div>\n'
        '        %s<h2>%s</h2>\n'
        '        <p>%s</p>\n'
        '      </a>'
    ) % (color, out_name, num, emoji, level_html, title, desc)


def build_index(chapters, index_tpl):
    """chapters: list of (meta, out_name). セクションごとにカードを並べる。"""
    blocks = []
    for name, sec in SECTIONS:
        items = [(m, o) for (m, o) in chapters if m.get("section") == name]
        if not items:
            continue
        items.sort(key=lambda t: t[0]["id"])
        cards = "\n\n".join(card_html(m, o) for m, o in items)
        blocks.append(
            '  <!-- ============ %s ============ -->\n'
            '  <section class="section %s">\n'
            '    <div class="section-head">\n'
            '      <span class="stitle">%s</span>\n'
            '      <span class="ssub">%s</span>\n'
            '    </div>\n'
            '    <div class="section-line"></div>\n\n'
            '    <div class="grid">\n%s\n    </div>\n'
            '  </section>'
            % (name, sec["cls"], sec["title"], sec["sub"], cards)
        )
    out = index_tpl.replace("{{CHAPTERS}}", "\n\n".join(blocks))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)


def main():
    chapter_tpl = open(os.path.join(TPL, "chapter.html"), encoding="utf-8").read()
    index_tpl = open(os.path.join(TPL, "index.html"), encoding="utf-8").read()

    md_files = sorted(f for f in os.listdir(CONTENT)
                      if f.endswith(".md") and not f.startswith("_"))
    if not md_files:
        print("content/ に .md がありません。"); return

    chapters = []
    for fn in md_files:
        text = open(os.path.join(CONTENT, fn), encoding="utf-8").read()
        meta, body = parse_frontmatter(text)
        missing = [k for k in ("id", "slug", "section", "nav_title", "card_title") if k not in meta]
        if missing:
            print("  [!] %s: フロントマター不足 %s（スキップ）" % (fn, missing)); continue
        if meta["section"] not in SECTION_MAP:
            print("  [!] %s: 未知の section '%s'（スキップ）" % (fn, meta["section"])); continue
        out_name = build_chapter(meta, body, chapter_tpl)
        chapters.append((meta, out_name))
        print("  ✓ %-22s → docs/%s" % (fn, out_name))

    build_index(chapters, index_tpl)
    print("  ✓ もくじ           → docs/index.html（%d章）" % len(chapters))
    print("完了。")


if __name__ == "__main__":
    main()
