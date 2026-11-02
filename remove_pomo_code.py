import io, os, re

# ---- 1) app.js 删除 initPomodoro 块 ----
js_dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in js_dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    start = t.find("  (function initPomodoro() {")
    if start >= 0:
        # 找到这个 IIFE 自己的收尾 "  })();\n"（后面紧跟主 IIFE 的 })();）
        end_marker = "    render();\n  })();\n"
        end = t.find(end_marker, start)
        if end < 0:
            end_marker2 = "    render();\n  })();"
            end = t.find(end_marker2, start)
            if end >= 0:
                end += len(end_marker2)
        if end >= 0:
            t = t[:start] + t[end:]
        else:
            print("end marker miss", d)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js cleaned", d)

# ---- 2) bridge.cs 删除 /pomo.json 路由 ----
bp = r"D:\MikuWallpaper\bridge\bridge.cs"
bt = io.open(bp, encoding="utf-8").read()
anchor = 'else if (path.StartsWith("/pomo.json"))'
start = bt.find(anchor)
if start >= 0:
    # 向前找到上一行 else if 的换行起点
    line_start = bt.rfind("\n", 0, start) + 1
    # 找到该块结束的 "}" 之后的 "\n"
    end = bt.find("\n                        else", start)
    if end < 0:
        end = bt.find("\n                        else if", start)
    if end < 0:
        end = bt.find("\n                        else\n", start)
    if end >= 0:
        bt = bt[:line_start] + bt[end:]
    else:
        print("bridge end miss")
else:
    print("bridge pomo route already gone")
io.open(bp, "w", encoding="utf-8", newline="").write(bt)
print("bridge cleaned")
