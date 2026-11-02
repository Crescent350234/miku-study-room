import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = r'''    var n = units.length;
    var cols = Math.max(2, Math.min(5, Math.ceil(Math.sqrt(n * 1.4))));
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
      var x = (col + 0.5) / cols * 84 + 8 + (r2 - 0.5) * 8;
      var y = (row + 0.5) / rows * 76 + 12 + (r3 - 0.5) * 8;
      var rot = (r1 - 0.5) * 30;
      var size = 1.05 + r4 * 1.25;

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

    start = t.find("    var per = dur / Math.max(1, units.length);")
    end = t.find("  function paintScatter", start)
    if start >= 0 and end > start:
        t = t[:start] + new_block + t[end:]
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("scatter anchor miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "心象 v2：满屏散字" not in ct:
            ct += '''

/* ---------------- 心象 v2：满屏散字 ---------------- */
body.theme-scatter .scatter-wrap {
  position: relative;
  display: block;
  width: 88vw;
  height: 48vh;
  margin: 0 auto;
  padding: 0;
}

body.theme-scatter .sc-word {
  position: absolute;
  display: block;
  line-height: 1;
  white-space: nowrap;
  text-shadow: 0 calc(6 * var(--s)) calc(28 * var(--s)) rgba(0, 0, 0, 0.45);
  transform-origin: center center;
}

/* ---------------- 云阶 v2：大小悬殊 ---------------- */
body.theme-stack .stack-seg.big {
  font-size: 2.15em !important;
  font-weight: 700;
  letter-spacing: 0.01em;
}

body.theme-stack .stack-seg:not(.big) {
  font-size: 0.52em !important;
  opacity: 0.75;
  letter-spacing: 0.14em;
}

body.theme-stack .stack-seg:nth-child(even) {
  margin-left: 10%;
}

body.theme-stack .stack-seg:nth-child(odd) {
  margin-right: 10%;
}

/* ---------------- 倾诉 v2：错位更明显 ---------------- */
body.theme-tilt .tilt-seg.tilt {
  font-size: 1.9em !important;
  font-weight: 300;
  letter-spacing: 0.12em;
}

body.theme-tilt .tilt-seg:not(.tilt) {
  font-size: 0.55em !important;
  opacity: 0.8;
  letter-spacing: 0.22em;
}

body.theme-tilt .tilt-seg.tilt .tc.up { transform: translateY(-0.24em); }
body.theme-tilt .tilt-seg.tilt .tc.down { transform: translateY(0.24em); }

/* ---------------- 浮名 v2：三行落差 ---------------- */
body.theme-fume .fume-row.r0 { font-size: 1.45em !important; }
body.theme-fume .fume-row.r1 { font-size: 2.05em !important; }
body.theme-fume .fume-row.r2 { font-size: 0.95em !important; opacity: 0.7; }

/* ---------------- 流光 v2：更大更亮 ---------------- */
body.theme-lumiere .lumi-line {
  font-size: 1.45em !important;
  letter-spacing: 0.08em;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=74", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
