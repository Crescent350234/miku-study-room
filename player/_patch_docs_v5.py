import io

root = r"D:\MikuWallpaper\_v5\Miku Study Room"
p = root + r"\README.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("# Miku Study Room · 音乐壁纸 v4.0.1", "# Miku Study Room · 音乐壁纸 v5.0")
t = t.replace("# Miku Study Room · 音乐壁纸 v4.0", "# Miku Study Room · 音乐壁纸 v5.0")

notes = '''
### v5.0 新增

- **独立桌面播放器 `Miku Player.exe`**：播放器与壁纸分离，贴在桌面上，只显示胶囊和歌词；壁纸继续用你喜欢的动态壁纸
- 播放器运行时，壁纸自动隐藏自己的胶囊和歌词（`/player-status` 协议），不会出现两套 UI
- 播放器支持鼠标点击：只在胶囊/歌词区域接收输入，其余区域穿透；`Ctrl + Alt + X` 可随时隐藏/显示播放器
- 托盘新增「打开桌面播放器」「桌面播放器开机自启」，安装器会创建开始菜单快捷方式
- **内置播放模式独立**：选择内置后不会被网易云自动切走，切歌只切本地歌单（`playMode` 持久化）
- 内置音量改成滑条（0–100，实时生效并记忆）
- 修复网易云 3.1.43 暂停状态识别；无调试端口时不再错误显示播放中
- 稳定性：页面不再自我 reload（避免 15 分钟重启循环）；频谱不可见时停止绘制；渲染进程 >750MB 静默重载；游戏运行期间暂停自动恢复
- 桌面歌词设置、纯净模式、恢复桌面图标等入口保持一致

'''
anchor = "## 使用\n"
if "v5.0 新增" not in t:
    t = t.replace(anchor, anchor + notes, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)

p2 = root + r"\使用说明.txt"
u = io.open(p2, encoding="utf-8").read()
u = u.replace("Miku Study Room 音乐壁纸 v4.0.1 · 使用说明", "Miku Study Room 音乐壁纸 v5.0 · 使用说明")
u = u.replace("Miku Study Room 音乐壁纸 v4.0 · 使用说明", "Miku Study Room 音乐壁纸 v5.0 · 使用说明")
extra = '''· 独立播放器：开始菜单「Miku 桌面播放器」，或托盘「打开桌面播放器」
  - 播放器运行时壁纸会自动隐藏自己的胶囊和歌词
  - Ctrl + Alt + X 可立即隐藏/显示播放器
· 内置音量：设置 → 内置音量滑条
· 音乐来源：设置 → 音乐来源，选择「内置播放」后不会被网易云自动切走

'''
if "独立播放器" not in u:
    u = u.replace("二、使用\n--------\n", "二、使用\n--------\n" + extra, 1)
io.open(p2, "w", encoding="utf-8", newline="").write(u)
print("docs updated")
