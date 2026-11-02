import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = """      if (i === tiltIdx) {
        Array.from(part).forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc ' + (ci % 2 ? 'up' : 'down');
          c.textContent = ch;
          seg.appendChild(c);
        });
      } else {
        seg.textContent = part;
      }"""

new = """      if (i === tiltIdx) {
        Array.from(part).forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc ' + (ci % 2 ? 'up' : 'down');
          c.textContent = ch;
          seg.appendChild(c);
        });
      } else {
        var chars = Array.from(part);
        var hlStart = Math.max(0, Math.floor((chars.length - 2) / 2));
        chars.forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc2';
          if (ci >= hlStart && ci < hlStart + 2) c.className += ' tilt-hl';
          c.textContent = ch;
          var rr = Math.abs((Math.sin(seed + i * 17 + ci * 5) * 10000) % 1);
          c.style.transform = 'translateY(' + ((rr - 0.5) * 6).toFixed(1) + 'px) rotate(' + ((rr - 0.5) * 5).toFixed(1) + 'deg)';
          seg.appendChild(c);
        });
      }"""

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
        if "倾诉小字突出" not in ct:
            ct += '''

/* 倾诉小字：放大、略错落、突出一个词 */
body.theme-tilt .tilt-seg:not(.tilt) {
  font-size: 0.72em !important;
  letter-spacing: 0.16em;
  opacity: 0.9;
}

body.theme-tilt .tc2 {
  display: inline-block;
  white-space: pre;
}

body.theme-tilt .tilt-hl {
  color: var(--accent, #7fd6ff) !important;
  font-weight: 700;
  text-shadow: 0 0 calc(16 * var(--s)) rgba(255, 255, 255, 0.12);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=132", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
