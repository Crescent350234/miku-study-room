import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

def remove_fn(t, name):
    start = t.find("  function " + name + "(")
    if start < 0:
        return t, False
    nxt = t.find("\n  function ", start + 10)
    if nxt < 0:
        return t, False
    return t[:start] + t[nxt + 1:], True

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    for name in ["buildQingshuLine", "updateQingshu", "ensureQsTrack"]:
        pass  # keep qingshu functions

    # remove dead stack implementation
    for name in ["stackItemFor", "clearStackLayer", "updateStack"]:
        t, ok = remove_fn(t, name)
        if not ok:
            print("miss", name, d)

    # dead hanabi check in fx loop -> never true, remove drawing gate cheaply
    t = t.replace("if (document.body.classList.contains('theme-hanabi')) {", "if (false) {")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书图层只在青书显示" not in ct:
            ct += '''

/* 青书图层只在青书模式显示，避免切走后残留 */
.qs-layer {
  display: none;
}

body.theme-qingshu .qs-layer {
  display: block;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=191", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
