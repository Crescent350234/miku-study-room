import io

p = r"D:\MikuWallpaper\bridge\AiSettings.cs"
t = io.open(p, encoding="utf-8").read()

if "using System.Diagnostics;" not in t:
    t = t.replace("using System.Drawing;", "using System.Diagnostics;\nusing System.Drawing;")

if "btnBg" not in t:
    anchor = """        Controls.Add(btnHkDefault);

"""
    add = """        Controls.Add(btnHkDefault);

        Button btnBg = new Button();
        btnBg.Text = "自定义背景…";
        btnBg.Location = new Point(250, 420);
        btnBg.Width = 120;
        btnBg.Click += delegate { using (var f = new BgForm()) f.ShowDialog(this); };
        Controls.Add(btnBg);

"""
    t = t.replace(anchor, add, 1)

bg_class = r'''

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
'''

if "class BgForm" not in t:
    t = t.rstrip() + "\n" + bg_class

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("BgForm added")
