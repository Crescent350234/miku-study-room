import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_req = "'要求：accent 与 background 对比明显；wordColors 8-12 个，词必须出现在歌词里；整体贴合情绪。\\n'"
new_req = "'要求：accent 与 background 对比明显；wordColors 8-12 个；lineKeywords 尽量覆盖每一句，keyword 必须是该句中最有情绪、最具体的 2-5 字词语（不要选“他/我/就/把”这类虚词开头的半截词）；整体贴合情绪。\\n'"

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    t = t.replace("var cacheKey = 'aiTheme:v2:' + d.id;", "var cacheKey = 'aiTheme:v3:' + d.id;")
    if old_req in t:
        t = t.replace(old_req, new_req)
    else:
        print("req miss", d)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=142", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
