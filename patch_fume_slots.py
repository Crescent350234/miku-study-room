import io

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

start = t.find("  function updateBubbles(dt) {")
end = t.find("  function buildFumeLine", start)
if start < 0 or end < 0:
    raise SystemExit("anchor miss")

new = r'''  function updateBubbles(dt) {
    if (!S.lrc.length) return;
    var layer = $('bubbleLayer');
    if (!layer) return;

    var cur = S.lrcIndex;
    var want = [];
    [-1, 0, 1].forEach(function (d) {
      var i = cur + d;
      if (i >= 0 && i < S.lrc.length) want.push(i);
    });

    BUBBLES = BUBBLES.filter(function (b) {
      if (want.indexOf(b.idx) < 0) {
        if (b.el && b.el.parentNode) b.el.parentNode.removeChild(b.el);
        return false;
      }
      return true;
    });

    want.forEach(function (i) {
      var exists = false;
      for (var k = 0; k < BUBBLES.length; k++) if (BUBBLES[k].idx === i) exists = true;
      if (exists) return;

      var el = document.createElement('span');
      el.className = 'bubble';
      el.textContent = S.lrc[i].text || '';

      var rel = i - cur;
      var yInit = window.innerHeight * (rel < 0 ? 0.24 : rel === 0 ? 0.50 : 0.92);
      el.style.opacity = '0';
      el.style.transform = 'translate3d(' + (window.innerWidth / 2) + 'px,' + yInit.toFixed(1) + 'px,0) translateX(-50%)';
      layer.appendChild(el);

      BUBBLES.push({
        idx: i,
        el: el,
        phase: Math.random() * Math.PI * 2,
        born: performance.now()
      });
    });

    var W = window.innerWidth;
    var H = window.innerHeight;
    var accent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';

    BUBBLES.forEach(function (b) {
      var rel = b.idx - cur;
      var yFactor = rel < 0 ? 0.24 : rel === 0 ? 0.50 : 0.76;
      var y = H * yFactor;
      var isCur = rel === 0;

      var x = W / 2 + Math.sin(S.position * 0.6 + b.phase) * 24;
      var op = (performance.now() - b.born < 120) ? 0 : (isCur ? 1 : 0.34);

      b.el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%)';
      b.el.style.opacity = op.toFixed(3);
      b.el.style.setProperty('font-size', isCur ? 'calc(50 * var(--s))' : 'calc(32 * var(--s))', 'important');
      b.el.style.color = isCur ? accent : 'rgba(255,255,255,0.72)';
      b.el.style.textShadow = isCur
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });
  }

'''

t = t[:start] + new + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("slot bubbles patched")
