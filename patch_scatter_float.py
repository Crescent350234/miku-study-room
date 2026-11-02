import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildScatterLine(idx) {")
    end = t.find("\n  function ", start + 10)
    if start < 0 or end < 0:
        print("anchor miss", d)
        continue
    fn = t[start:end]

    old = "      wrap.appendChild(sp);"
    new = """      var floatWrap = document.createElement('span');
      floatWrap.className = 'sc-float';
      floatWrap.style.setProperty('--ax', (4 + r * 10).toFixed(1) + 'px');
      floatWrap.style.setProperty('--ay', (3 + r2 * 9).toFixed(1) + 'px');
      floatWrap.style.setProperty('--ar', (1.2 + r3 * 3.2).toFixed(2) + 'deg');
      floatWrap.style.setProperty('--dur', (3.2 + r * 4.5).toFixed(2) + 's');
      floatWrap.style.setProperty('--delay', (-r2 * 3).toFixed(2) + 's');
      floatWrap.appendChild(sp);
      wrap.appendChild(floatWrap);"""
    if old in fn:
        fn = fn.replace(old, new)
        t = t[:start] + fn + t[end:]
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "心象：单字不规则飘动" not in ct:
            ct += '''

/* 心象：单字不规则飘动 */
.sc-float {
  display: inline-block;
  animation: scFloat var(--dur, 5s) ease-in-out var(--delay, 0s) infinite alternate;
  will-change: transform;
}

@keyframes scFloat {
  from {
    transform: translate(calc(-1 * var(--ax, 6px)), calc(-1 * var(--ay, 5px)))
               rotate(calc(-1 * var(--ar, 2deg)));
  }
  to {
    transform: translate(var(--ax, 6px), var(--ay, 5px)) rotate(var(--ar, 2deg));
  }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=214", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
