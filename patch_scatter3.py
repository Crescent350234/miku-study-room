import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = r'''    var raw = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.trim().length > 0; });
    var units = [];
    raw.forEach(function (part) {
      var arr = Array.from(part);
      for (var k = 0; k < arr.length; k += 2) units.push(arr.slice(k, k + 2).join(''));
    });
    if (!units.length) units = [text];

    var n = units.length;
    var cols = Math.min(3, Math.max(1, Math.ceil(n / 2)));
    var rows = Math.ceil(n / cols);
    var pal = lyricPalette();

    units.forEach(function (unit, i) {
      var elWord = document.createElement('span');
      elWord.className = 'sc-word';
      elWord.textContent = unit;

      var r1 = Math.abs((Math.sin(seed + i * 7) * 10000) % 1);
      var r2 = Math.abs((Math.sin(seed + i * 13) * 10000) % 1);
      var r3 = Math.abs((Math.sin(seed + i * 19) * 10000) % 1);
      var r4 = Math.abs((Math.sin(seed + i * 23) * 10000) % 1);

      var col = i % cols;
      var row = Math.floor(i / cols);
      var x = (col + 0.5) / cols * 70 + 15 + (r2 - 0.5) * 6;
      var y = (row + 0.5) / rows * 70 + 15 + (r3 - 0.5) * 6;
      var rot = (r1 - 0.5) * 20;
      var size = 1.15 + r4 * 0.55;

      elWord.style.left = x.toFixed(1) + '%';
      elWord.style.top = y.toFixed(1) + '%';
      elWord.style.fontSize = size.toFixed(2) + 'em';
      elWord.style.transform = 'translate(-50%, -50%) rotate(' + rot.toFixed(1) + 'deg)';
      elWord.style.color = lyricWordColor(unit, i, pal);
      elWord.style.opacity = '1';

      wrap.appendChild(elWord);
      S.scatterWords.push(elWord);
    });

    main.appendChild(wrap);
  }

'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    start = t.find("    var n = units.length;", t.find("function buildScatterLine"))
    end = t.find("  function paintScatter", start)
    if start >= 0 and end > start:
        t = t[:start] + new_block + t[end:]
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "心象 v3" not in ct:
            ct += '''

/* 心象 v3：中间区域散字，保留可读性 */
body.theme-scatter .scatter-wrap {
  width: 70vw;
  height: 36vh;
  margin: 0 auto;
}

body.theme-scatter .sc-word {
  font-weight: 600;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=77", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
