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

    old_start = "  (function setupGuideAndRestart() {"
    new_start = "  document.addEventListener('DOMContentLoaded', function setupGuideAndRestart() {"
    if old_start in t:
        t = t.replace(old_start, new_start, 1)
        idx = t.find(new_start)
        end = t.find("  })();", idx)
        if end >= 0:
            t = t[:end] + "  });" + t[end + len("  })();"):]
        else:
            print("end miss", d)
    else:
        print("start miss", d)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=203", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
