import io

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

start = t.find("    BUBBLES.forEach(function (b) {")
end = t.find("  }\n\n  function buildFumeLine", start)
if start < 0 or end < 0:
    raise SystemExit("anchor miss")

new = r'''    var now = performance.now();

    BUBBLES.forEach(function (b) {
      var rel = b.idx - cur;
      var yFactor = rel < 0 ? 0.24 : rel === 0 ? 0.50 : 0.76;
      var isCur = rel === 0;

      var age = (now - b.born) / 1000;
      var bobY = Math.sin(now / 1000 * 0.62 + b.phase) * 11;
      var bobX = Math.sin(now / 1000 * 0.41 + b.phase * 1.7) * 34;
      var rot = Math.sin(now / 1000 * 0.5 + b.phase) * 1.8;

      var y = H * yFactor + bobY;
      var x = W / 2 + bobX;

      var fadeIn = Math.min(1, age / 0.8);
      var op = (isCur ? 1 : 0.34) * fadeIn;

      b.el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%) rotate(' + rot.toFixed(2) + 'deg)';
      b.el.style.opacity = op.toFixed(3);
      b.el.style.setProperty('font-size', isCur ? 'calc(50 * var(--s))' : 'calc(32 * var(--s))', 'important');
      b.el.style.color = isCur ? accent : 'rgba(255,255,255,0.72)';
      b.el.style.textShadow = isCur
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });
'''

t = t[:start] + new + t[end:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("float added")
