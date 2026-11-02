using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

public class TrayApp : ApplicationContext
{
    private NotifyIcon icon;
    private ContextMenuStrip menu;
    private ToolStripMenuItem songItem;
    private ToolStripMenuItem playItem;
    private ToolStripMenuItem focusItem;
    private ToolStripMenuItem overlayItem;
    private ToolStripMenuItem[] alphaItems = new ToolStripMenuItem[5];
    private ToolStripMenuItem[] sizeItems = new ToolStripMenuItem[4];
    private static readonly double[] AlphaVals = { 1.0, 0.85, 0.7, 0.55, 0.4 };
    private static readonly string[] AlphaLabels = { "100%", "85%", "70%", "55%", "40%" };
    private static readonly double[] SizeVals = { 0.8, 1.0, 1.25, 1.5 };
    private static readonly string[] SizeLabels = { "小", "标准", "大", "特大" };
    private System.Windows.Forms.Timer timer;
    private string baseUrl = "http://127.0.0.1:51789/";
    private bool focusOn = false;

    public TrayApp()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        baseUrl = ResolveBase();

        menu = new ContextMenuStrip();
        menu.Font = new Font("Microsoft YaHei UI", 9.5f);

        songItem = new ToolStripMenuItem("读取中…");
        songItem.Enabled = false;
        menu.Items.Add(songItem);
        menu.Items.Add(new ToolStripSeparator());

        playItem = new ToolStripMenuItem("播放 / 暂停", null, delegate { Get("playpause"); });
        menu.Items.Add(playItem);
        menu.Items.Add(new ToolStripMenuItem("上一首", null, delegate { Get("prev"); }));
        menu.Items.Add(new ToolStripMenuItem("下一首", null, delegate { Get("next"); }));
        menu.Items.Add(new ToolStripSeparator());

        focusItem = new ToolStripMenuItem("纯净模式");
        focusItem.CheckOnClick = false;
        focusItem.Click += delegate { ToggleFocus(); };
        menu.Items.Add(focusItem);

        overlayItem = new ToolStripMenuItem("桌面歌词");
        overlayItem.CheckOnClick = true;
        overlayItem.Checked = OverlayOn();
        overlayItem.Click += delegate { SetOverlay(overlayItem.Checked); };
        menu.Items.Add(overlayItem);

        var posMenu = new ToolStripMenuItem("歌词位置");
        var posTop = new ToolStripMenuItem("顶部");
        var posBottom = new ToolStripMenuItem("底部");
        posTop.Click += delegate { SetOverlayPos("top"); };
        posBottom.Click += delegate { SetOverlayPos("bottom"); };
        posMenu.DropDownItems.Add(posTop);
        posMenu.DropDownItems.Add(posBottom);
        menu.Items.Add(posMenu);

        var alphaMenu = new ToolStripMenuItem("歌词透明度");
        for (int i = 0; i < AlphaVals.Length; i++)
        {
            double v = AlphaVals[i];
            var it = new ToolStripMenuItem(AlphaLabels[i]);
            it.Click += delegate { SetOverlayAlpha(v); };
            alphaMenu.DropDownItems.Add(it);
            alphaItems[i] = it;
        }
        menu.Items.Add(alphaMenu);

        var sizeMenu = new ToolStripMenuItem("歌词字号");
        for (int i = 0; i < SizeVals.Length; i++)
        {
            double v = SizeVals[i];
            var it = new ToolStripMenuItem(SizeLabels[i]);
            it.Click += delegate { SetOverlayScale(v); };
            sizeMenu.DropDownItems.Add(it);
            sizeItems[i] = it;
        }
        menu.Items.Add(sizeMenu);
        menu.Opening += delegate { SyncOverlayChecks(); };

        menu.Items.Add(new ToolStripMenuItem("重启桥接", null, delegate { RestartBridge(); }));
        menu.Items.Add(new ToolStripMenuItem("打开设置", null, delegate { OpenSettings(); }));
        menu.Items.Add(new ToolStripMenuItem("打开壁纸目录", null, delegate { OpenWallpaperDir(); }));
        menu.Items.Add(new ToolStripMenuItem("重载壁纸", null, delegate { ReloadWallpaper(); }));

        var autoItem = new ToolStripMenuItem("开机自启");
        autoItem.CheckOnClick = true;
        autoItem.Checked = IsAutostart();
        autoItem.Click += delegate { SetAutostart(autoItem.Checked); };
        menu.Items.Add(autoItem);

        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(new ToolStripMenuItem("退出", null, delegate { ExitThread(); }));

        icon = new NotifyIcon();
        icon.Icon = BuildIcon();
        icon.Text = "Miku 控制中心";
        icon.ContextMenuStrip = menu;
        icon.Visible = true;
        icon.ShowBalloonTip(3000, "Miku 控制中心", "左键或右键 M 图标：桌面歌词 / 纯净模式 / 切歌", ToolTipIcon.Info);
        icon.DoubleClick += delegate { Get("playpause"); };
        icon.MouseClick += delegate (object s, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left) menu.Show(Cursor.Position);
        };

        try
        {
            var sb = new StringBuilder();
            foreach (ToolStripItem it in menu.Items) sb.AppendLine(it.Text);
            File.WriteAllText(Path.Combine(Path.GetDirectoryName(Application.ExecutablePath), "tray-menu.log"),
                DateTime.Now.ToString("HH:mm:ss") + "\r\n" + sb.ToString(), new UTF8Encoding(false));
        }
        catch { }

        timer = new System.Windows.Forms.Timer();
        timer.Interval = 3000;
        timer.Tick += delegate { RefreshNow(); };
        timer.Start();

        if (OverlayOn()) EnsureOverlay();
        RefreshNow();
    }

    private static string ResolveBase()
    {
        try
        {
            string p = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"MikuWallpaper\bridge\port.txt");
            if (File.Exists(p))
            {
                string s = File.ReadAllText(p).Trim();
                int port;
                if (int.TryParse(s, out port)) return "http://127.0.0.1:" + port + "/";
            }
        }
        catch { }
        return "http://127.0.0.1:51789/";
    }

    private string Get(string path)
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create(baseUrl + path);
            req.Timeout = 900;
            req.Method = "GET";
            req.UserAgent = "MikuTray/1.0";
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                return sr.ReadToEnd();
        }
        catch
        {
            return null;
        }
    }

    private void RefreshNow()
    {
        ThreadPool.QueueUserWorkItem(delegate
        {
            string now = Get("now.json");
            string f = Get("focus.json");
            try
            {
                menu.BeginInvoke(new Action(delegate
                {
                    if (string.IsNullOrEmpty(now))
                    {
                        songItem.Text = "bridge 未连接";
                        icon.Text = "Miku 控制中心 · 未连接";
                    }
                    else
                    {
                        string title = Field(now, "title");
                        string artist = Field(now, "artist");
                        string line = string.IsNullOrEmpty(title) ? "未在播放" : (title + (string.IsNullOrEmpty(artist) ? "" : " - " + artist));
                        songItem.Text = line;
                        string tip = "Miku 控制中心 · " + line;
                        icon.Text = tip.Length > 63 ? tip.Substring(0, 60) + "…" : tip;
                    }
                    if (f != null)
                    {
                        focusOn = f.IndexOf("\"focus\":true", StringComparison.Ordinal) >= 0;
                        focusItem.Checked = focusOn;
                    }
                }));
            }
            catch { }
        });
    }

    private static string Field(string json, string key)
    {
        string pat = "\"" + key + "\":\"";
        int i = json.IndexOf(pat, StringComparison.Ordinal);
        if (i < 0) return "";
        i += pat.Length;
        var sb = new StringBuilder();
        for (int j = i; j < json.Length; j++)
        {
            char c = json[j];
            if (c == '\\' && j + 1 < json.Length) { sb.Append(json[++j]); continue; }
            if (c == '"') break;
            sb.Append(c);
        }
        return sb.ToString();
    }

    private void ToggleFocus()
    {
        string r = Get("focus.toggle");
        if (r != null && r.IndexOf("\"focus\":true", StringComparison.Ordinal) >= 0) focusOn = true;
        else if (r != null) focusOn = false;
        else { focusOn = !focusOn; }
        focusItem.Checked = focusOn;
        icon.ShowBalloonTip(1200, "Miku", focusOn ? "纯净模式：已隐藏桌面图标和任务栏" : "纯净模式：已恢复", ToolTipIcon.None);
    }

    private void RestartBridge()
    {
        Get("restart.all");
        icon.ShowBalloonTip(1500, "Miku", "正在重启 bridge 和 watchdog…", ToolTipIcon.None);
    }

    private void OpenSettings()
    {
        try
        {
            string exe = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"MikuWallpaper\bridge\AiSettings.exe");
            if (File.Exists(exe)) Process.Start(exe);
            else MessageBox.Show("找不到 AiSettings.exe，请先运行安装器。", "Miku", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
        catch (Exception ex)
        {
            MessageBox.Show("打开设置失败：" + ex.Message, "Miku", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }
    }

    private static string ProjectDir()
    {
        try
        {
            string we = null;
            string ini = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\installer.ini");
            if (File.Exists(ini))
            {
                foreach (string line in File.ReadAllLines(ini))
                    if (line.StartsWith("we=", StringComparison.OrdinalIgnoreCase)) { we = line.Substring(3).Trim(); break; }
            }
            if (!string.IsNullOrEmpty(we))
            {
                string p = Path.Combine(we, @"projects\myprojects\Miku Study Room");
                if (Directory.Exists(p)) return p;
            }
        }
        catch { }

        string[] cand =
        {
            @"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
            @"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room"
        };
        foreach (string c in cand) if (Directory.Exists(c)) return c;
        return null;
    }

    private static string WallpaperExe()
    {
        string proj = ProjectDir();
        if (!string.IsNullOrEmpty(proj))
        {
            string root = Path.GetFullPath(Path.Combine(proj, @"..\..\.."));
            foreach (string name in new string[] { "wallpaper64.exe", "wallpaper32.exe" })
            {
                string exe = Path.Combine(root, name);
                if (File.Exists(exe)) return exe;
            }
        }
        foreach (string c in new string[] {
            @"D:\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe",
            @"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\wallpaper64.exe" })
            if (File.Exists(c)) return c;
        return null;
    }

    private static string OverlayStatePath()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            @"MikuWallpaper\overlay.json");
    }

    private static string OverlayExe()
    {
        return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "MikuLyrics.exe");
    }

    private static bool OverlayOn()
    {
        try
        {
            if (!File.Exists(OverlayStatePath())) return false;
            return File.ReadAllText(OverlayStatePath()).IndexOf("\"on\":true", StringComparison.Ordinal) >= 0;
        }
        catch { return false; }
    }

    private static string OverlayPos()
    {
        try
        {
            if (!File.Exists(OverlayStatePath())) return "top";
            string s = File.ReadAllText(OverlayStatePath());
            return s.IndexOf("\"pos\":\"bottom\"", StringComparison.Ordinal) >= 0 ? "bottom" : "top";
        }
        catch { return "top"; }
    }

    private static double OverlayNum(string key, double def)
    {
        try
        {
            if (!File.Exists(OverlayStatePath())) return def;
            string s = File.ReadAllText(OverlayStatePath());
            string pat = "\"" + key + "\":";
            int i = s.IndexOf(pat, StringComparison.Ordinal);
            if (i < 0) return def;
            i += pat.Length;
            int st = i;
            while (i < s.Length && (char.IsDigit(s[i]) || s[i] == '.' || s[i] == '-')) i++;
            double v;
            return double.TryParse(s.Substring(st, i - st), System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out v) ? v : def;
        }
        catch { return def; }
    }

    private static void WriteOverlayState(bool on, string pos, double alpha, double scale)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(OverlayStatePath()));
            File.WriteAllText(OverlayStatePath(),
                "{\"on\":" + (on ? "true" : "false") + ",\"pos\":\"" + pos +
                "\",\"alpha\":" + alpha.ToString(System.Globalization.CultureInfo.InvariantCulture) +
                ",\"scale\":" + scale.ToString(System.Globalization.CultureInfo.InvariantCulture) + "}", new UTF8Encoding(false));
        }
        catch { }
    }

    private static void WriteOverlayState(bool on, string pos)
    {
        WriteOverlayState(on, pos, OverlayNum("alpha", 1.0), OverlayNum("scale", 1.0));
    }

    private void SetOverlayAlpha(double alpha)
    {
        WriteOverlayState(OverlayOn(), OverlayPos(), alpha, OverlayNum("scale", 1.0));
    }

    private void SetOverlayScale(double scale)
    {
        WriteOverlayState(OverlayOn(), OverlayPos(), OverlayNum("alpha", 1.0), scale);
    }

    private void SyncOverlayChecks()
    {
        double a = OverlayNum("alpha", 1.0);
        double s = OverlayNum("scale", 1.0);
        for (int i = 0; i < alphaItems.Length; i++)
            if (alphaItems[i] != null) alphaItems[i].Checked = Math.Abs(AlphaVals[i] - a) < 0.01;
        for (int i = 0; i < sizeItems.Length; i++)
            if (sizeItems[i] != null) sizeItems[i].Checked = Math.Abs(SizeVals[i] - s) < 0.01;
    }

    private static void EnsureOverlay()
    {
        try
        {
            if (Process.GetProcessesByName("MikuLyrics").Length > 0) return;
            string exe = OverlayExe();
            if (!File.Exists(exe)) return;
            Process.Start(new ProcessStartInfo(exe) { WorkingDirectory = Path.GetDirectoryName(exe), UseShellExecute = true });
        }
        catch { }
    }

    private void SetOverlay(bool on)
    {
        WriteOverlayState(on, OverlayPos());
        if (on) EnsureOverlay();
        icon.ShowBalloonTip(1000, "Miku", on ? "桌面歌词已开启" : "桌面歌词已关闭", ToolTipIcon.None);
    }

    private void SetOverlayPos(string pos)
    {
        WriteOverlayState(OverlayOn(), pos);
    }

    private static void OpenWallpaperDir()
    {
        string dir = ProjectDir();
        if (string.IsNullOrEmpty(dir))
        {
            MessageBox.Show("找不到壁纸工程目录，请先运行安装器。", "Miku", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }
        try { Process.Start("explorer.exe", "\"" + dir + "\""); } catch { }
    }

    private void ReloadWallpaper()
    {
        string exe = WallpaperExe();
        if (string.IsNullOrEmpty(exe))
        {
            MessageBox.Show("找不到 Wallpaper Engine，请确认已安装。", "Miku", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }
        try
        {
            var psi = new ProcessStartInfo(exe, "-control reloadWallpaper");
            psi.CreateNoWindow = true;
            psi.UseShellExecute = false;
            Process.Start(psi);
            icon.ShowBalloonTip(1200, "Miku", "正在重载壁纸…", ToolTipIcon.None);
        }
        catch { }
    }

    private const string RunKeyPath = @"Software\Microsoft\Windows\CurrentVersion\Run";
    private const string RunValueName = "MikuTrayCenter";

    private static bool IsAutostart()
    {
        try
        {
            using (var k = Registry.CurrentUser.OpenSubKey(RunKeyPath))
            {
                object v = k == null ? null : k.GetValue(RunValueName);
                return v != null && !string.IsNullOrEmpty(v.ToString());
            }
        }
        catch { return false; }
    }

    private static void SetAutostart(bool on)
    {
        try
        {
            using (var k = Registry.CurrentUser.CreateSubKey(RunKeyPath))
            {
                if (k == null) return;
                if (on) k.SetValue(RunValueName, "\"" + Application.ExecutablePath + "\"");
                else k.DeleteValue(RunValueName, false);
            }
        }
        catch { }
    }

    private static Icon BuildIcon()
    {
        var bmp = new Bitmap(32, 32);
        using (var g = Graphics.FromImage(bmp))
        {
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.Clear(Color.Transparent);
            using (var b = new SolidBrush(Color.FromArgb(20, 34, 31)))
                g.FillEllipse(b, 1, 1, 30, 30);
            using (var p = new Pen(Color.FromArgb(143, 240, 226), 2))
                g.DrawEllipse(p, 4, 4, 24, 24);
            using (var f = new Font("Segoe UI", 14f, FontStyle.Bold))
            using (var tb = new SolidBrush(Color.FromArgb(143, 240, 226)))
            {
                var s = g.MeasureString("M", f);
                g.DrawString("M", f, tb, (32 - s.Width) / 2, (32 - s.Height) / 2);
            }
        }
        IntPtr h = bmp.GetHicon();
        return Icon.FromHandle(h);
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            if (icon != null) icon.Visible = false;
            if (timer != null) timer.Dispose();
            if (menu != null) menu.Dispose();
        }
        base.Dispose(disposing);
    }

    [STAThread]
    public static void Main()
    {
        bool created;
        using (var mutex = new Mutex(true, "MikuTrayCenter", out created))
        {
            if (!created) return;
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new TrayApp());
        }
    }
}
