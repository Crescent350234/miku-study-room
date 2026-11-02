import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = """      var parts = splitLyricSegments(line.text, 2);
      if (!parts.length) parts = [line.text];

      parts.forEach(function (part) {
        var col = document.createElement('div');
        col.className = 'stack-col';
        col.textContent = part;
        if (cls === 'current') {
          col.style.color = accent;
          col.style.textShadow = '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(8 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.45)';
        }
        inner.appendChild(col);
      });"""

new = """      var sv = Math.min(window.innerWidth * 0.000390625, window.innerHeight * 0.00069444) || 1;
      var basePx = (cls === 'current' ? 46 : 30) * sv;
      var maxChars = Math.max(2, Math.floor(window.innerHeight * 0.19 / basePx));

      var parts = line.text.length <= maxChars ? [line.text] : splitLyricSegments(line.text, 2);
      if (!parts.length) parts = [line.text];

      parts.forEach(function (part, pi) {
        var col = document.createElement('div');
        col.className = 'stack-col';
        col.textContent = part;

        if (pi === 1) {
          col.style.transform = 'translateY(' + (cls === 'current' ? 64 : 42) + 'px) rotate(-2.4deg)';
        }

        var cpx = basePx;
        if (part.length * cpx > window.innerHeight * 0.19) {
          cpx = window.innerHeight * 0.19 / Math.max(2, part.length);
          col.style.setProperty('font-size', cpx.toFixed(1) + 'px', 'important');
        }

        if (cls === 'current') {
          col.style.color = accent;
          col.style.textShadow = '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(8 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.45)';
        }
        inner.appendChild(col);
      });"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v15" not in ct:
            ct += '''

/* 云阶 v15：一列优先，最多两列，错开成平行四边形 */
body.theme-stack .stack-col {
  max-height: 21vh !important;
}

body.theme-stack .stack-pair.current .stack-col {
  font-size: calc(46 * var(--s)) !important;
}

body.theme-stack .stack-inner {
  align-items: flex-start !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=158", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
