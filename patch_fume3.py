import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = r'''    var parts = text.split(/[，。！？、；：]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length === 1) {
      var mid = Math.max(2, Math.round(text.length * 0.6));
      parts = [text.slice(0, mid), text.slice(mid)].filter(function (s) { return s.trim().length > 0; });
    }

    parts = parts.slice(0, 3);
    var sorted = parts.slice().sort(function (a, b) { return b.length - a.length; });
    var big = sorted[0] || text;
    var smalls = sorted.slice(1);

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'fume-wrap';

    if (smalls[0]) {
      var r0 = document.createElement('div');
      r0.className = 'fume-row r0';
      r0.textContent = smalls[0];
      wrap.appendChild(r0);
    }

    var r1 = document.createElement('div');
    r1.className = 'fume-row r1';
    r1.textContent = big;
    wrap.appendChild(r1);

    if (smalls[1]) {
      var r2 = document.createElement('div');
      r2.className = 'fume-row r2';
      r2.textContent = smalls[1];
      wrap.appendChild(r2);
    }

    main.appendChild(wrap);
  }

'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    start = t.find("    var parts = text.split(/[，。！？、；：]+/)", t.find("function buildFumeLine"))
    end = t.find("  function buildLumiLine", start)
    if start >= 0 and end > start:
        t = t[:start] + new_block + t[end:]
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "浮名 v3：杂志排版" not in ct:
            ct += '''

/* ---------------- 浮名 v3：杂志式排版 ---------------- */
@keyframes fumeRise {
  from { translate: 0 6px; }
  to   { translate: 0 -6px; }
}

body.theme-fume .fume-wrap {
  position: relative;
  width: min(64vw, calc(880 * var(--s))) !important;
  max-width: 64vw !important;
  margin: 0 auto !important;
  padding-left: calc(20 * var(--s));
  text-align: left;
  animation: fumeRise 8s ease-in-out infinite alternate;
}

body.theme-fume .fume-wrap::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6%;
  bottom: 6%;
  width: calc(2 * var(--s));
  background: linear-gradient(180deg, transparent, var(--accent, #3cc5bb), transparent);
  opacity: 0.65;
}

body.theme-fume .fume-row.r0 {
  font-size: 0.5em !important;
  letter-spacing: 0.32em;
  opacity: 0.55;
  margin-bottom: calc(6 * var(--s));
  font-weight: 400 !important;
}

body.theme-fume .fume-row.r1 {
  font-size: 2.1em !important;
  font-weight: 700 !important;
  line-height: 1.08;
  letter-spacing: 0.02em;
  color: #ffffff;
  text-shadow: 0 calc(8 * var(--s)) calc(34 * var(--s)) rgba(0, 0, 0, 0.5);
  margin-bottom: calc(8 * var(--s));
}

body.theme-fume .fume-row.r2 {
  font-size: 0.72em !important;
  letter-spacing: 0.18em;
  color: var(--accent, #3cc5bb) !important;
  opacity: 0.95;
}

body.theme-fume .fume-row.r1::after {
  content: '';
  display: block;
  width: 38%;
  height: 1px;
  margin-top: calc(12 * var(--s));
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.55), transparent);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=86", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
