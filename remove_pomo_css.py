import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "css", "style.css")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    # 删掉我追加的番茄钟样式（从第一个番茄钟注释到文件尾）
    i = t.find("/* ---------------- 番茄钟")
    if i >= 0:
        t = t[:i].rstrip() + "\n"

    # 删掉旧的 .pomodoro 相关规则
    t = re.sub(r"\.pomodoro[^{]*\{[^}]*\}", "", t)
    t = re.sub(r"\.pomodoro\.break \.ring-fg \{[^}]*\}", "", t)
    t = re.sub(r"body\.clean-wallpaper \.pomo \{[^}]*\}", "", t)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("css cleaned", d)
