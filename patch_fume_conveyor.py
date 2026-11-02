import io, os

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

start = t.find("  function spawnBubbles(")
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

      var y, op;
      if (p <= 0) {
        y = H * 0.98;
        op = 0.10;
      } else if (p < 0.30) {
        var q = p / 0.30;
        var e = 1 - Math.pow(1 - q, 3);
        y = H * 0.98 + (H * 0.46 - H * 0.98) * e;
        op = 0.10 + 0.90 * q;
      } else if (p < 0.80) {
        y = H * 0.46;
        op = 1;
      } else if (p < 1.05) {
        var q2 = (p - 0.80) / 0.25;
        y = H * 0.46 + (H * 0.10 - H * 0.46) * q2;
        op = 1 - q2;
      } else {
        y = H * 0.10;
        op = 0;
      }

      var isCur = b.idx === S.lrcIndex;
      var x = W / 2 + Math.sin(S.position * 0.8 + b.phase) * 12;

      b.el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%)';
      b.el.style.opacity = Math.max(0, Math.min(1, op)).toFixed(3);
      b.el.style.fontSize = isCur ? 'calc(34 * var(--s))' : 'calc(24 * var(--s))';
      b.el.style.color = (isCur && p > 0.2 && p < 0.85) ? accent : '#ffffff';
      b.el.style.textShadow = (isCur && p > 0.2 && p < 0.85)
        ? '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(24 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });
  }

'''

t = t[:start] + new + t[end:]

# fume branch: no manual spawn, updateBubbles handles it
t = t.replace(
    "if (S.lyricTheme === 'fume') { var __ln = S.lrc[idx]; var __nx = S.lrc[idx + 1]; spawnBubbles(__ln ? __ln.text : '', __ln ? __ln.t : 0, __nx ? __nx.t : (__ln ? __ln.t + 4 : 4)); return; }",
    "if (S.lyricTheme === 'fume') { return; }"
)

# remove old respawn guard
guard = """    if (S.lyricTheme === 'fume' && idx >= 0 && S.bubbleLine !== idx) {
      S.bubbleLine = idx;
      var __l2 = S.lrc[idx]; var __n2 = S.lrc[idx + 1];
      spawnBubbles(__l2 ? __l2.text : '', __l2 ? __l2.t : 0, __n2 ? __n2.t : (__l2 ? __l2.t + 4 : 4));
    }
"""
t = t.replace(guard, "")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fume conveyor patched")
