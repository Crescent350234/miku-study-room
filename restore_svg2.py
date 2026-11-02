import io, os, re

src = io.open(r"D:\MikuWallpaper\patch_sketch_hand.py", encoding="utf-8").read()
marker = "new_svg = r'''"
a = src.find(marker) + len(marker)
b = src.find("'''", a)
svg_fn = src[a:b]

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
    if "function buildCylinderSvg" in t:
        print("already", d)
        continue
    anchor = "  function buildCylinderLine(idx) {"
    i = t.find(anchor)
    if i < 0:
        print("anchor miss", d)
        continue
    t = t[:i] + svg_fn + "\n" + t[i:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("restored", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=276", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
