import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js_add = r'''
  function ensureQsTrack() {
    var layer = $('qsLayer');
    if (!layer || !S.lrc.length) return;

    if (S.qsTrack && S.qsLrcRef === S.lrc) return;

    layer.innerHTML = '';
    var track = document.createElement('div');
    track.className = 'qs-track';

    S.lrc.forEach(function (line) {
      if (!line || !line.text) return;

      var col = document.createElement('div');
      col.className = 'qs-col';

      var textCol = document.createElement('div');
      textCol.className = 'qs-text';
      Array.from(line.text).forEach(function (ch) {
        var sp = document.createElement('span');
        sp.className = 'qs-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        textCol.appendChild(sp);
      });
      col.appendChild(textCol);

      if (line.sub) {
        var subCol = document.createElement('div');
        subCol.className = 'qs-text qs-sub-text';
        Array.from(line.sub).forEach(function (ch) {
          var sp = document.createElement('span');
          sp.className = 'qs-sub-char';
          sp.textContent = ch === ' ' ? '\u00a0' : ch;
          subCol.appendChild(sp);
        });
        col.appendChild(subCol);
      }

      track.appendChild(col);
    });

    layer.appendChild(track);
    S.qsTrack = track;
    S.qsLrcRef = S.lrc;
    S.qsCols = track.children;
  }

  function updateQingshu() {
    if (S.lyricTheme !== 'qingshu') return;

    ensureQsTrack();
    var layer = $('qsLayer');
    if (!layer || !S.qsTrack || !S.qsCols || !S.qsCols.length) return;
    if (S.lrcIndex < 0) return;

    var idx = Math.min(S.lrcIndex, S.qsCols.length - 1);

    for (var i = 0; i < S.qsCols.length; i++) {
      S.qsCols[i].classList.toggle('current', i === idx);
    }

    var col = S.qsCols[idx];
    var cx = layer.clientWidth / 2;
    var x = cx - (col.offsetLeft + col.offsetWidth / 2);
    S.qsTrack.style.transform = 'translateX(' + x.toFixed(1) + 'px)';
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "function ensureQsTrack" not in t:
        t = t.replace("  function buildQingshuLine(idx) {", js_add + "\n  function buildQingshuLine(idx) {", 1)

    if "updateQingshu();" not in t:
        t = t.replace("    updateBubbles(dt);", "    updateBubbles(dt);\n    updateQingshu();", 1)

    t = t.replace("if (S.lyricTheme === 'qingshu') { buildQingshuLine(idx); return; }",
                  "if (S.lyricTheme === 'qingshu') { return; }")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="qsLayer"' not in ht:
            ht = ht.replace('<div id="bubbleLayer"', '<div id="qsLayer" class="qs-layer"></div>\n    <div id="bubbleLayer"', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=175", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书 v9：常驻轨道" not in ct:
            ct += '''

/* 青书 v9：常驻轨道，向左平移 */
.qs-layer {
  position: fixed;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  overflow: hidden;
}

body.theme-qingshu .lyrics {
  opacity: 0 !important;
}

.qs-track {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  display: flex;
  align-items: center;
  gap: calc(34 * var(--s));
  padding: 0 calc(40 * var(--s));
  transition: transform 0.95s cubic-bezier(0.22, 0.8, 0.2, 1);
  will-change: transform;
}

.qs-col {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: calc(10 * var(--s));
  padding: 0 calc(20 * var(--s));
  border-right: 1px solid rgba(140, 220, 215, 0.22);
  opacity: 0.38;
  transition: opacity 0.5s ease;
}

.qs-col.current {
  opacity: 1;
}

.qs-text {
  writing-mode: vertical-rl;
  text-orientation: upright;
  display: inline-block;
  text-align: center;
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
}

.qs-text .qs-char {
  font-size: calc(40 * var(--s));
  line-height: 1.08;
  letter-spacing: 0.12em;
  color: #cfece6;
  text-shadow: 0 0 calc(14 * var(--s)) rgba(150, 225, 220, 0.22);
}

.qs-col.current .qs-char {
  color: #f0f8ee;
  text-shadow: 0 0 calc(18 * var(--s)) rgba(150, 225, 220, 0.4);
}

.qs-sub-text .qs-sub-char {
  font-size: calc(18 * var(--s));
  line-height: 1.12;
  letter-spacing: 0.08em;
  color: rgba(160, 210, 205, 0.7);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
