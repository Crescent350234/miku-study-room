import io

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

# fields
t = t.replace("    private Button btnKey;\n    private readonly string iniPath;",
              "    private Button btnKey;\n    private TextBox txtNext;\n    private TextBox txtPrev;\n    private TextBox txtPause;\n    private readonly string iniPath;\n    private readonly string hotkeyPath;")

# paths
t = t.replace('        iniPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ai.ini");',
              '        iniPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ai.ini");\n        hotkeyPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "hotkeys.ini");')

# window size/title
t = t.replace('Text = "Miku 壁纸 · AI 主题设置";\n        ClientSize = new Size(500, 424);',
              'Text = "Miku 壁纸 · 设置（AI 与快捷键）";\n        ClientSize = new Size(500, 575);')

# move buttons/footer down
t = t.replace('btnSave.Location = new Point(380, 364);', 'btnSave.Location = new Point(380, 500);')
t = t.replace('btnCancel.Location = new Point(276, 364);', 'btnCancel.Location = new Point(276, 500);')
t = t.replace('foot.Location = new Point(26, 330);', 'foot.Location = new Point(26, 545);')

# insert hotkey UI before LoadIni
hot = r'''        Label hkTitle = new Label();
        hkTitle.Text = "网易云快捷键（需与客户端设置一致）";
        hkTitle.Font = new Font("Microsoft YaHei UI", 10f, FontStyle.Bold);
        hkTitle.Location = new Point(24, 326);
        hkTitle.AutoSize = true;
        Controls.Add(hkTitle);

        Label h1 = MakeLabel("下一首", 26, 360);
        txtNext = MakeText(120, 356, 240);
        Controls.Add(txtNext);

        Label h2 = MakeLabel("上一首", 26, 394);
        txtPrev = MakeText(120, 390, 240);
        Controls.Add(txtPrev);

        Label h3 = MakeLabel("播放/暂停", 26, 428);
        txtPause = MakeText(120, 424, 240);
        Controls.Add(txtPause);

        Label hkHint = new Label();
        hkHint.Text = "格式示例：ctrl+alt+p、ctrl+shift+right、media_next";
        hkHint.ForeColor = Color.FromArgb(140, 140, 150);
        hkHint.Location = new Point(26, 460);
        hkHint.AutoSize = true;
        Controls.Add(hkHint);

        Button btnHkDefault = new Button();
        btnHkDefault.Text = "恢复默认";
        btnHkDefault.Location = new Point(380, 420);
        btnHkDefault.Width = 90;
        btnHkDefault.Click += delegate {
            txtNext.Text = "ctrl+alt+right";
            txtPrev.Text = "ctrl+alt+left";
            txtPause.Text = "ctrl+alt+p";
        };
        Controls.Add(btnHkDefault);

'''
t = t.replace("        LoadIni();", hot + "        LoadIni();", 1)

# load hotkeys at end of LoadIni
t = t.replace('        lblStatus.Text = chkEnabled.Checked ? "当前：已启用" : "当前：未启用（免费封面取色）";\n    }',
'''        lblStatus.Text = chkEnabled.Checked ? "当前：已启用" : "当前：未启用（免费封面取色）";

        txtNext.Text = "ctrl+alt+right";
        txtPrev.Text = "ctrl+alt+left";
        txtPause.Text = "ctrl+alt+p";
        try
        {
            if (File.Exists(hotkeyPath))
            {
                foreach (string raw in File.ReadAllLines(hotkeyPath, Encoding.UTF8))
                {
                    string line = raw.Trim();
                    int eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    string k = line.Substring(0, eq).Trim().ToLowerInvariant();
                    string v = line.Substring(eq + 1).Trim();
                    if (v.Length == 0) continue;
                    if (k == "next") txtNext.Text = v;
                    else if (k == "prev") txtPrev.Text = v;
                    else if (k == "playpause") txtPause.Text = v;
                }
            }
        }
        catch { }
    }''')

# save hotkeys + restart bridge
t = t.replace('''            File.WriteAllText(iniPath, sb.ToString(), new UTF8Encoding(false));

            MessageBox.Show(this, "已保存。\\n\\n壁纸会在 15 秒内自动读取新配置；\\n切一首歌就会生成 AI 主题。",
                "保存成功", MessageBoxButtons.OK, MessageBoxIcon.Information);''',
'''            File.WriteAllText(iniPath, sb.ToString(), new UTF8Encoding(false));

            StringBuilder hb = new StringBuilder();
            hb.AppendLine("# 网易云全局快捷键（格式：ctrl+alt+p / media_next）");
            hb.AppendLine("next=" + txtNext.Text.Trim());
            hb.AppendLine("prev=" + txtPrev.Text.Trim());
            hb.AppendLine("playpause=" + txtPause.Text.Trim());
            File.WriteAllText(hotkeyPath, hb.ToString(), new UTF8Encoding(false));

            RestartBridge();

            MessageBox.Show(this, "已保存，并已重启控制桥。\\n\\n如果快捷键仍不生效，请检查网易云：\\n设置 → 快捷键 → 全局快捷键是否开启、组合键是否一致。",
                "保存成功", MessageBoxButtons.OK, MessageBoxIcon.Information);''')

# add RestartBridge method before OpenKeyPage
t = t.replace("    private void OpenKeyPage()",
'''    private void RestartBridge()
    {
        try
        {
            foreach (var p in System.Diagnostics.Process.GetProcessesByName("bridge"))
            {
                try { p.Kill(); } catch { }
            }
            Thread.Sleep(600);
            var psi = new System.Diagnostics.ProcessStartInfo(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "bridge.exe"));
            psi.WorkingDirectory = AppDomain.CurrentDomain.BaseDirectory;
            psi.UseShellExecute = true;
            psi.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            System.Diagnostics.Process.Start(psi);
        }
        catch { }
    }

    private void OpenKeyPage()''')

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("AiSettings patched")
