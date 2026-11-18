import io

p = r"D:\MikuWallpaper\installer\Installer.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''            var fontSrc = Path.Combine(baseDir, "fonts");
            if (Directory.Exists(fontSrc)) CopyDir(fontSrc, Path.Combine(dataDir, "fonts"));'''

add = '''
            var playerSrc = Path.Combine(baseDir, "player");
            if (Directory.Exists(playerSrc))
            {
                var playerDst = Path.Combine(dataDir, "DesktopPlayer");
                CopyDir(playerSrc, playerDst);
                try
                {
                    File.WriteAllText(Path.Combine(playerDst, "overlay.ini"),
                        "wallpaper=" + dst + "\\r\\n", new System.Text.UTF8Encoding(false));
                }
                catch { }
                CreateStartMenuShortcut("Miku 桌面播放器.lnk", Path.Combine(playerDst, "MikuPlayer.exe"), playerDst);
            }
'''

if "DesktopPlayer" not in t:
    t = t.replace(anchor, anchor + add, 1)
    print("installer player block added")
else:
    print("exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)
