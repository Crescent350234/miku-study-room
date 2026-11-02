import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_tail = """    main.appendChild(wrap);
  }
"""
new_tail = """    var group = document.createElement('div');
    group.className = 'stack-group';
    group.appendChild(wrap);

    if (line.sub) {
      var subParts = splitLyricSegments(line.sub, 3);
      if (subParts.length) {
        var subV = document.createElement('div');
        subV.className = 'stack-v sub-v';
        subParts.forEach(function (part, i) {
          var col = document.createElement('div');
          col.className = 'stack-col';
          col.textContent = part;
          var visualIndex = subParts.length - 1 - i;
          col.style.transform = 'translateY(' + (-visualIndex * 26) + 'px)';
          subV.appendChild(col);
        });
        group.appendChild(subV);
      }
    }

    main.appendChild(group);
  }
"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildStackLine(idx) {")
    nxt = t.find("\n  function ", start + 10)
    if start < 0 or nxt < 0:
        print("anchor miss", d)
        continue
    fn = t[start:nxt]
    if old_tail not in fn:
        print("tail miss", d)
        continue
    fn = fn.replace(old_tail, new_tail, 1)
    t = t[:start] + fn + t[nxt:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v6：竖排翻译" not in ct:
            ct += '''

/* 云阶 v6：翻译也竖排、跟随阶梯 */
body.theme-stack .stack-group {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: calc(26 * var(--s));
  width: min(90vw, calc(1300 * var(--s)));
  margin: 0 auto;
}

body.theme-stack .stack-v.sub-v {
  height: auto;
  gap: calc(10 * var(--s));
  margin-top: calc(30 * var(--s));
  align-items: flex-end;
}

body.theme-stack .stack-v.sub-v .stack-col {
  font-size: calc(18 * var(--s)) !important;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.55) !important;
  max-height: 24vh;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=148", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
