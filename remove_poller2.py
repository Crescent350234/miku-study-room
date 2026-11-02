import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

style = '''  <style>
  #pomo, #pomoCfg, #pomoSettingsBtn { display: none !important; }
  </style>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()
    t = re.sub(r"<script>\s*\(function \(\) \{\s*function poll\(\).*?</script>", style.strip(), t, flags=re.S)
    if "#pomo, #pomoCfg, #pomoSettingsBtn" not in t:
        t = t.replace("</body>", style + "\n</body>", 1)
    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)
