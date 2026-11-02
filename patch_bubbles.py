import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js = r'''
  function clearBubbles() {
    var layer = $('bubbleLayer');
    if (layer) layer.innerHTML = '';
  }

  function spawnBubbles(text) {
    var layer = $('bubbleLayer');
    if (!layer) return;
    layer.innerHTML = '';
    if (!text) return;

    var raw = String(text).split(/[，。！？、；：\s]+/).filter(function (s) { return s.trim().length > 0; });
    var chunks = [];
    raw.forEach(function (part) {
      var arr = Array.from(part);
      for (var i = 0; i < arr.length; i += 3) chunks.push(arr.slice(i, i + 3).join(''));
    });
    if (!chunks.length) chunks = [String(text)];

    var pal = lyricPalette();

    chunks.forEach(function (chunk, i) {
      var b = document.createElement('span');
      b.className = 'bubble';
      b.textContent = chunk;

      b.style.left = (4 + Math.random() * 86).toFixed(1) + 'vw';
      b.style.fontSize = (16 + Math.random() * 18).toFixed(0) + 'px';
      b.style.setProperty('--drift', ((Math.random() * 180 - 90).toFixed(0)) + 'px');
      b.style.animationDuration = (9 + Math.random() * 6).toFixed(1) + 's';
      b.style.animationDelay = (i * 0.55 + Math.random() * 0.7).toFixed(2) + 's';
      b.style.color = (i % 4 === 1) ? pal[1] : '#ffffff';

      layer.appendChild(b);
    });
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="bubbleLayer"' not in t:
            anchor = '  <canvas id="fxCanvas"'
            if anchor in t:
                t = t.replace(anchor, '  <div id="bubbleLayer" class="bubble-layer"></div>\n\n' + anchor, 1)
                io.open(h, "w", encoding="utf-8", newline="").write(t)
                print("html", d)

    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function spawnBubbles" not in t:
        t = t.replace("  function buildFumeLine(idx) {", js + "\n  function buildFumeLine(idx) {", 1)

    # fume uses bubbles instead of the old layout
    t = t.replace("    if (S.lyricTheme === 'fume') { buildFumeLine(idx); return; }",
                  "    if (S.lyricTheme === 'fume') { spawnBubbles(S.lrc[idx] ? S.lrc[idx].text : ''); return; }")

    # clear bubbles when leaving fume / idle
    if "if (S.lyricTheme !== 'fume') clearBubbles();" not in t:
        t = t.replace("    if (idx < 0) {", "    if (S.lyricTheme !== 'fume') clearBubbles();\n\n    if (idx < 0) {", 1)

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "浮名 v4：上浮气泡" not in ct:
            ct += '''

/* ---------------- 浮名 v4：上浮气泡 ---------------- */
.bubble-layer {
  position: fixed;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  overflow: hidden;
}

.bubble {
  position: absolute;
  bottom: -14vh;
  display: inline-block;
  padding: 0.32em 0.9em;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.32);
  -webkit-backdrop-filter: blur(6px) saturate(160%);
  backdrop-filter: blur(6px) saturate(160%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.55),
    0 calc(10 * var(--s)) calc(30 * var(--s)) rgba(0, 0, 0, 0.25);
  white-space: nowrap;
  opacity: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
  animation: bubbleRise linear forwards;
  will-change: translate, opacity;
}

@keyframes bubbleRise {
  0%   { translate: 0 0; opacity: 0; }
  8%   { opacity: 0.95; }
  55%  { translate: var(--drift, 0px) -55vh; }
  100% { translate: calc(var(--drift, 0px) * -0.5) -125vh; opacity: 0; }
}

body.theme-fume .lyrics {
  display: none !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=89", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
