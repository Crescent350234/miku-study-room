import io, re

root = r"D:\MikuWallpaper\_v5post\Miku Study Room"
p = root + r"\README.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("# Miku Study Room · 音乐壁纸 v5.0", "# Miku Study Room · 音乐壁纸 v5post")
notes = '''
### v5post 修复

- **修复桌面局部点不到**：桌面播放器之前把歌词可视区也当成可点击区域，生成了一块约 1300×529 的透明输入窗口，挡住下面的应用。现在只保留胶囊可点击，歌词区完全穿透
- 设置/歌单面板只在打开时临时接管输入，关闭后自动撤销；页面 3 秒未上报区域时，所有输入代理自动隐藏
- 修复托盘「打开桌面播放器」因路径转义错误提示找不到 exe；播放器安装到 `%LOCALAPPDATA%\\MikuWallpaper\\DesktopPlayer`
- 新增 `Ctrl + Alt + X`：立即隐藏/显示桌面播放器，作为挡鼠标时的应急开关

'''
anchor = "## 使用\n"
if "v5post 修复" not in t:
    t = t.replace(anchor, anchor + notes, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)

p2 = root + r"\使用说明.txt"
u = io.open(p2, encoding="utf-8").read()
u = u.replace("Miku Study Room 音乐壁纸 v5.0 · 使用说明", "Miku Study Room 音乐壁纸 v5post · 使用说明")
if "Ctrl + Alt + X" not in u:
    u = u.replace("· 独立播放器：", "· Ctrl + Alt + X：立即隐藏/显示桌面播放器\n· 独立播放器：", 1)
io.open(p2, "w", encoding="utf-8", newline="").write(u)
print("docs v5post")
