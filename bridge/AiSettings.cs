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

    public AiSettingsForm()
    {
        iniPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ai.ini");
        hotkeyPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "hotkeys.ini");

        Text = "Miku 壁纸 · 设置（AI 与快捷键）";
        ClientSize = new Size(520, 640);
        StartPosition = FormStartPosition.CenterScreen;
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        Font = new Font("Microsoft YaHei UI", 9.5f);
        BackColor = Color.FromArgb(250, 250, 252);

        Label title = new Label();
        title.Text = "AI 主题（可选）";
        title.Font = new Font("Microsoft YaHei UI", 14f, FontStyle.Bold);
        title.Location = new Point(24, 18);
        title.AutoSize = true;
        Controls.Add(title);

        Label sub = new Label();
        sub.Text = "不开启也能正常用：默认从专辑封面取色，完全免费。";
        sub.ForeColor = Color.FromArgb(110, 110, 120);
        sub.Location = new Point(26, 52);
        sub.AutoSize = true;
        Controls.Add(sub);

        chkEnabled = new CheckBox();
        chkEnabled.Text = "启用 AI 主题（按歌曲生成配色）";
        chkEnabled.Location = new Point(26, 84);
        chkEnabled.AutoSize = true;
        Controls.Add(chkEnabled);

        Label l1 = MakeLabel("服务商", 26, 118);
        cbPreset = new ComboBox();
        cbPreset.DropDownStyle = ComboBoxStyle.DropDownList;
        cbPreset.Location = new Point(120, 114);
        cbPreset.Width = 340;
        foreach (string k in Presets.Keys) cbPreset.Items.Add(k);
        cbPreset.SelectedIndex = 0;
        cbPreset.SelectedIndexChanged += PresetChanged;
        Controls.Add(cbPreset);

        Label l2 = MakeLabel("接口地址", 26, 156);
        txtBase = MakeText(120, 152, 340);
        Controls.Add(txtBase);

        Label l3 = MakeLabel("API Key", 26, 194);
        txtKey = MakeText(120, 190, 340);
        txtKey.UseSystemPasswordChar = true;
        Controls.Add(txtKey);

        Label l4 = MakeLabel("模型", 26, 232);
        txtModel = MakeText(120, 228, 340);
        Controls.Add(txtModel);

        btnKey = new Button();
        btnKey.Text = "获取 Key";
        btnKey.Location = new Point(380, 264);
        btnKey.Width = 80;
        btnKey.Click += delegate { OpenKeyPage(); };
        Controls.Add(btnKey);

        btnTest = new Button();
        btnTest.Text = "测试连接";
        btnTest.Location = new Point(120, 264);
        btnTest.Width = 110;
        btnTest.Click += delegate { TestConnection(); };
        Controls.Add(btnTest);

        lblStatus = new Label();
        lblStatus.Text = "";
        lblStatus.ForeColor = Color.FromArgb(110, 110, 120);
        lblStatus.Location = new Point(26, 300);
        lblStatus.AutoSize = true;
        Controls.Add(lblStatus);

        btnSave = new Button();
        btnSave.Text = "保存";
        btnSave.Location = new Point(400, 560);
        btnSave.Width = 94;
        btnSave.Height = 32;
        btnSave.Click += delegate { SaveAndClose(); };
        Controls.Add(btnSave);

        Button btnCancel = new Button();
        btnCancel.Text = "取消";
        btnCancel.Location = new Point(296, 560);
        btnCancel.Width = 94;
        btnCancel.Height = 32;
        btnCancel.Click += delegate { Close(); };
        Controls.Add(btnCancel);

        Label foot = new Label();
        foot.Text = "Key 只保存在本机 bridge\\ai.ini，不会上传到别处。";
        foot.ForeColor = Color.FromArgb(140, 140, 150);
        foot.Location = new Point(26, 610);
        foot.AutoSize = true;
        Controls.Add(foot);

        Label hkTitle = new Label();
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
        hkHint.Location = new Point(26, 500);
        hkHint.AutoSize = false;
        hkHint.Width = 460;
        Controls.Add(hkHint);

        Button btnHkDefault = new Button();
        btnHkDefault.Text = "恢复默认";
        btnHkDefault.Location = new Point(120, 462);
        btnHkDefault.Width = 110;
        btnHkDefault.Click += delegate {
            txtNext.Text = "ctrl+alt+right";
            txtPrev.Text = "ctrl+alt+left";
            txtPause.Text = "ctrl+alt+p";
        };
        Controls.Add(btnHkDefault);

        Button btnBg = new Button();
        btnBg.Text = "自定义背景…";
        btnBg.Location = new Point(245, 462);
        btnBg.Width = 140;
        btnBg.Click += delegate { using (var f = new BgForm()) f.ShowDialog(this); };
        Controls.Add(btnBg);

        StyleUi(this);
        StyleDark(this);
        btnSave.BackColor = Color.FromArgb(58, 167, 154);
        btnSave.ForeColor = Color.White;
        btnSave.FlatAppearance.BorderSize = 0;
        LoadIni();
    }


    private static void StyleDark(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Label l = c as Label;
            if (l != null) l.ForeColor = Color.FromArgb(220, 235, 231);
            CheckBox cb = c as CheckBox;
            if (cb != null) cb.ForeColor = Color.FromArgb(220, 235, 231);
            TextBox tb = c as TextBox;
            if (tb != null)
            {
                tb.BackColor = Color.FromArgb(30, 46, 42);
                tb.ForeColor = Color.FromArgb(236, 246, 243);
            }
            ComboBox cmb = c as ComboBox;
            if (cmb != null)
            {
                cmb.BackColor = Color.FromArgb(30, 46, 42);
                cmb.ForeColor = Color.FromArgb(236, 246, 243);
            }
            Button b = c as Button;
            if (b != null)
            {
                b.BackColor = Color.FromArgb(38, 56, 51);
                b.ForeColor = Color.FromArgb(230, 242, 238);
                b.FlatAppearance.BorderColor = Color.FromArgb(72, 102, 94);
            }
            StyleDark(c);
        }
    }

    private static void StyleUi(Control root)
    {
        foreach (Control c in root.Controls)
        {
            Button b = c as Button;
            if (b != null)
            {
                b.FlatStyle = FlatStyle.Flat;
                b.FlatAppearance.BorderColor = Color.FromArgb(214, 222, 222);
                b.FlatAppearance.BorderSize = 1;
                b.BackColor = Color.FromArgb(244, 247, 247);
                b.ForeColor = Color.FromArgb(52, 64, 64);
                if (b.Height < 30) b.Height = 30;
                b.Cursor = Cursors.Hand;
            }
            TextBox tb = c as TextBox;
            if (tb != null)
            {
                tb.BorderStyle = BorderStyle.FixedSingle;
                tb.Font = new Font("Microsoft YaHei UI", 10f);
                tb.BackColor = Color.White;
            }
            ComboBox cb = c as ComboBox;
            if (cb != null) cb.Font = new Font("Microsoft YaHei UI", 10f);
            StyleUi(c);
        }
    }

    protected override void OnHandleCreated(EventArgs e)
    {
        base.OnHandleCreated(e);
        AcrylicHelper.Enable(this.Handle, 18, 30, 28, 205);
        this.Opacity = 0.98;
        this.BackColor = Color.FromArgb(24, 38, 35);
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
