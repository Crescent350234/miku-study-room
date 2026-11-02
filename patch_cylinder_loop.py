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

    old = "    updateBubbles(dt);\n    updateQingshu();"
    new = """    updateBubbles(dt);
    updateQingshu();

    if (S.lyricTheme === 'cylinder' && S.lrcIndex >= 0 && S.cylBuiltIdx !== S.lrcIndex) {
      S.cylBuiltIdx = S.lrcIndex;
      buildCylinderLine(S.lrcIndex);
    }"""
    if "cylBuiltIdx" not in t and old in t:
        t = t.replace(old, new, 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=268", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
