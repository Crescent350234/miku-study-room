import io, os

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
    t = t.replace("var endAngle = -(idx * 60);", "var endAngle = (idx * 60);")
    t = t.replace(
        "wheel.style.transform = 'rotate(' + (endAngle - 60) + 'deg)';",
        "wheel.style.transform = 'rotate(' + (endAngle + 60) + 'deg)';",
    )
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)
