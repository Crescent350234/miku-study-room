import io

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

# add random fields at creation
old_push = """      BUBBLES.push({
        idx: i,
        el: el,
        phase: Math.random() * Math.PI * 2,
        born: performance.now()
      });"""
new_push = """      BUBBLES.push({
        idx: i,
        el: el,
        phase: Math.random() * Math.PI * 2,
        born: performance.now(),
        bx: (Math.random() - 0.5) * window.innerWidth * 0.18,
        by: (Math.random() - 0.5) * window.innerHeight * 0.05,
        amp: 40 + Math.random() * 50,
        freqX: 0.18 + Math.random() * 0.22,
        freqY: 0.45 + Math.random() * 0.4,
        rotBase: (Math.random() - 0.5) * 5,
        scaleJitter: 0.9 + Math.random() * 0.2
      });"""
if old_push in t:
    t = t.replace(old_push, new_push)

start = t.find("    BUBBLES.forEach(function (b) {")
end = t.find("  }\n\n  function buildFumeLine", start)
if start < 0 or end < 0:
    raise SystemExit("anchor miss")

new_block = r'''    BUBBLES.forEach(function (b) {
      var rel = b.idx - cur;
      var yFactor = rel < 0 ? 0.24 : rel === 0 ? 0.50 : 0.76;
      var isCur = rel === 0;

      var age = (now - b.born) / 1000;
      var tt = now / 1000;

      var bobY = Math.sin(tt * b.freqY + b.phase) * 13;
      var bobX = Math.sin(tt * b.freqX + b.phase * 1.7) * b.amp;
      var rot = b.rotBase + Math.sin(tt * 0.4 + b.phase) * 2.4;

      var y = H * yFactor + b.by + bobY - (isCur ? Math.min(26, age * 2.6) : 0);
      var x = W / 2 + b.bx + bobX;
      var scale = (0.78 + (1 - y / H) * 0.62) * b.scaleJitter;

      var fadeIn = Math.min(1, age / 0.8);
      var op = (isCur ? 1 : 0.34) * fadeIn;

      b.el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%) rotate(' + rot.toFixed(2) + 'deg) scale(' + scale.toFixed(3) + ')';
      b.el.style.opacity = op.toFixed(3);
      b.el.style.setProperty('font-size', 'calc(42 * var(--s))', 'important');
      b.el.style.color = isCur ? accent : 'rgba(255,255,255,0.72)';
      b.el.style.textShadow = isCur
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });
'''

t = t[:start] + new_block + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("randomized bubbles patched")
