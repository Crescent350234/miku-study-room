import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_fonts = """  var LYRIC_FONTS = [
    { id: 'sans', name: '黑体' },
    { id: 'serif', name: '宋体' },
    { id: 'kai', name: '楷体' },
    { id: 'fangsong', name: '仿宋' },
    { id: 'dengxian', name: '等线' },
    { id: 'youyuan', name: '幼圆' },
    { id: 'mono', name: '等宽' },
    { id: 'lishu', name: '隶书' }
  ];"""

new_fonts = """  var LYRIC_FONTS = [
    { id: 'sans', name: '现代' },
    { id: 'hei', name: '黑体' },
    { id: 'serif', name: '宋体' },
    { id: 'dengxian', name: '等线' },
    { id: 'youyuan', name: '圆体' },
    { id: 'light', name: '细体' }
  ];"""

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if old_fonts in t:
            t = t.replace(old_fonts, new_fonts)
        # fallback for old saved ids
        if "if (!LYRIC_FONTS.some" not in t:
            t = t.replace("  function applyLyricFont(id) {",
                          "  function applyLyricFont(id) {\n    var __ok = false;\n    for (var __i = 0; __i < LYRIC_FONTS.length; __i++) if (LYRIC_FONTS[__i].id === id) __ok = true;\n    if (!__ok) id = 'sans';")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "Miku Sans" not in ct:
            ct += '''

/* ---------------- 内置 MiSans + 新字体栈 ---------------- */
@font-face {
  font-family: "Miku Sans";
  src: url("../assets/fonts/MiSans-Regular.otf") format("opentype");
  font-weight: 100 900;
  font-display: swap;
}

body.font-sans .line, body.font-sans .line .main {
  font-family: "Miku Sans", "MiSans", "Noto Sans SC", "Microsoft YaHei UI", sans-serif;
  font-weight: 500;
  letter-spacing: 0.02em;
}

body.font-hei .line, body.font-hei .line .main {
  font-family: "Noto Sans SC", "Microsoft YaHei UI", sans-serif;
  font-weight: 700;
}

body.font-serif .line, body.font-serif .line .main {
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  font-weight: 500;
  letter-spacing: 0.03em;
}

body.font-dengxian .line, body.font-dengxian .line .main {
  font-family: "DengXian", "Microsoft YaHei UI", sans-serif;
  font-weight: 400;
}

body.font-youyuan .line, body.font-youyuan .line .main {
  font-family: "YouYuan", "Microsoft YaHei UI", sans-serif;
  font-weight: 400;
  letter-spacing: 0.04em;
}

body.font-light .line, body.font-light .line .main {
  font-family: "Noto Sans SC Light", "MiSans Light", "Microsoft YaHei UI Light", sans-serif;
  font-weight: 300;
  letter-spacing: 0.06em;
}

/* 当前行字重更稳 */
body.font-sans .line.active { font-weight: 600; }
body.font-hei .line.active { font-weight: 800; }
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=57", t)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
