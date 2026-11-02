import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_style = '''<style id="pomoInline">
#pomo, #pomoCfg, #pomoSettingsBtn { display: none !important; }
</style>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()

    t = re.sub(r'<style id="pomoInline">.*?</style>', new_style, t, flags=re.S)

    # 移除壁纸内的专注轮询脚本
    t = re.sub(r"\s*<script>\s*\(function \(\) \{\s*var ports = \[51789.*?</script>", "", t, flags=re.S)

    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)
