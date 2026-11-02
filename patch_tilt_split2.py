import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = r'''    var parts = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length < 2) {
      var mid = Math.ceil(text.length / 2);
      parts = [text.slice(0, mid), text.slice(mid)];
    }
    parts = parts.slice(0, 4).filter(function (s) { return s.length > 0; });'''

new = r'''    var parts = splitLyricSegments(text, 3);'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("patched", p)
    else:
        print("miss", p)
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=130", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
