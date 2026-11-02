import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

style = '''<style id="pomoInline">
#pomo, #pomoCfg, #pomoSettingsBtn { display: none !important; }
body.focus #settingsPanel,
body.focus #drawer,
body.focus .chips,
body.focus .settings,
body.focus #cleanCover { display: none !important; }
</style>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()
    if 'id="pomoInline"' not in t:
        t = t.replace("</head>", style + "</head>", 1)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
        print("html", d)
