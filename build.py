#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py  --  content/ から docs/ の教材サイトを生成するビルドスクリプト

使い方:
    python build.py

構成（章ごとに1フォルダ・content と docs が対称）:
    content/<章>/index.md   +  content/<章>/img/*     （あなたが編集するのはここだけ）
        │  python build.py
        ▼
    docs/<章>/index.html    +  docs/<章>/img/*  +  docs/<章>/qr.svg
    docs/assets/            … deck.css / deck.js / hakase.png / qr.svg（共通部品）
    docs/index.html         … もくじ

依存: segno（QR生成）, Pillow（画像縮小・任意）  →  pip install segno pillow
"""

import os, re, sys, shutil, html

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


def _copy_or_resize(src, dst):
    try:
        from PIL import Image
        im = Image.open(src)
        if im.width > MAX_IMG_WIDTH:
            h = int(im.height * MAX_IMG_WIDTH / im.width)
            im.resize((MAX_IMG_WIDTH, h)).save(dst)
            return
    except Exception:
        pass
    shutil.copy2(src, dst)


def copy_images(chapter_dir, body, out_dir):
    """body 内の img/xxx を content/<章>/img から docs/<章>/img へコピー（パスはそのまま）。"""
    refs = sorted(set(re.findall(r"\]\(img/([^)]+)\)", body)))
    if not refs:
        return
    srcdir = os.path.join(CONTENT, chapter_dir, "img")
    dstdir = os.path.join(out_dir, "img")
    os.makedirs(dstdir, exist_ok=True)
    for name in refs:
        src = os.path.join(srcdir, name)
        if not os.path.exists(src):
            print("  [!] 画像が見つかりません: content/%s/img/%s" % (chapter_dir, name))
            continue
        _copy_or_resize(src, os.path.join(dstdir, name))


def build_chapter(meta, body, chapter_dir, chapter_tpl):
    out_dir = os.path.join(DOCS, chapter_dir)
    os.makedirs(out_dir, exist_ok=True)

    copy_images(chapter_dir, body, out_dir)

    # 表紙に QR を自動挿入（最初の {cover} の直後）。QRは章フォルダ内 qr.svg
    if "{cover}" in body and "{qr:" not in body:
        body = body.replace("{cover}", "{cover}\n{qr: qr.svg}", 1)
    make_qr(BASE_URL + chapter_dir + "/", os.path.join(out_dir, "qr.svg"))

    suffix = SECTION_MAP.get(meta["section"], {}).get("suffix", "")
    out = (chapter_tpl
           .replace("{{PAGE_TITLE}}", meta["nav_title"] + suffix)
           .replace("{{NAV_TITLE}}", meta["nav_title"])
           .replace("{{BODY}}", body))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(out)


def card_html(meta, chapter_dir):
    num = html.escape(meta.get("num", ""))
    title = html.escape(meta.get("card_title", ""))
    desc = html.escape(meta.get("desc", ""))
    level = meta.get("level")
    level_html = ('<span class="level">%s</span>\n        ' % html.escape(level)) if level else ""
    return (
        '      <a class="card %s" href="%s/">\n'
        '        <div class="face"><span class="num">%s</span><span class="emoji">%s</span></div>\n'
        '        %s<h2>%s</h2>\n'
        '        <p>%s</p>\n'
        '      </a>'
    ) % (meta.get("color", ""), chapter_dir, num, meta.get("emoji", ""), level_html, title, desc)


def build_index(chapters, index_tpl):
    blocks = []
    for name, sec in SECTIONS:
        items = [(m, d) for (m, d) in chapters if m.get("section") == name]
        if not items:
            continue
        items.sort(key=lambda t: t[0].get("id", t[1]))
        cards = "\n\n".join(card_html(m, d) for m, d in items)
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

    dirs = sorted(d for d in os.listdir(CONTENT)
                  if os.path.isdir(os.path.join(CONTENT, d)) and not d.startswith("_"))
    chapters = []
    for d in dirs:
        mdpath = os.path.join(CONTENT, d, "index.md")
        if not os.path.exists(mdpath):
            print("  [!] %s に index.md がありません（スキップ）" % d); continue
        meta, body = parse_frontmatter(open(mdpath, encoding="utf-8").read())
        missing = [k for k in ("section", "nav_title", "card_title") if k not in meta]
        if missing:
            print("  [!] %s: フロントマター不足 %s（スキップ）" % (d, missing)); continue
        if meta["section"] not in SECTION_MAP:
            print("  [!] %s: 未知の section '%s'（スキップ）" % (d, meta["section"])); continue
        build_chapter(meta, body, d, chapter_tpl)
        chapters.append((meta, d))
        print("  ✓ content/%-18s → docs/%s/" % (d, d))

    build_index(chapters, index_tpl)
    print("  ✓ もくじ                        → docs/index.html（%d章）" % len(chapters))
    print("完了。")


if __name__ == "__main__":
    main()
