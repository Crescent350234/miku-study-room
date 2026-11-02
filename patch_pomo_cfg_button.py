import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()

    if "pomoSettingsBtn" not in t:
        t = t.replace(
            '<button class="style-chip" id="restartBridge"',
            '<button class="style-chip" id="pomoSettingsBtn">番茄钟设置</button>\n        <button class="style-chip" id="restartBridge"',
            1,
        )

    if "e.target.id === 'pomoSettingsBtn'" not in t:
        anchor = "    draw();\n  })();"
        add = """    b.addEventListener('dblclick', function () { if (cfg) cfg.classList.add('open'); });

    document.addEventListener('click', function (e) {
      if (e.target && e.target.id === 'pomoSettingsBtn') {
        if (fIn) fIn.value = m;
        if (bIn) bIn.value = (localStorage.getItem('pomoBreak') || 5);
        if (cfg) cfg.classList.add('open');
      }
    });

    draw();
  })();"""
        t = t.replace(anchor, add, 1)

    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)
