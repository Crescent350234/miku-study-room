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

    t = t.replace("fill: 'rgba(17, 18, 17, 0.82)'", "fill: 'rgba(214, 232, 226, 0.05)'")
    t = t.replace("'rgba(222, 220, 210, 0.10)'", "'rgba(222, 220, 210, 0.05)'")
    t = t.replace("'rgba(222, 220, 210, 0.06)'", "'rgba(222, 220, 210, 0.03)'")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=264", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
