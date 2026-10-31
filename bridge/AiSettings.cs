using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Runtime.InteropServices;

public class AiSettingsForm : Form
{
    private TextBox txtBase;
    private TextBox txtKey;
    private TextBox txtModel;
    private CheckBox chkEnabled;
    private ComboBox cbPreset;
    private Label lblStatus;
    private Button btnSave;
    private Button btnTest;
    private Button btnKey;
    private TextBox txtNext;
    private TextBox txtPrev;
    private TextBox txtPause;
    private readonly string iniPath;
    private readonly string hotkeyPath;

    private static readonly Dictionary<string, string[]> Presets = new Dictionary<string, string[]>
    {
        { "DeepSeek（推荐，便宜）", new string[] { "https://api.deepseek.com/v1", "deepseek-chat" } },
        { "OpenAI", new string[] { "https://api.openai.com/v1", "gpt-4o-mini" } },
        { "自定义（OpenAI 兼容）", null }
    };

    [System.Runtime.InteropServices.DllImport("user32.dll")]
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

    private Label MakeLabel(string text, int x, int y)
    {
        Label l = new Label();
        l.Text = text;
        l.Location = new Point(x, y);
        l.AutoSize = true;
        l.ForeColor = Color.FromArgb(60, 60, 70);
        Controls.Add(l);
        return l;
    }

    private TextBox MakeText(int x, int y, int w)
    {
        TextBox t = new TextBox();
        t.Location = new Point(x, y);
        t.Width = w;
        t.BorderStyle = BorderStyle.FixedSingle;
        return t;
    }

    private void PresetChanged(object sender, EventArgs e)
    {
        string name = cbPreset.SelectedItem as string;
        if (name == null) return;
        string[] p = Presets[name];
        if (p == null) return;

        txtBase.Text = p[0];
        txtModel.Text = p[1];
    }

    private void LoadIni()
    {
        Dictionary<string, string> d = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        try
        {
            if (File.Exists(iniPath))
            {
                foreach (string raw in File.ReadAllLines(iniPath, Encoding.UTF8))
                {
                    string line = raw.Trim();
                    if (line.Length == 0 || line.StartsWith("#") || line.StartsWith(";")) continue;
                    int eq = line.IndexOf('=');
                    if (eq <= 0) continue;
                    d[line.Substring(0, eq).Trim()] = line.Substring(eq + 1).Trim();
                }
            }
        }
        catch { }

        chkEnabled.Checked = d.ContainsKey("enabled") && d["enabled"] == "1";
        txtBase.Text = d.ContainsKey("base") ? d["base"] : "https://api.deepseek.com/v1";
        txtKey.Text = d.ContainsKey("key") ? d["key"] : "";
        txtModel.Text = d.ContainsKey("model") ? d["model"] : "deepseek-chat";

        if (txtBase.Text.IndexOf("api.deepseek.com", StringComparison.OrdinalIgnoreCase) >= 0)
            cbPreset.SelectedIndex = 0;
        else if (txtBase.Text.IndexOf("api.openai.com", StringComparison.OrdinalIgnoreCase) >= 0)
            cbPreset.SelectedIndex = 1;
        else
            cbPreset.SelectedIndex = 2;

        lblStatus.Text = chkEnabled.Checked ? "当前：已启用" : "当前：未启用（免费封面取色）";

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
    }

    private void SaveAndClose()
    {
        try
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("# 由 Miku 壁纸 AI 设置工具生成");
            sb.AppendLine("enabled=" + (chkEnabled.Checked ? "1" : "0"));
            sb.AppendLine("base=" + txtBase.Text.Trim());
            sb.AppendLine("key=" + txtKey.Text.Trim());
            sb.AppendLine("model=" + txtModel.Text.Trim());
            File.WriteAllText(iniPath, sb.ToString(), new UTF8Encoding(false));

            StringBuilder hb = new StringBuilder();
            hb.AppendLine("# 网易云全局快捷键（格式：ctrl+alt+p / media_next）");
            hb.AppendLine("next=" + txtNext.Text.Trim());
            hb.AppendLine("prev=" + txtPrev.Text.Trim());
            hb.AppendLine("playpause=" + txtPause.Text.Trim());
            File.WriteAllText(hotkeyPath, hb.ToString(), new UTF8Encoding(false));

            RestartBridge();

            MessageBox.Show(this, "已保存，并已重启控制桥。\n\n如果快捷键仍不生效，请检查网易云：\n设置 → 快捷键 → 全局快捷键是否开启、组合键是否一致。",
                "保存成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
            Close();
        }
        catch (Exception ex)
        {
            MessageBox.Show(this, "保存失败：" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void RestartBridge()
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

    private void OpenKeyPage()
    {
        try
        {
            string url = txtBase.Text.IndexOf("openai.com", StringComparison.OrdinalIgnoreCase) >= 0
                ? "https://platform.openai.com/api-keys"
                : "https://platform.deepseek.com/api_keys";
            System.Diagnostics.Process.Start(url);
        }
        catch { }
    }

    private void TestConnection()
    {
        string baseUrl = txtBase.Text.Trim().TrimEnd('/');
        string key = txtKey.Text.Trim();
        string model = txtModel.Text.Trim();
        if (baseUrl.Length == 0 || key.Length == 0)
        {
            lblStatus.Text = "请先填接口地址和 Key";
            return;
        }

        btnTest.Enabled = false;
        lblStatus.Text = "测试中…";

        Thread t = new Thread(delegate ()
        {
            string result;
            try
            {
                result = CallApi(baseUrl, key, model);
            }
            catch (Exception ex)
            {
                result = "失败：" + ex.Message;
            }

            try
            {
                BeginInvoke(new Action(delegate ()
                {
                    lblStatus.Text = result;
                    btnTest.Enabled = true;
                }));
            }
            catch { }
        });
        t.IsBackground = true;
        t.Start();
    }

    private string CallApi(string baseUrl, string key, string model)
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;

        string body = "{\"model\":\"" + model.Replace("\"", "") + "\",\"messages\":[{\"role\":\"user\",\"content\":\"只回复两个字：正常\"}],\"max_tokens\":16}";
        HttpWebRequest req = (HttpWebRequest)WebRequest.Create(baseUrl + "/chat/completions");
        req.Method = "POST";
        req.ContentType = "application/json";
        req.Headers["Authorization"] = "Bearer " + key;
        req.Proxy = null;
        req.Timeout = 30000;

        byte[] bytes = Encoding.UTF8.GetBytes(body);
        req.ContentLength = bytes.Length;
        using (Stream s = req.GetRequestStream()) s.Write(bytes, 0, bytes.Length);

        try
        {
            using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
            using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
            {
                string text = sr.ReadToEnd();
                int i = text.IndexOf("\"content\":\"", StringComparison.Ordinal);
                if (i >= 0)
                {
                    i += 11;
                    int j = text.IndexOf('"', i);
                    if (j > i) return "连接正常，模型回复：" + text.Substring(i, Math.Min(j - i, 40));
                }
                return "连接正常（HTTP " + (int)resp.StatusCode + "）";
            }
        }
        catch (WebException wex)
        {
            string detail = "";
            try
            {
                if (wex.Response != null)
                {
                    using (StreamReader er = new StreamReader(wex.Response.GetResponseStream(), Encoding.UTF8))
                        detail = er.ReadToEnd();
                }
            }
            catch { }
            if (detail.Length > 160) detail = detail.Substring(0, 160);
            return "失败：" + wex.Message + (detail.Length > 0 ? " — " + detail : "");
        }
    }

    [STAThread]
    public static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new AiSettingsForm());
    }
}


public class BgForm : Form
{
    private Label lbl;
    private ProgressBar bar;
    private Button btnVideo;
    private Button btnImage;

    public BgForm()
    {
        Text = "自定义背景";
        ClientSize = new Size(520, 250);
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        Font = new Font("Microsoft YaHei UI", 9.5f);
        BackColor = Color.FromArgb(250, 250, 252);

        Label title = new Label();
        title.Text = "把视频或图片换成壁纸背景";
        title.Font = new Font("Microsoft YaHei UI", 12f, FontStyle.Bold);
        title.Location = new Point(22, 18);
        title.AutoSize = true;
        Controls.Add(title);

        Label hint = new Label();
        hint.Text = "视频会转成 VP9 WebM（需要 ffmpeg，首次会提示安装）。\n输出到已安装壁纸工程的 custom 文件夹。";
        hint.ForeColor = Color.FromArgb(110, 110, 120);
        hint.Location = new Point(24, 48);
        hint.AutoSize = true;
        Controls.Add(hint);

        btnVideo = new Button();
        btnVideo.Text = "选择视频并转换";
        btnVideo.Location = new Point(24, 96);
        btnVideo.Width = 220;
        btnVideo.Height = 36;
        btnVideo.Click += delegate { PickVideo(); };
        Controls.Add(btnVideo);

        btnImage = new Button();
        btnImage.Text = "选择图片";
        btnImage.Location = new Point(258, 96);
        btnImage.Width = 220;
        btnImage.Height = 36;
        btnImage.Click += delegate { PickImage(); };
        Controls.Add(btnImage);

        bar = new ProgressBar();
        bar.Location = new Point(24, 146);
        bar.Width = 454;
        bar.Height = 16;
        bar.Style = ProgressBarStyle.Continuous;
        bar.Value = 0;
        Controls.Add(bar);

        lbl = new Label();
        lbl.Text = "选择文件开始。";
        lbl.Location = new Point(24, 170);
        lbl.Width = 460;
        lbl.Height = 40;
        lbl.ForeColor = Color.FromArgb(90, 100, 100);
        Controls.Add(lbl);

        Button close = new Button();
        close.Text = "关闭";
        close.Location = new Point(384, 208);
        close.Width = 94;
        close.Click += delegate { Close(); };
        Controls.Add(close);
    }

    private void SetStatus(string s)
    {
        if (lbl.IsDisposed) return;
        if (lbl.InvokeRequired) { lbl.BeginInvoke(new Action<string>(SetStatus), s); return; }
        lbl.Text = s;
    }

    private void SetBusy(bool busy)
    {
        if (btnVideo.IsDisposed) return;
        if (btnVideo.InvokeRequired) { btnVideo.BeginInvoke(new Action<bool>(SetBusy), busy); return; }
        btnVideo.Enabled = !busy;
        btnImage.Enabled = !busy;
        bar.Style = busy ? ProgressBarStyle.Marquee : ProgressBarStyle.Continuous;
        if (!busy) bar.Value = 0;
    }

    private string CustomDir()
    {
        string we = null;
        try
        {
            string ini = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\installer.ini");
            if (File.Exists(ini))
            {
                foreach (string line in File.ReadAllLines(ini))
                {
                    if (line.StartsWith("we=", StringComparison.OrdinalIgnoreCase)) { we = line.Substring(3).Trim(); break; }
                }
            }
        }
        catch { }

        var candidates = new List<string>();
        if (!string.IsNullOrEmpty(we)) candidates.Add(we);
        candidates.Add(@"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"C:\Program Files\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\SteamLibrary\steamapps\common\wallpaper_engine");
        candidates.Add(@"E:\Steam\steamapps\common\wallpaper_engine");

        foreach (string c in candidates)
        {
            string proj = Path.Combine(c, @"projects\myprojects\Miku Study Room");
            if (Directory.Exists(proj))
            {
                string custom = Path.Combine(proj, "custom");
                Directory.CreateDirectory(custom);
                return custom;
            }
        }
        return null;
    }

    private string FindFfmpeg()
    {
        foreach (string dir in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';'))
        {
            try
            {
                if (dir.Trim().Length == 0) continue;
                string f = Path.Combine(dir.Trim(), "ffmpeg.exe");
                if (File.Exists(f)) return f;
            }
            catch { }
        }
        try
        {
            string winget = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"Microsoft\WinGet\Packages");
            if (Directory.Exists(winget))
            {
                foreach (string d in Directory.GetDirectories(winget, "Gyan.FFmpeg*"))
                {
                    foreach (string f in Directory.GetFiles(d, "ffmpeg.exe", SearchOption.AllDirectories))
                        return f;
                }
            }
        }
        catch { }
        return null;
    }

    private string EnsureFfmpeg()
    {
        string ff = FindFfmpeg();
        if (ff != null) return ff;

        var r = MessageBox.Show(this,
            "没有找到 ffmpeg，转换视频需要它。\n\n是否现在用 winget 自动安装？",
            "需要 ffmpeg", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
        if (r != DialogResult.Yes) return null;

        try
        {
            SetStatus("正在安装 ffmpeg，请稍候…");
            var psi = new ProcessStartInfo("winget",
                "install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements");
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;
            using (var p = Process.Start(psi))
            {
                p.WaitForExit(300000);
            }
            ff = FindFfmpeg();
        }
        catch (Exception ex)
        {
            SetStatus("安装失败：" + ex.Message);
        }

        if (ff == null) MessageBox.Show(this, "ffmpeg 仍未找到。请手动安装后重试。", "失败", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        return ff;
    }

    private void PickVideo()
    {
        using (var dlg = new OpenFileDialog())
        {
            dlg.Title = "选择视频";
            dlg.Filter = "视频文件|*.mp4;*.mkv;*.mov;*.avi;*.flv;*.wmv;*.webm|所有文件|*.*";
            if (dlg.ShowDialog(this) != DialogResult.OK) return;

            string src = dlg.FileName;
            string outDir = CustomDir();
            if (outDir == null)
            {
                MessageBox.Show(this, "找不到已安装的壁纸工程，请先用安装器安装一次。", "未安装", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            SetBusy(true);
            SetStatus("准备转换…");
            Thread t = new Thread(delegate ()
            {
                try
                {
                    string ff = EnsureFfmpeg();
                    if (ff == null) { SetStatus("已取消。"); return; }

                    string outWebm = Path.Combine(outDir, "bg.webm");
                    SetStatus("正在转换视频，越长越慢…");
                    var psi = new ProcessStartInfo(ff,
                        "-y -i \"" + src + "\" -c:v libvpx-vp9 -b:v 3M -an -vf \"scale=1920:-2\" \"" + outWebm + "\"");
                    psi.UseShellExecute = false;
                    psi.CreateNoWindow = true;
                    psi.RedirectStandardOutput = true;
                    psi.RedirectStandardError = true;
                    using (var p = Process.Start(psi))
                    {
                        p.StandardOutput.ReadToEnd();
                        p.StandardError.ReadToEnd();
                        p.WaitForExit();
                    }
                    if (!File.Exists(outWebm))
                    {
                        SetStatus("转换失败，请换一个视频。");
                        return;
                    }

                    // 抽第一帧当封面
                    try
                    {
                        var psi2 = new ProcessStartInfo(ff,
                            "-y -i \"" + src + "\" -frames:v 1 -q:v 2 \"" + Path.Combine(outDir, "bg.jpg") + "\"");
                        psi2.UseShellExecute = false;
                        psi2.CreateNoWindow = true;
                        using (var p2 = Process.Start(psi2)) p2.WaitForExit(30000);
                    }
                    catch { }

                    SetStatus("完成。打开壁纸设置 → 背景 → 选择「自定义」。");
                    MessageBox.Show(this, "背景已转换并写入壁纸工程。\n\n打开壁纸设置 → 背景 → 选择「自定义」。",
                        "完成", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    SetStatus("失败：" + ex.Message);
                }
                finally
                {
                    SetBusy(false);
                }
            });
            t.IsBackground = true;
            t.Start();
        }
    }

    private void PickImage()
    {
        using (var dlg = new OpenFileDialog())
        {
            dlg.Title = "选择图片";
            dlg.Filter = "图片|*.jpg;*.jpeg;*.png;*.bmp;*.webp|所有文件|*.*";
            if (dlg.ShowDialog(this) != DialogResult.OK) return;

            string outDir = CustomDir();
            if (outDir == null)
            {
                MessageBox.Show(this, "找不到已安装的壁纸工程，请先用安装器安装一次。", "未安装", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            try
            {
                string ext = Path.GetExtension(dlg.FileName).ToLowerInvariant();
                string target = Path.Combine(outDir, ext == ".png" ? "bg.png" : "bg.jpg");
                File.Copy(dlg.FileName, target, true);
                SetStatus("图片已写入：" + Path.GetFileName(target));
                MessageBox.Show(this, "图片已写入壁纸工程。\n\n打开壁纸设置 → 背景 → 选择「自定义」。",
                    "完成", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, "写入失败：" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}

internal static class AcrylicHelper
{
    [StructLayout(LayoutKind.Sequential)]
    private struct AccentPolicy
    {
        public int AccentState;
        public int AccentFlags;
        public int GradientColor;
        public int AnimationId;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct WindowCompositionAttributeData
    {
        public int Attribute;
        public IntPtr Data;
        public int SizeOfData;
    }

    [DllImport("user32.dll")]
    private static extern int SetWindowCompositionAttribute(IntPtr hwnd, ref WindowCompositionAttributeData data);

    [DllImport("dwmapi.dll")]
    private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int value, int size);

    public static void Enable(IntPtr hwnd, int r, int g, int b, int alpha)
    {
        try
        {
            int gradient = (alpha << 24) | (b << 16) | (g << 8) | r;
            AccentPolicy policy = new AccentPolicy();
            policy.AccentState = 4; // ACCENT_ENABLE_ACRYLICBLURBEHIND
            policy.AccentFlags = 2;
            policy.GradientColor = gradient;

            int size = Marshal.SizeOf(policy);
            IntPtr ptr = Marshal.AllocHGlobal(size);
            Marshal.StructureToPtr(policy, ptr, false);

            WindowCompositionAttributeData data = new WindowCompositionAttributeData();
            data.Attribute = 19; // WCA_ACCENT_POLICY
            data.Data = ptr;
            data.SizeOfData = size;
            SetWindowCompositionAttribute(hwnd, ref data);
            Marshal.FreeHGlobal(ptr);

            int round = 2; // DWMWCP_ROUND
            DwmSetWindowAttribute(hwnd, 33, ref round, sizeof(int));
        }
        catch { }
    }
}


public class MusicForm : Form
{
    private ListBox lst;
    private Label lbl;
    private Button btnImport;
    private Button btnClear;

    public MusicForm()
    {
        Text = "本地歌单";
        ClientSize = new Size(560, 420);
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        Font = new Font("Microsoft YaHei UI", 9.5f);
        BackColor = Color.FromArgb(24, 38, 35);

        Label title = new Label();
        title.Text = "本地歌单";
        title.Font = new Font("Microsoft YaHei UI", 12f, FontStyle.Bold);
        title.ForeColor = Color.FromArgb(220, 235, 231);
        title.Location = new Point(22, 18);
        title.AutoSize = true;
        Controls.Add(title);

        lbl = new Label();
        lbl.Text = "音乐和歌词会复制到壁纸工程的 music 文件夹。";
        lbl.ForeColor = Color.FromArgb(150, 175, 168);
        lbl.Location = new Point(24, 50);
        lbl.AutoSize = true;
        Controls.Add(lbl);

        lst = new ListBox();
        lst.Location = new Point(24, 82);
        lst.Width = 510;
        lst.Height = 240;
        lst.BackColor = Color.FromArgb(30, 46, 42);
        lst.ForeColor = Color.FromArgb(230, 242, 238);
        lst.BorderStyle = BorderStyle.FixedSingle;
        Controls.Add(lst);

        btnImport = new Button();
        btnImport.Text = "导入音乐（可多选）";
        btnImport.Location = new Point(24, 336);
        btnImport.Width = 200;
        btnImport.Height = 34;
        btnImport.Click += delegate { Import(); };
        Controls.Add(btnImport);

        btnClear = new Button();
        btnClear.Text = "清空歌单";
        btnClear.Location = new Point(238, 336);
        btnClear.Width = 120;
        btnClear.Height = 34;
        btnClear.Click += delegate {
            if (MessageBox.Show(this, "只清空歌单列表，不删除 music 里的文件。继续？", "确认", MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                if (ProjectDir() != null) File.WriteAllText(Path.Combine(ProjectDir(), "music", "playlist.json"), "[]", new UTF8Encoding(false));
                LoadList();
            }
        };
        Controls.Add(btnClear);

        Button close = new Button();
        close.Text = "关闭";
        close.Location = new Point(440, 336);
        close.Width = 94;
        close.Height = 34;
        close.Click += delegate { Close(); };
        Controls.Add(close);

        Style(this);
        LoadList();
    }

    private static void Style(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Button b = c as Button;
            if (b != null)
            {
                b.FlatStyle = FlatStyle.Flat;
                b.FlatAppearance.BorderColor = Color.FromArgb(72, 102, 94);
                b.BackColor = Color.FromArgb(38, 56, 51);
                b.ForeColor = Color.FromArgb(230, 242, 238);
                b.Cursor = Cursors.Hand;
            }
            Style(c);
        }
    }

    private static string ProjectDir()
    {
        string we = null;
        try
        {
            string ini = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\installer.ini");
            if (File.Exists(ini))
            {
                foreach (string line in File.ReadAllLines(ini))
                {
                    if (line.StartsWith("we=", StringComparison.OrdinalIgnoreCase)) { we = line.Substring(3).Trim(); break; }
                }
            }
        }
        catch { }

        var candidates = new List<string>();
        if (!string.IsNullOrEmpty(we)) candidates.Add(we);
        candidates.Add(@"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"C:\Program Files\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\SteamLibrary\steamapps\common\wallpaper_engine");
        candidates.Add(@"E:\Steam\steamapps\common\wallpaper_engine");

        foreach (string c in candidates)
        {
            string proj = Path.Combine(c, @"projects\myprojects\Miku Study Room");
            if (Directory.Exists(proj)) return proj;
        }
        return null;
    }

    private string MusicDir()
    {
        string proj = ProjectDir();
        if (proj == null) return null;
        string dir = Path.Combine(proj, "music");
        Directory.CreateDirectory(dir);
        return dir;
    }

    private void LoadList()
    {
        lst.Items.Clear();
        try
        {
            string proj = ProjectDir();
            if (proj == null) return;
            string file = Path.Combine(proj, "music", "playlist.json");
            if (!File.Exists(file)) return;
            string json = File.ReadAllText(file, Encoding.UTF8).Trim();
            if (json.Length < 3) return;
            int pos = 0;
            while (true)
            {
                int i = json.IndexOf("\"file\":\"", pos, StringComparison.Ordinal);
                if (i < 0) break;
                i += 8;
                int j = json.IndexOf('"', i);
                if (j < 0) break;
                lst.Items.Add(json.Substring(i, j - i));
                pos = j;
            }
        }
        catch { }
    }

    private void Import()
    {
        string music = MusicDir();
        if (music == null)
        {
            MessageBox.Show(this, "找不到已安装的壁纸工程，请先用安装器安装一次。", "未安装", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        using (var dlg = new OpenFileDialog())
        {
            dlg.Title = "选择音乐文件（可多选）";
            dlg.Multiselect = true;
            dlg.Filter = "音频|*.mp3;*.flac;*.wav;*.m4a;*.ogg;*.aac|所有文件|*.*";
            if (dlg.ShowDialog(this) != DialogResult.OK) return;

            // 可选：再选一次同名 lrc
            string[] lyrics = new string[0];
            if (MessageBox.Show(this, "是否同时选择对应的 .lrc 歌词文件？", "歌词", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            {
                using (var dlg2 = new OpenFileDialog())
                {
                    dlg2.Title = "选择歌词文件（可多选，可取消）";
                    dlg2.Multiselect = true;
                    dlg2.Filter = "歌词|*.lrc|所有文件|*.*";
                    if (dlg2.ShowDialog(this) == DialogResult.OK) lyrics = dlg2.FileNames;
                }
            }

            try
            {
                var entries = new List<string>();
                foreach (string src in dlg.FileNames)
                {
                    string name = Path.GetFileNameWithoutExtension(src);
                    string ext = Path.GetExtension(src);
                    string target = Path.Combine(music, name + ext);
                    File.Copy(src, target, true);

                    string lrcName = "";
                    foreach (string l in lyrics)
                    {
                        if (string.Equals(Path.GetFileNameWithoutExtension(l), name, StringComparison.OrdinalIgnoreCase))
                        {
                            File.Copy(l, Path.Combine(music, name + ".lrc"), true);
                            lrcName = name + ".lrc";
                            break;
                        }
                    }

                    entries.Add("{\"name\":" + Q(name) + ",\"artist\":\"本地\",\"file\":" + Q(name + ext) + ",\"lrc\":" + Q(lrcName) + "}");
                }

                string playlist = Path.Combine(music, "playlist.json");
                string existing = "[]";
                if (File.Exists(playlist))
                {
                    existing = File.ReadAllText(playlist, Encoding.UTF8).Trim();
                    if (existing.Length <= 2) existing = "[]";
                }

                string merged;
                if (existing == "[]") merged = "[" + string.Join(",", entries.ToArray()) + "]";
                else merged = existing.TrimEnd(']') + "," + string.Join(",", entries.ToArray()) + "]";

                File.WriteAllText(playlist, merged, new UTF8Encoding(false));
                LoadList();
                MessageBox.Show(this, "已导入 " + entries.Count + " 首。\n\n重载壁纸后，内置播放会使用本地歌单。",
                    "完成", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show(this, "导入失败：" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    private static string Q(string s)
    {
        if (s == null) return "\"\"";
        return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }
}
