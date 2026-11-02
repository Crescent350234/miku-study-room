import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = r'''    var chars = Array.from(text).filter(function (ch) { return !/\s/.test(ch); });
    var pal = lyricPalette();

    chars.forEach(function (ch, i) {
      var sp = document.createElement('span');
      sp.className = 'sc-word';
      sp.textContent = ch;

      var r = Math.abs((Math.sin(seed + i * 7) * 10000) % 1);
      sp.style.fontSize = (1.0 + r * 0.3).toFixed(2) + 'em';
      sp.style.transform = 'rotate(' + ((r - 0.5) * 8).toFixed(1) + 'deg)';
      sp.style.color = (i % 4 === 2) ? pal[1] : '#ffffff';

      wrap.appendChild(sp);
      S.scatterWords.push(sp);
    });

    main.appendChild(wrap);
  }

'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    start = t.find("    var raw = text.split", t.find("function buildScatterLine"))
    end = t.find("  function paintScatter", start)
    if start >= 0 and end > start:
        t = t[:start] + new_block + t[end:]
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "心象 v4：单行居中" not in ct:
            ct += '''

/* ---------------- 心象 v4：单行居中、字距拉开 ---------------- */
body.theme-scatter .scatter-wrap {
  display: flex !important;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.02em 0.14em;
  width: 86vw !important;
  height: auto !important;
  margin: 0 auto !important;
  padding: 0 !important;
}

body.theme-scatter .sc-word {
  position: static !important;
  left: auto !important;
  top: auto !important;
  display: inline-block;
  line-height: 1.12;
  white-space: nowrap;
  font-weight: 600;
  opacity: 1 !important;
  text-shadow: 0 calc(4 * var(--s)) calc(22 * var(--s)) rgba(0, 0, 0, 0.42);
}

body.theme-scatter .line.active {
  text-align: center;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=81", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
