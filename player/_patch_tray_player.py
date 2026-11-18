import io

p = r"D:\MikuWallpaper\tray\TrayCenter.cs"
t = io.open(p, encoding="utf-8").read()

method = '''    private static string PlayerExe()
    {
        string local = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\DesktopPlayer\MikuPlayer.exe");
        if (File.Exists(local)) return local;
        string dev = @"D:\MikuWallpaper\player\bin\MikuPlayer.exe";
        if (File.Exists(dev)) return dev;
        return "";
    }

    private void OpenPlayer()
    {
        try
        {
            string exe = PlayerExe();
            if (string.IsNullOrEmpty(exe)) { MessageBox.Show("未找到 MikuPlayer.exe", "Miku"); return; }
            if (Process.GetProcessesByName("MikuPlayer").Length > 0)
            {
                icon.ShowBalloonTip(1200, "Miku", "桌面播放器已在运行", ToolTipIcon.None);
                return;
            }
            Process.Start(new ProcessStartInfo(exe) { WorkingDirectory = Path.GetDirectoryName(exe), UseShellExecute = true });
        }
        catch (Exception ex) { MessageBox.Show("启动桌面播放器失败：" + ex.Message, "Miku"); }
    }

'''

if "private void OpenPlayer()" not in t:
    t = t.replace("    private void OpenSettings()", method + "    private void OpenSettings()", 1)

anchor = '        menu.Items.Add(new ToolStripMenuItem("打开设置", null, delegate { OpenSettings(); }));'
item = '        menu.Items.Add(new ToolStripMenuItem("打开桌面播放器", null, delegate { OpenPlayer(); }));\n'
if "打开桌面播放器" not in t:
    t = t.replace(anchor, item + anchor, 1)
    print("menu added")
else:
    print("exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)
