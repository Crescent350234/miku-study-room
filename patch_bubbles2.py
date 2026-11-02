import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js = r'''
  var BUBBLES = [];

  function clearBubbles() {
    var layer = $('bubbleLayer');
    if (layer) layer.innerHTML = '';
    BUBBLES = [];
  }

  function spawnBubbles(text) {
    var layer = $('bubbleLayer');
    if (!layer || !text) return;

    if (BUBBLES.length > 3) {
      var old = BUBBLES.shift();
      if (old && old.el && old.el.parentNode) old.el.parentNode.removeChild(old.el);
    }

    var el = document.createElement('span');
    el.className = 'bubble';
    el.textContent = String(text);

    var w = window.innerWidth;
    var h = window.innerHeight;
    var x = w * (0.24 + Math.random() * 0.52);
    var y = h * (0.92 + Math.random() * 0.12);

    el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%)';
    layer.appendChild(el);

    BUBBLES.push({
      el: el,
      x: x,
      y: y,
      vy: 0.35 + Math.random() * 0.35,
      phase: Math.random() * Math.PI * 2,
      amp: 10 + Math.random() * 22
    });
  }
'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    start = t.find("  function clearBubbles() {")
    end = t.find("  function buildFumeLine", start)
    if start >= 0 and end > start:
        t = t[:start] + js + "\n" + t[end:]
    else:
        print("bubble anchor miss", d)

    # update bubbles in fxLoop before canvas drawing
    if "BUBBLES[i].y -= BUBBLES[i].vy" not in t:
        t = t.replace("  function fxLoop(now) {\n    if (!FX.ctx) return;",
                      "  function fxLoop(now) {\n    if (!FX.ctx) return;\n\n    for (var bi = BUBBLES.length - 1; bi >= 0; bi--) {\n      var bb = BUBBLES[bi];\n      bb.y -= bb.vy;\n      bb.x += Math.sin((bb.y + bb.phase) * 0.006) * 0.5;\n      var fade = bb.y < window.innerHeight * 0.18 ? Math.max(0, bb.y / (window.innerHeight * 0.18)) : 1;\n      bb.el.style.transform = 'translate3d(' + bb.x.toFixed(1) + 'px,' + bb.y.toFixed(1) + 'px,0) translateX(-50%)';\n      bb.el.style.opacity = fade.toFixed(3);\n      if (bb.y < -120) {\n        if (bb.el.parentNode) bb.el.parentNode.removeChild(bb.el);\n        BUBBLES.splice(bi, 1);\n      }\n    }\n")

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "浮名 v5：整句文字上浮" not in ct:
            ct += '''

/* ---------------- 浮名 v5：整句文字上浮（弱化泡泡感） ---------------- */
body.theme-fume .bubble {
  position: absolute !important;
  left: 0 !important;
  top: 0 !important;
  bottom: auto !important;
  display: block !important;
  max-width: 52vw;
  padding: 0 !important;
  background: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
  white-space: normal !important;
  text-align: center;
  font-size: calc(26 * var(--s)) !important;
  line-height: 1.45;
  color: #ffffff;
  opacity: 0.85;
  text-shadow: 0 calc(4 * var(--s)) calc(22 * var(--s)) rgba(0, 0, 0, 0.55);
  animation: none !important;
  will-change: transform, opacity;
}

body.theme-fume .bubble-layer {
  z-index: 4;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=93", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
