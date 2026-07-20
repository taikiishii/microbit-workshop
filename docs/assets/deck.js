/* =========================================================================
   deck.js  --  埋め込みMarkdownを読み込んでスライド化する小さなエンジン
   依存ライブラリなし。file:// で開いてもそのまま動く（ネット不要）。

   各章HTMLの中に
     <script type="text/markdown" id="deck-source"> ...Markdown... </script>
   を置いておくと、このスクリプトがそれをスライドに変換します。

   Markdown 記法（このワークショップ用の最小セット）:
     ---            スライドの区切り（行頭・単独）
     # 〜 ######    見出し（各スライド最初の # がスライドタイトル）
     1. / - / *     番号つき／箇条書きリスト（手順）
     ![説明](画像)   画像（説明はキャプションになる。連続すると横並び）
     > 本文          博士の吹き出し（先頭に ⚠ を付けると注意色）
     :::            スライド内を左右カラムに分ける区切り
     **太字** *斜体* `コード` [リンク](url)
   スライドの先頭に {cover} と書くと表紙用の中央寄せレイアウトになる。
   ========================================================================= */
(function () {
  "use strict";

  var MASCOT = "../assets/hakase.png"; // 吹き出しに出る博士（章ページは1階層下）

  // ---- インライン記法 ---------------------------------------------------
  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function inline(s) {
    s = esc(s);
    // 画像（インライン）
    s = s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,
      '<img src="$2" alt="$1">');
    // リンク
    s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // 太字 → コード → 斜体 の順（太字を先に処理して * の衝突を避ける）
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    return s;
  }

  // 1行が「画像だけ」かどうか
  function isImageLine(line) {
    return /^!\[[^\]]*\]\([^)]+\)\s*$/.test(line.trim());
  }
  function imageHTML(line) {
    var m = line.trim().match(/^!\[([^\]]*)\]\(([^)]+)\)\s*$/);
    var alt = m[1], src = m[2];
    var cap = alt ? '<figcaption>' + inline(alt) + '</figcaption>' : '';
    return '<figure><img src="' + src + '" alt="' + esc(alt) + '">' + cap + '</figure>';
  }

  // ---- ブロック記法（1カラム分のMarkdown → HTML） ---------------------
  function blocks(md) {
    var lines = md.replace(/\r/g, "").split("\n");
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];

      if (line.trim() === "") { i++; continue; }

      // 見出し
      var h = line.match(/^(#{1,6})\s+(.*)$/);
      if (h) {
        var lv = h[1].length;
        out.push("<h" + lv + ">" + inline(h[2]) + "</h" + lv + ">");
        i++; continue;
      }

      // 画像（連続していれば横並びの figrow に）
      if (isImageLine(line)) {
        var figs = [];
        while (i < lines.length && isImageLine(lines[i])) {
          figs.push(imageHTML(lines[i])); i++;
        }
        if (figs.length === 1) out.push(figs[0]);
        else out.push('<div class="figrow">' + figs.join("") + "</div>");
        continue;
      }

      // 吹き出し（blockquote）
      if (/^>\s?/.test(line)) {
        var buf = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) {
          buf.push(lines[i].replace(/^>\s?/, "")); i++;
        }
        var text = buf.join(" ").trim();
        var cls = "";
        if (/^(⚠|！|注意)/.test(text)) { cls = " warn"; text = text.replace(/^(⚠️?|！|注意[:：]?)\s*/, ""); }
        else if (/^💪/.test(text)) { cls = " challenge"; text = text.replace(/^💪\s*/, ""); }
        out.push(
          '<div class="callout' + cls + '">' +
            '<img class="hakase" src="' + MASCOT + '" alt="博士">' +
            '<div class="callout-body"><p>' + inline(text) + "</p></div>" +
          "</div>");
        continue;
      }

      // 番号つきリスト
      if (/^\d+\.\s+/.test(line)) {
        var oli = [];
        while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
          oli.push("<li>" + inline(lines[i].replace(/^\d+\.\s+/, "")) + "</li>"); i++;
        }
        out.push("<ol>" + oli.join("") + "</ol>");
        continue;
      }

      // 箇条書き
      if (/^[-*]\s+/.test(line)) {
        var uli = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i])) {
          uli.push("<li>" + inline(lines[i].replace(/^[-*]\s+/, "")) + "</li>"); i++;
        }
        out.push("<ul>" + uli.join("") + "</ul>");
        continue;
      }

      // 段落（空行まで）
      var para = [];
      while (i < lines.length && lines[i].trim() !== "" &&
             !/^(#{1,6}\s|>\s?|\d+\.\s|[-*]\s)/.test(lines[i]) && !isImageLine(lines[i])) {
        para.push(lines[i]); i++;
      }
      out.push("<p>" + inline(para.join(" ")) + "</p>");
    }
    return out.join("\n");
  }

  // ---- スライド1枚を組み立てる -----------------------------------------
  function buildSlide(md, index) {
    var cover = false;
    md = md.replace(/^\s*\{cover\}\s*$/m, function () { cover = true; return ""; });

    // {qr: パス} … スライド右下にQRコードと説明を表示（主に表紙で使う）
    var qr = null;
    md = md.replace(/\{qr:\s*([^}]+)\}/, function (_, p) { qr = p.trim(); return ""; });

    // 画像だけで構成されたチャンクか（＝大きく見せるメディアカラム）
    function isMediaChunk(c) {
      var ls = c.replace(/\r/g, "").split("\n").filter(function (l) { return l.trim() !== ""; });
      return ls.length > 0 && ls.every(isImageLine);
    }

    var inner;
    if (/^\s*:::\s*$/m.test(md)) {
      // 最初の ::: より前は「全幅ヘッダー」（タイトルなど）。残りを左右カラムにする。
      var chunks = md.split(/^\s*:::\s*$/m);
      var header = chunks.shift();
      var headerHTML = header.trim() ? blocks(header) : "";
      var cols = chunks.map(function (c) {
        var media = isMediaChunk(c);
        return '<div class="col' + (media ? " col-media" : "") + '">' + blocks(c) + "</div>";
      }).join("");
      inner = headerHTML + '<div class="cols">' + cols + "</div>";
    } else {
      inner = blocks(md);
    }

    var slide = document.createElement("section");
    slide.className = "slide" + (qr ? " has-qr" : "");
    slide.innerHTML =
      '<div class="slide-inner' + (cover ? " cover" : "") + '">' + inner + "</div>" +
      (qr ? '<div class="slide-qr"><img src="' + qr + '" alt="QRコード">' +
            '<span class="cap">この資料はこちらから<br>ダウンロードできます</span></div>' : "") +
      '<div class="page-no">' + (index + 1) + "</div>";
    return slide;
  }

  // ---- 初期化 -----------------------------------------------------------
  function init() {
    var src = document.getElementById("deck-source");
    if (!src) return;
    var md = src.textContent;

    // スライド分割（行頭の --- 単独）
    var parts = md.replace(/\r/g, "").split(/\n[ \t]*-{3,}[ \t]*\n/);

    var deck = document.getElementById("deck") || (function () {
      var d = document.createElement("div"); d.id = "deck"; d.className = "deck";
      document.body.appendChild(d); return d;
    })();

    var slides = [];
    parts.forEach(function (p, idx) {
      if (p.trim() === "") return;
      var el = buildSlide(p, slides.length);
      deck.appendChild(el);
      slides.push(el);
    });

    setupModes(slides);

    // #present で開いたら発表モードで起動（会場配布URLに便利）。#present=3 で3枚目から。
    var mp = location.hash.match(/^#present(?:=(\d+))?$/);
    if (mp) {
      var btn = document.getElementById("btn-present");
      if (btn) btn.click();
      if (mp[1] && window.__deckGoto) window.__deckGoto(parseInt(mp[1], 10) - 1);
    }
  }

  // ---- Web / 発表モードの切り替えと操作 ---------------------------------
  function setupModes(slides) {
    var current = 0;

    function show(n) {
      current = Math.max(0, Math.min(slides.length - 1, n));
      slides.forEach(function (s, i) { s.classList.toggle("active", i === current); });
      var c = document.getElementById("counter");
      if (c) c.textContent = (current + 1) + " / " + slides.length;
      var active = slides[current];
      if (active && !document.body.classList.contains("mode-present")) {
        active.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    function enterPresent() {
      document.body.classList.add("mode-present");
      // いま画面に一番近いスライドから開始
      var best = 0, bestDist = Infinity;
      slides.forEach(function (s, i) {
        var d = Math.abs(s.getBoundingClientRect().top);
        if (d < bestDist) { bestDist = d; best = i; }
      });
      show(best);
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().catch(function () {});
      }
    }
    function exitPresent() {
      document.body.classList.remove("mode-present");
      if (document.fullscreenElement && document.exitFullscreen) {
        document.exitFullscreen().catch(function () {});
      }
      slides[current].scrollIntoView({ block: "center" });
    }

    window.__deckGoto = show; // 深リンク用

    // ボタン
    var bPresent = document.getElementById("btn-present");
    var bPrint = document.getElementById("btn-print");
    if (bPresent) bPresent.addEventListener("click", enterPresent);
    if (bPrint) bPrint.addEventListener("click", function () { window.print(); });

    // 発表バー
    var bar = document.createElement("div");
    bar.className = "present-bar";
    bar.innerHTML =
      '<button id="pv">◀ もどる</button>' +
      '<span class="counter" id="counter">1 / ' + slides.length + "</span>" +
      '<button id="nx">つぎ ▶</button>' +
      '<button id="ex">終了 (Esc)</button>';
    document.body.appendChild(bar);
    document.getElementById("pv").addEventListener("click", function () { show(current - 1); });
    document.getElementById("nx").addEventListener("click", function () { show(current + 1); });
    document.getElementById("ex").addEventListener("click", exitPresent);

    // クリックで次へ（発表モード時、ボタン以外）
    document.addEventListener("click", function (e) {
      if (!document.body.classList.contains("mode-present")) return;
      if (e.target.closest(".present-bar")) return;
      show(current + 1);
    });

    // キーボード
    document.addEventListener("keydown", function (e) {
      var present = document.body.classList.contains("mode-present");
      if (e.key === "Escape" && present) { exitPresent(); return; }
      if (!present) return;
      if (e.key === "ArrowRight" || e.key === "PageDown" || e.key === " ") { e.preventDefault(); show(current + 1); }
      else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); show(current - 1); }
      else if (e.key === "Home") { show(0); }
      else if (e.key === "End") { show(slides.length - 1); }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
