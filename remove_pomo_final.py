import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "index.html")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    # 1) 删除网页内番茄钟 div
    i = t.find('<div id="pomo" class="pomo"')
    if i >= 0:
        j = t.find('</div>', i)
        if j >= 0:
            t = t[:i] + t[j + len('</div>'):]

    # 2) 删除内联番茄钟脚本
    t = re.sub(
        r"<script>\s*\(function \(\) \{\s*var b = document\.getElementById\('pomo'\);.*?</script>",
        "",
        t,
        flags=re.S,
    )

    # 3) 删除 pomoCfg 面板（到 start-hint 之前）
    i = t.find('<div id="pomoCfg"')
    if i >= 0:
        j = t.find('<div class="start-hint"', i)
        if j >= 0:
            t = t[:i] + t[j:]

    # 4) 删除设置面板里的番茄钟设置按钮
    t = t.replace('<button class="style-chip" id="pomoSettingsBtn">番茄钟设置</button>\n        ', '')

    # 5) 删除末尾隐藏样式
    t = re.sub(
        r"\s*<style>\s*#pomo,\s*#pomoCfg,\s*#pomoSettingsBtn\s*\{[^}]*\}\s*</style>",
        "",
        t,
        flags=re.S,
    )

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("cleaned", d)
