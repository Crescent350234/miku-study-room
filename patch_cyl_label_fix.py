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

    t = t.replace(
        "'rotate(' + slots[s].a + 'deg) translateY(calc(-196 * var(--s))) rotate(-90deg)'",
        "'rotate(' + slots[s].a + 'deg) translateY(calc(-0.313 * min(58vw, calc(920 * var(--s))))) rotate(-90deg)'",
    )
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v29" not in ct:
            ct += '''

/* 弹巢 v29：歌词从弹孔处开始，保持可见 */
.cyl5-label-inner {
  white-space: nowrap !important;
  opacity: 1 !important;
}

.cyl5-label.current .cyl5-label-inner {
  font-size: calc(42 * var(--s)) !important;
  animation-name: cylRadialFire2 !important;
  animation-fill-mode: forwards;
}

@keyframes cylRadialFire2 {
  0%   { opacity: 1; transform: translateX(0); }
  60%  { opacity: 1; transform: translateX(0); }
  80%  { opacity: 1; transform: translateX(10vw); }
  100% { opacity: 0; transform: translateX(40vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=271", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
