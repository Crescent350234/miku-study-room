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
      el.style.opacity = '0';
      layer.appendChild(el);

      BUBBLES.push({
        idx: i,
        el: el,
        t0: S.lrc[i].t,
        t1: S.lrc[i + 1] ? S.lrc[i + 1].t : S.lrc[i].t + 4,
        phase: Math.random() * Math.PI * 2
      });
    });

    var W = window.innerWidth;
    var H = window.innerHeight;
    var accent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';

    BUBBLES.forEach(function (b) {
      var dur = Math.max(1.5, b.t1 - b.t0);
      var p = (S.position - b.t0) / dur;
      var isCur = b.idx === S.lrcIndex;

      var y, op;
      if (p <= 0) {
        y = H * 0.74;
        op = 0.35;
      } else if (p < 0.45) {
        var q = p / 0.45;
        var e = 1 - Math.pow(1 - q, 3);
        y = H * 0.95 + (H * 0.46 - H * 0.95) * e;
        op = 0.35 + 0.65 * q;
      } else if (p < 0.85) {
        y = H * 0.46;
        op = 1;
      } else if (p < 1.20) {
        var q2 = (p - 0.85) / 0.35;
        y = H * 0.46 + (H * 0.12 - H * 0.46) * q2;
        op = 1 - q2;
      } else {
        y = H * 0.12;
        op = 0;
      }

      var x = W / 2 + Math.sin(S.position * 0.55 + b.phase) * 42;

      b.el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%)';
      b.el.style.opacity = Math.max(0, Math.min(1, op)).toFixed(3);
      b.el.style.fontSize = isCur ? 'calc(46 * var(--s))' : 'calc(32 * var(--s))';
      b.el.style.color = (isCur && p > 0.25 && p < 0.85) ? accent : '#ffffff';
      b.el.style.textShadow = (isCur && p > 0.25 && p < 0.85)
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });
  }

'''

t = t[:start] + new + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fume sizes/positions patched")
