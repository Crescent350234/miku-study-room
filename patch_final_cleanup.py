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

    # remove debug probes
    t = re.sub(r"\n\s*document\.documentElement\.setAttribute\('data-step', '[A-E]'\);", "", t)
    t = re.sub(r"\n  window\.addEventListener\('error', function \(e\) \{\n    try \{ document\.documentElement\.setAttribute\('data-err'.*?\n  \}\);\n", "\n", t, flags=re.S)

    # respect saved lyric theme
    t = t.replace("""    var savedTheme = 'plain';
    applyLyricTheme(savedTheme);""", """    var savedTheme = 'plain';
    try { savedTheme = localStorage.getItem('lyricTheme') || 'plain'; } catch (e) {}
    applyLyricTheme(savedTheme);""")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=204", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
