import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

hook = """  window.addEventListener('error', function (e) {
    try { document.documentElement.setAttribute('data-err', (e.message || '') + ' @' + (e.filename || '') + ':' + (e.lineno || 0)); } catch (x) {}
  });

"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if "data-err" not in t:
        idx = t.find("(function () {")
        if idx >= 0:
            t = t[:idx + len("(function () {")] + "\n" + hook + t[idx + len("(function () {"):]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=200", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
