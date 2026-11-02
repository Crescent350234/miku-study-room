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
    old = """    { id: 'youyuan', name: '圆体' },
    { id: 'light', name: '细体' }
  ];"""
    new = """    { id: 'youyuan', name: '圆体' },
    { id: 'light', name: '细体' },
    { id: 'kai', name: '楷体' },
    { id: 'fangsong', name: '仿宋' },
    { id: 'lishu', name: '隶书' },
    { id: 'mono', name: '等宽' }
  ];"""
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "新增字体：气泡与青书" not in ct:
            ct += '''

/* 新增字体：气泡与青书同步 */
body.font-kai .bubble,
body.font-kai .qs-line,
body.font-kai .qs-col,
body.font-kai .tilt-key {
  font-family: "KaiTi", "STKaiti", "Kaiti SC", serif !important;
}

body.font-fangsong .bubble,
body.font-fangsong .qs-line,
body.font-fangsong .qs-col,
body.font-fangsong .tilt-key {
  font-family: "FangSong", "STFangsong", "FangSong_GB2312", serif !important;
}

body.font-lishu .bubble,
body.font-lishu .qs-line,
body.font-lishu .qs-col,
body.font-lishu .tilt-key {
  font-family: "LiSu", "STLiti", "LiSu Pro", serif !important;
}

body.font-mono .bubble,
body.font-mono .qs-line,
body.font-mono .qs-col,
body.font-mono .tilt-key {
  font-family: "Cascadia Mono", "Consolas", "Noto Sans Mono CJK SC", monospace !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=216", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
