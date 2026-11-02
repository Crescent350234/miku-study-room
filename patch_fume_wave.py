import io

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

old = """      var el = document.createElement('span');
      el.className = 'bubble';
      el.textContent = S.lrc[i].text || '';

      var rel = i - cur;"""
new = """      var el = document.createElement('span');
      el.className = 'bubble';
      Array.from(S.lrc[i].text || '').forEach(function (ch) {
        var cs = document.createElement('span');
        cs.className = 'bch';
        cs.textContent = ch === ' ' ? '\\u00a0' : ch;
        el.appendChild(cs);
      });

      var rel = i - cur;"""
if old in t:
    t = t.replace(old, new)
else:
    print("creation anchor miss")

old2 = """      b.el.style.textShadow = isCur
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';
    });"""
new2 = """      b.el.style.textShadow = isCur
        ? '0 0 calc(30 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.5)'
        : '0 calc(4 * var(--s)) calc(18 * var(--s)) rgba(0,0,0,0.45)';

      for (var ci = 0; ci < b.el.children.length; ci++) {
        var chEl = b.el.children[ci];
        var wy = Math.sin(tt * 2.1 + ci * 0.72 + b.phase) * 7;
        var wr = Math.sin(tt * 1.7 + ci * 0.55 + b.phase) * 2.2;
        chEl.style.transform = 'translateY(' + wy.toFixed(2) + 'px) rotate(' + wr.toFixed(2) + 'deg)';
      }
    });"""
if old2 in t:
    t = t.replace(old2, new2)
else:
    print("update anchor miss")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("wave chars patched")
