import io

p = r"D:\MikuWallpaper\tray\TrayCenter.cs"
t = io.open(p, encoding="utf-8").read()
bad = None
for line in t.splitlines():
    if "MikuPlayer.exe" in line and "player" in line and "dev" in line:
        bad = line
        break

if bad:
    fixed = '        string dev = System.IO.Path.Combine(@"D:\\MikuWallpaper\\player", "bin", "MikuPlayer.exe");'
    t = t.replace(bad, fixed)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("fixed path")
else:
    print("line not found")
