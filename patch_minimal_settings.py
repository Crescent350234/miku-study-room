import io

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    public AiSettingsForm()")
end = t.find("    private Label MakeLabel", start)
if start < 0 or end < 0:
    raise SystemExit("constructor anchor miss")

new_ctor = r'''    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool ReleaseCapture();
    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern IntPtr SendMessage(IntPtr hWnd, int msg, IntPtr wParam, IntPtr lParam);

    public AiSettingsForm()
    {
        iniPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ai.ini");
        hotkeyPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "hotkeys.ini");

        Text = "Miku Study Room";
        ClientSize = new Size(620, 728);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.None;
        MaximizeBox = false;
        Font = new Font("Microsoft YaHei UI", 9.5f);
        BackColor = Color.FromArgb(14, 18, 17);
        DoubleBuffered = true;

        Label title = new Label();
        title.Text = "Miku Study Room";
        title.Font = new Font("Microsoft YaHei UI", 17f, FontStyle.Bold);
        title.ForeColor = Color.FromArgb(236, 244, 241);
        title.Location = new Point(30, 24);
        title.AutoSize = true;
        Controls.Add(title);

        Label sub = new Label();
        sub.Text = "AI 主题与网易云快捷键";
        sub.ForeColor = Color.FromArgb(126, 148, 141);
        sub.Location = new Point(32, 62);
        sub.AutoSize = true;
        Controls.Add(sub);

        Button close = new Button();
        close.Text = "×";
        close.Font = new Font("Microsoft YaHei UI", 13f);
        close.ForeColor = Color.FromArgb(180, 198, 192);
        close.BackColor = Color.FromArgb(14, 18, 17);
        close.FlatStyle = FlatStyle.Flat;
        close.FlatAppearance.BorderSize = 0;
        close.Location = new Point(566, 18);
        close.Size = new Size(34, 34);
        close.Cursor = Cursors.Hand;
        close.Click += delegate { Close(); };
        Controls.Add(close);


        Label aiTitle = SectionTitle("AI 主题", 30, 104);
        Controls.Add(aiTitle);

        chkEnabled = new CheckBox();
        chkEnabled.Text = "启用 AI 主题（按歌曲生成配色）";
        chkEnabled.ForeColor = Color.FromArgb(214, 228, 223);
        chkEnabled.Location = new Point(30, 134);
        chkEnabled.AutoSize = true;
        Controls.Add(chkEnabled);

        Controls.Add(RowLabel("服务商", 30, 172));
        cbPreset = new ComboBox();
        cbPreset.DropDownStyle = ComboBoxStyle.DropDownList;
        cbPreset.Location = new Point(150, 168);
        cbPreset.Width = 430;
        foreach (string k in Presets.Keys) cbPreset.Items.Add(k);
        cbPreset.SelectedIndex = 0;
        cbPreset.SelectedIndexChanged += PresetChanged;
        Controls.Add(cbPreset);

        Controls.Add(RowLabel("接口地址", 30, 212));
        txtBase = MakeText(150, 208, 430);
        Controls.Add(txtBase);

        Controls.Add(RowLabel("API Key", 30, 252));
        txtKey = MakeText(150, 248, 430);
        txtKey.UseSystemPasswordChar = true;
        Controls.Add(txtKey);

        Controls.Add(RowLabel("模型", 30, 292));
        txtModel = MakeText(150, 288, 430);
        Controls.Add(txtModel);

        btnTest = new Button();
        btnTest.Text = "测试连接";
        btnTest.Location = new Point(150, 330);
        btnTest.Size = new Size(130, 34);
        btnTest.Click += delegate { TestConnection(); };
        Controls.Add(btnTest);

        btnKey = new Button();
        btnKey.Text = "获取 Key";
        btnKey.Location = new Point(450, 330);
        btnKey.Size = new Size(130, 34);
        btnKey.Click += delegate { OpenKeyPage(); };
        Controls.Add(btnKey);

        lblStatus = new Label();
        lblStatus.Text = "";
        lblStatus.ForeColor = Color.FromArgb(126, 148, 141);
        lblStatus.Location = new Point(30, 376);
        lblStatus.AutoSize = true;
        Controls.Add(lblStatus);

        Controls.Add(SectionTitle("网易云快捷键", 30, 414));

        Controls.Add(RowLabel("下一首", 30, 448));
        txtNext = MakeText(150, 444, 300);
        Controls.Add(txtNext);

        Controls.Add(RowLabel("上一首", 30, 484));
        txtPrev = MakeText(150, 480, 300);
        Controls.Add(txtPrev);

        Controls.Add(RowLabel("播放/暂停", 30, 520));
        txtPause = MakeText(150, 516, 300);
        Controls.Add(txtPause);

        Button btnHkDefault = new Button();
        btnHkDefault.Text = "恢复默认";
        btnHkDefault.Location = new Point(150, 552);
        btnHkDefault.Size = new Size(110, 32);
        btnHkDefault.Click += delegate {
            txtNext.Text = "ctrl+alt+right";
            txtPrev.Text = "ctrl+alt+left";
            txtPause.Text = "ctrl+alt+p";
        };
        Controls.Add(btnHkDefault);

        Label hkHint = new Label();
        hkHint.Text = "格式：ctrl+alt+p / ctrl+shift+right / media_next";
        hkHint.ForeColor = Color.FromArgb(100, 120, 114);
        hkHint.Location = new Point(30, 592);
        hkHint.AutoSize = true;
        Controls.Add(hkHint);

        Button btnBg = new Button();
        btnBg.Text = "自定义背景";
        btnBg.Location = new Point(30, 620);
        btnBg.Size = new Size(140, 34);
        btnBg.Click += delegate { using (var f = new BgForm()) f.ShowDialog(this); };
        Controls.Add(btnBg);

        Button btnMusic = new Button();
        btnMusic.Text = "本地音乐";
        btnMusic.Location = new Point(184, 620);
        btnMusic.Size = new Size(140, 34);
        btnMusic.Click += delegate { using (var f = new MusicForm()) f.ShowDialog(this); };
        Controls.Add(btnMusic);

        btnSave = new Button();
        btnSave.Text = "保存";
        btnSave.Location = new Point(450, 664);
        btnSave.Size = new Size(130, 38);
        btnSave.Click += delegate { SaveAndClose(); };
        Controls.Add(btnSave);

        Button btnCancel = new Button();
        btnCancel.Text = "取消";
        btnCancel.Location = new Point(330, 664);
        btnCancel.Size = new Size(100, 34);
        btnCancel.Click += delegate { Close(); };
        Controls.Add(btnCancel);

        Label foot = new Label();
        foot.Text = "Key 只保存在本机 bridge\\ai.ini";
        foot.ForeColor = Color.FromArgb(88, 106, 100);
        foot.Location = new Point(30, 700);
        foot.AutoSize = true;
        Controls.Add(foot);

        // 窗口拖动
        MouseEventHandler startDrag = delegate (object s, MouseEventArgs me) {
            if (me.Button == MouseButtons.Left)
            {
                ReleaseCapture();
                SendMessage(Handle, 0xA1, (IntPtr)0x2, IntPtr.Zero);
            }
        };
        title.MouseDown += startDrag;
        sub.MouseDown += startDrag;
        this.MouseDown += startDrag;

        StyleMinimal(this);
        btnSave.BackColor = Color.FromArgb(127, 227, 212);
        btnSave.ForeColor = Color.FromArgb(12, 26, 22);
        btnSave.FlatAppearance.BorderSize = 0;

        LoadIni();
    }

    private static Label SectionTitle(string text, int x, int y)
    {
        Label l = new Label();
        l.Text = text;
        l.Font = new Font("Microsoft YaHei UI", 11f, FontStyle.Bold);
        l.ForeColor = Color.FromArgb(206, 224, 218);
        l.Location = new Point(x, y);
        l.AutoSize = true;
        return l;
    }

    private static Label RowLabel(string text, int x, int y)
    {
        Label l = new Label();
        l.Text = text;
        l.ForeColor = Color.FromArgb(128, 150, 143);
        l.Location = new Point(x, y);
        l.AutoSize = true;
        return l;
    }

    private static void StyleMinimal(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Button b = c as Button;
            if (b != null)
            {
                b.FlatStyle = FlatStyle.Flat;
                b.FlatAppearance.BorderSize = 0;
                b.BackColor = Color.FromArgb(26, 32, 30);
                b.ForeColor = Color.FromArgb(220, 234, 229);
                if (b.Height < 32) b.Height = 32;
                b.Cursor = Cursors.Hand;
            }
            TextBox tb = c as TextBox;
            if (tb != null)
            {
                tb.BorderStyle = BorderStyle.None;
                tb.BackColor = Color.FromArgb(24, 30, 28);
                tb.ForeColor = Color.FromArgb(236, 246, 242);
                tb.Font = new Font("Microsoft YaHei UI", 10f);
            }
            ComboBox cb = c as ComboBox;
            if (cb != null)
            {
                cb.FlatStyle = FlatStyle.Flat;
                cb.BackColor = Color.FromArgb(24, 30, 28);
                cb.ForeColor = Color.FromArgb(236, 246, 242);
                cb.Font = new Font("Microsoft YaHei UI", 10f);
            }
            StyleMinimal(c);
        }
    }

'''
t = t[:start] + new_ctor + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("minimal constructor written")
