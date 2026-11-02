import io, os

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

start = t.find("  function spawnBubbles(text) {")
end = t.find("  function buildFumeLine", start)
if start < 0 or end < 0:
    raise SystemExit("spawn anchor miss")

new = r'''  function spawnBubbles(text, t0, t1) {
    var layer = $('bubbleLayer');
    if (!layer || !text) return;

    layer.innerHTML = '';
    BUBBLES = [];

    var el = document.createElement('span');
    el.className = 'bubble';
    el.textContent = String(text);
    el.style.opacity = '0';
    el.style.transform = 'translate3d(' + (window.innerWidth / 2) + 'px,' + (window.innerHeight * 0.82) + 'px,0) translateX(-50%)';
    layer.appendChild(el);

    BUBBLES.push({
      el: el,
      t0: t0 || 0,
      t1: t1 || (t0 || 0) + 4,
      phase: Math.random() * Math.PI * 2
    });
  }

  function updateBubbles(dt) {
    if (!BUBBLES.length) return;

    var b = BUBBLES[0];
    var el = b.el;
    if (!el) { BUBBLES = []; return; }

    var pos = S.position;
    var dur = Math.max(1.5, b.t1 - b.t0);
    var p = (pos - b.t0) / dur;

    var W = window.innerWidth;
    var H = window.innerHeight;
    var startY = H * 0.82;
    var centerY = H * 0.46;
    var endY = H * 0.16;

    var y;
    if (p < 0.22) {
      var q = Math.max(0, p) / 0.22;
      var e = 1 - Math.pow(1 - q, 3);
      y = startY + (centerY - startY) * e;
    } else if (p < 0.82) {
      y = centerY;
    } else {
      var q2 = Math.min(1, (p - 0.82) / 0.18);
      y = centerY + (endY - centerY) * q2;
    }

    var fade = 1;
    if (p < 0.12) fade = Math.max(0, p) / 0.12;
    else if (p > 0.9) fade = Math.max(0, (1.05 - p) / 0.15);

    var x = W / 2 + Math.sin(pos * 0.9 + b.phase) * 16;

    el.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0) translateX(-50%)';
    el.style.opacity = Math.max(0, Math.min(1, fade)).toFixed(3);

    var accent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';
    el.style.color = (p > 0.14 && p < 0.86) ? accent : '#ffffff';
    el.style.textShadow = (p > 0.14 && p < 0.86)
      ? '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(24 * var(--s)) rgba(0,0,0,0.5)'
      : '0 calc(4 * var(--s)) calc(20 * var(--s)) rgba(0,0,0,0.45)';

    if (p > 1.08) {
      if (el.parentNode) el.parentNode.removeChild(el);
      BUBBLES = [];
      if (S.lrc && S.lrcIndex >= 0) S.bubbleLine = S.lrcIndex;
    }
  }

'''

t = t[:start] + new + t[end:]

# buildActiveChars fume call with times
t = t.replace(
    "if (S.lyricTheme === 'fume') { spawnBubbles(S.lrc[idx] ? S.lrc[idx].text : ''); return; }",
    "if (S.lyricTheme === 'fume') { var __ln = S.lrc[idx]; var __nx = S.lrc[idx + 1]; spawnBubbles(__ln ? __ln.text : '', __ln ? __ln.t : 0, __nx ? __nx.t : (__ln ? __ln.t + 4 : 4)); return; }"
)

# respawn guard also pass times
t = t.replace(
    "      spawnBubbles(S.lrc[idx] ? S.lrc[idx].text : '');",
    "      var __l2 = S.lrc[idx]; var __n2 = S.lrc[idx + 1];\n      spawnBubbles(__l2 ? __l2.text : '', __l2 ? __l2.t : 0, __n2 ? __n2.t : (__l2 ? __l2.t + 4 : 4));"
)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("fume sync bubble patched")
