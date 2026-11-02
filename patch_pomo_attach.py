import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        old = "    var box = document.getElementById('pomo');"
        new = """    var box = document.getElementById('pomo');
    var playerEl = document.getElementById('player');
    if (box && playerEl && box.parentNode !== playerEl) playerEl.appendChild(box);"""
        if "playerEl.appendChild(box)" not in t:
            t = t.replace(old, new, 1)
            io.open(j, "w", encoding="utf-8", newline="").write(t)
            print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "番茄钟 v2" not in ct:
            ct += '''

/* 番茄钟 v2：挂在播放器上方，随播放器一起显示 */
.pomo {
  position: absolute !important;
  left: 50% !important;
  bottom: calc(100% + 14 * var(--s)) !important;
  transform: translateX(-50%) !important;
  z-index: 8 !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=291", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
