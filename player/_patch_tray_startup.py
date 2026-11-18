import io

p = r"D:\MikuWallpaper\tray\TrayCenter.cs"
t = io.open(p, encoding="utf-8").read()

method = '''    private static string PlayerStartupLnk()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Startup), "MikuDesktopPlayer.lnk");
    }

    private void TogglePlayerStartup(bool on)
    {
        try
        {
            string lnk = PlayerStartupLnk();
            if (!on)
            {
                if (File.Exists(lnk)) File.Delete(lnk);
                return;
            }
            string exe = PlayerExe();
            if (string.IsNullOrEmpty(exe)) return;
            Type shellType = Type.GetTypeFromProgID("WScript.Shell");
            dynamic shell = Activator.CreateInstance(shellType);
            dynamic link = shell.CreateShortcut(lnk);
            link.TargetPath = exe;
            link.WorkingDirectory = Path.GetDirectoryName(exe);
            link.Description = "Miku 桌面播放器";
            link.Save();
        }
        catch (Exception ex) { MessageBox.Show("设置开机自启失败：" + ex.Message, "Miku"); }
    }

'''

if "TogglePlayerStartup" not in t:
    t = t.replace("    private void OpenSettings()", method + "    private void OpenSettings()", 1)

anchor = '        menu.Items.Add(new ToolStripMenuItem("打开桌面播放器", null, delegate { OpenPlayer(); }));\n'
item = '''        var playerStartup = new ToolStripMenuItem("桌面播放器开机自启");
        playerStartup.Checked = File.Exists(PlayerStartupLnk());
        playerStartup.CheckOnClick = true;
        playerStartup.Click += delegate { TogglePlayerStartup(playerStartup.Checked); };
        menu.Items.Add(playerStartup);
'''
if "桌面播放器开机自启" not in t:
    t = t.replace(anchor, anchor + item, 1)
    print("startup item added")
else:
    print("exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)
