import io, os

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

# start position above player
t = t.replace("    var y = h * (0.92 + Math.random() * 0.12);", "    var y = h * (0.72 + Math.random() * 0.08);")
t = t.replace("      vy: 0.35 + Math.random() * 0.35,", "      vy: 22 + Math.random() * 22,")

# add updateBubbles after spawnBubbles
if "function updateBubbles" not in t:
    anchor = "  function buildFumeLine(idx) {"
    fn = r'''
  function updateBubbles(dt) {
    for (var i = BUBBLES.length - 1; i >= 0; i--) {
      var b = BUBBLES[i];
      b.y -= b.vy * dt;
      b.x += Math.sin((b.y + b.phase) * 0.01) * 18 * dt;
      var fade = b.y < window.innerHeight * 0.15 ? Math.max(0, b.y / (window.innerHeight * 0.15)) : 1;
      if (b.el) {
        b.el.style.transform = 'translate3d(' + b.x.toFixed(1) + 'px,' + b.y.toFixed(1) + 'px,0) translateX(-50%)';
        b.el.style.opacity = fade.toFixed(3);
      }
      if (b.y < -80) {
        if (b.el && b.el.parentNode) b.el.parentNode.removeChild(b.el);
        BUBBLES.splice(i, 1);
      }
    }
  }

'''
    t = t.replace(anchor, fn + anchor, 1)

# remove bubble block from fxLoop
start = t.find("    for (var bi = BUBBLES.length - 1; bi >= 0; bi--) {")
end = t.find("    if (document.body.classList.contains('theme-hanabi')) {", start)
if start >= 0 and end > start:
    t = t[:start] + t[end:]

# call updateBubbles in main loop (after paint call)
if "updateBubbles(dt);" not in t:
    t = t.replace("    tickPomo(dt);", "    updateBubbles(dt);\n\n    tickPomo(dt);", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bubble loop patched")
