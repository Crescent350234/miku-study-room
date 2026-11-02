import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = """(line.sub ? '<span class="sub">' + colorizeSub(line.sub) + '</span>' : '')"""
new = """(line.sub ? '<span class="sub">' + (S.lyricTheme === 'lumiere' ? colorizeSub(line.sub) : esc(line.sub)) + '</span>' : '')"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
    else:
        print("render anchor miss", d)

    if "if (S.lrc && S.lrc.length) renderLyrics(S.lrc);" not in t:
        t = t.replace("    S.lyricTheme = id;", "    S.lyricTheme = id;\n    if (S.lrc && S.lrc.length) renderLyrics(S.lrc);")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=126", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
