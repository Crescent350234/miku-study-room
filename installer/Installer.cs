using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

class InstallerForm : Form
{
    static string baseDir = AppDomain.CurrentDomain.BaseDirectory;
    static string dataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MikuWallpaper");
    static string bridgeDir = Path.Combine(dataDir, "bridge");
    static string iniPath = Path.Combine(dataDir, "installer.ini");

    TextBox txtWe;
    Button btnBrowse;
    Button btnInstall;
    Button btnOpen;
    Button btnApi;
    CheckBox chkAuto;
    TextBox txtLog;
    Label lblStatus;

    public InstallerForm()
    {
        Text = "Miku Study Room 安装器";
        Width = 720;
        Height = 520;
        StartPosition = FormStartPosition.CenterScreen;
        Font = new Font("Microsoft YaHei UI", 9F);
        BackColor = Color.FromArgb(246, 248, 248);

        var title = new Label();
        title.Text = "Miku Study Room";
        title.Font = new Font("Microsoft YaHei UI", 18F, FontStyle.Bold);
        title.AutoSize = true;
        title.Location = new Point(24, 18);
        Controls.Add(title);

        var sub = new Label();
        sub.Text = "安装、打开壁纸，以及连接你自己的 AI 服务。";
        sub.AutoSize = true;
        sub.ForeColor = Color.FromArgb(90, 100, 100);
        sub.Location = new Point(26, 56);
        Controls.Add(sub);

        var step1 = new Label();
        step1.Text = "1  确认 Wallpaper Engine 位置";
        step1.AutoSize = true;
        step1.Location = new Point(26, 96);
        Controls.Add(step1);

        txtWe = new TextBox();
        txtWe.Location = new Point(26, 122);
        txtWe.Width = 500;
        Controls.Add(txtWe);

        btnBrowse = new Button();
        btnBrowse.Text = "选择目录";
        btnBrowse.Location = new Point(536, 120);
        btnBrowse.Width = 150;
        btnBrowse.Height = 28;
        btnBrowse.Click += delegate { BrowseWe(); };
        Controls.Add(btnBrowse);

        chkAuto = new CheckBox();
        chkAuto.Text = "音乐连接程序开机启动（可选）";
        chkAuto.Location = new Point(26, 164);
        chkAuto.AutoSize = true;
        Controls.Add(chkAuto);

        btnInstall = new Button();
        btnInstall.Text = "安装 / 更新";
        btnInstall.Location = new Point(26, 200);
        btnInstall.Width = 200;
        btnInstall.Height = 38;
        btnInstall.Click += delegate { DoInstall(); };
        Controls.Add(btnInstall);

        btnOpen = new Button();
        btnOpen.Text = "打开壁纸";
        btnOpen.Location = new Point(240, 200);
        btnOpen.Width = 200;
        btnOpen.Height = 38;
        btnOpen.Click += delegate { ApplyWallpaper(); };
        Controls.Add(btnOpen);

        btnApi = new Button();
        btnApi.Text = "设置我的 API";
        btnApi.Location = new Point(454, 200);
        btnApi.Width = 232;
        btnApi.Height = 38;
        btnApi.Click += delegate { OpenApiSettings(); };
        Controls.Add(btnApi);

        lblStatus = new Label();
        lblStatus.Text = "准备就绪。完整解压安装包后，点击安装 / 更新。";
        lblStatus.AutoSize = false;
        lblStatus.Width = 660;
        lblStatus.Height = 22;
        lblStatus.Location = new Point(26, 252);
        lblStatus.ForeColor = Color.FromArgb(70, 90, 90);
        Controls.Add(lblStatus);

        txtLog = new TextBox();
        txtLog.Multiline = true;
        txtLog.ScrollBars = ScrollBars.Vertical;
        txtLog.ReadOnly = true;
        txtLog.Location = new Point(26, 282);
        txtLog.Width = 660;
        txtLog.Height = 180;
        txtLog.BackColor = Color.White;
        Controls.Add(txtLog);

        LoadSettings();
        if (!DetectWe()) { }
    }

    void LoadSettings()
    {
        try
        {
            if (File.Exists(iniPath))
            {
                foreach (var line in File.ReadAllLines(iniPath))
                {
                    var i = line.IndexOf('=');
                    if (i < 0) continue;
                    var k = line.Substring(0, i).Trim();
                    var v = line.Substring(i + 1).Trim();
                    if (k == "we") txtWe.Text = v;
                    if (k == "autostart") chkAuto.Checked = v == "1";
                }
            }
        }
        catch { }
        if (string.IsNullOrEmpty(txtWe.Text)) DetectWe();
    }

    void SaveSettings()
    {
        try
        {
            Directory.CreateDirectory(dataDir);
            File.WriteAllText(iniPath, "we=" + txtWe.Text.Trim() + "\r\nautostart=" + (chkAuto.Checked ? "1" : "0") + "\r\n", Encoding.UTF8);
        }
        catch { }
    }

    bool ValidWe(string p)
    {
        return !string.IsNullOrEmpty(p) && File.Exists(Path.Combine(p, "wallpaper32.exe"));
    }

    bool DetectWe()
    {
        var candidates = new System.Collections.Generic.List<string>();
        foreach (var key in new string[] { @"Software\Valve\Steam", @"SOFTWARE\WOW6432Node\Valve\Steam", @"SOFTWARE\Valve\Steam" })
        {
            using (var k = Registry.LocalMachine.OpenSubKey(key) ?? Registry.CurrentUser.OpenSubKey(key))
            {
                if (k == null) continue;
                var sp = k.GetValue("SteamPath") as string ?? k.GetValue("InstallPath") as string;
                if (!string.IsNullOrEmpty(sp)) candidates.Add(Path.Combine(sp, @"steamapps\common\wallpaper_engine"));
            }
        }
        candidates.Add(@"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"C:\Program Files\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"D:\SteamLibrary\steamapps\common\wallpaper_engine");
        candidates.Add(@"E:\Steam\steamapps\common\wallpaper_engine");
        candidates.Add(@"E:\SteamLibrary\steamapps\common\wallpaper_engine");
        foreach (var c in candidates)
        {
            if (ValidWe(c)) { txtWe.Text = c; return true; }
        }
        return false;
    }

    void BrowseWe()
    {
        using (var dlg = new FolderBrowserDialog())
        {
            dlg.Description = "选择 wallpaper_engine 文件夹（里面有 wallpaper32.exe）";
            if (dlg.ShowDialog() == DialogResult.OK)
            {
                if (ValidWe(dlg.SelectedPath)) txtWe.Text = dlg.SelectedPath;
                else MessageBox.Show("这个目录里没有 wallpaper32.exe，请重新选择。", "路径无效", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }
    }

    static string logFile = Path.Combine(dataDir, "installer.log");

    void Log(string s)
    {
        try { File.AppendAllText(logFile, DateTime.Now.ToString("HH:mm:ss") + "  " + s + "\r\n"); } catch { }
        try
        {
            if (txtLog != null && !txtLog.IsDisposed) txtLog.AppendText(s + "\r\n");
            if (lblStatus != null && !lblStatus.IsDisposed) lblStatus.Text = s;
            Application.DoEvents();
        }
        catch { }
    }

    static void Kill(string name)
    {
        foreach (var p in Process.GetProcessesByName(name))
        {
            try { p.Kill(); } catch { }
        }
    }

    static void CopyDir(string src, string dst)
    {
        Directory.CreateDirectory(dst);
        foreach (var f in Directory.GetFiles(src))
            File.Copy(f, Path.Combine(dst, Path.GetFileName(f)), true);
        foreach (var d in Directory.GetDirectories(src))
            CopyDir(d, Path.Combine(dst, Path.GetFileName(d)));
    }

    string InstalledWallpaperPath()
    {
        return Path.Combine(txtWe.Text.Trim(), @"projects\myprojects\Miku Study Room\index.html");
    }

    void DoInstall()
    {
        try
        {
            var we = txtWe.Text.Trim();
            if (!ValidWe(we))
            {
                MessageBox.Show("Wallpaper Engine 路径无效，请选择包含 wallpaper32.exe 的文件夹。", "路径无效", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (!File.Exists(Path.Combine(baseDir, @"wallpaper\index.html")))
            {
                MessageBox.Show("安装包不完整：找不到 wallpaper\\index.html。", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            SaveSettings();
            Log("正在安装...");

            // 权限探测
            try
            {
                var probe = Path.Combine(we, @"projects\myprojects\.miku-test");
                Directory.CreateDirectory(Path.GetDirectoryName(probe));
                File.WriteAllText(probe, "x");
                File.Delete(probe);
            }
            catch
            {
                var psi = new ProcessStartInfo(Application.ExecutablePath, "--elevated");
                psi.Verb = "runas";
                Process.Start(psi);
                Log("已申请管理员权限，请在弹窗中继续。");
                return;
            }

            Log("复制壁纸工程...");
            var dst = Path.Combine(we, @"projects\myprojects\Miku Study Room");
            CopyDir(Path.Combine(baseDir, "wallpaper"), dst);

            Log("安装控制桥...");
            Directory.CreateDirectory(bridgeDir);
            Kill("bridge");
            Kill("watchdog");
            System.Threading.Thread.Sleep(500);

            foreach (var f in Directory.GetFiles(Path.Combine(baseDir, "bridge")))
            {
                if (Path.GetFileName(f).Equals("ai.ini", StringComparison.OrdinalIgnoreCase)) continue;
                File.Copy(f, Path.Combine(bridgeDir, Path.GetFileName(f)), true);
            }
            var dstAi = Path.Combine(bridgeDir, "ai.ini");
            if (!File.Exists(dstAi))
                File.Copy(Path.Combine(baseDir, @"bridge\ai.ini"), dstAi, true);

            Log("启动控制桥...");
            var bridgeExe = Path.Combine(bridgeDir, "bridge.exe");
            StartHidden(bridgeExe, bridgeDir);
            var watchdogExe = Path.Combine(bridgeDir, "watchdog.exe");
            if (File.Exists(watchdogExe)) StartHidden(watchdogExe, bridgeDir);

            bool ok = false;
            foreach (var port in new int[] { 51789, 52789, 53789, 54789 })
            {
                for (var i = 0; i < 15; i++)
                {
                    try
                    {
                        var req = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:" + port + "/now.json");
                        req.Timeout = 1500;
                        using (var resp = (HttpWebResponse)req.GetResponse()) { ok = resp.StatusCode == HttpStatusCode.OK; }
                        if (ok) break;
                    }
                    catch { System.Threading.Thread.Sleep(300); }
                }
                if (ok) { Log("控制桥已启动（端口 " + port + "）"); break; }
            }
            if (!ok) Log("控制桥未响应，网易云跟随可能不可用。");

            Log("应用壁纸...");
            Process.Start(Path.Combine(we, "wallpaper32.exe"), "-control openWallpaper -file \"" + Path.Combine(dst, "index.html") + "\"");

            if (chkAuto.Checked) CreateStartupShortcut("MikuWallpaperBridge.lnk", bridgeExe, bridgeDir, false);
            else RemoveStartupShortcut("MikuWallpaperBridge.lnk");
            if (File.Exists(watchdogExe))
            {
                if (chkAuto.Checked) CreateStartupShortcut("MikuWallpaperWatchdog.lnk", watchdogExe, bridgeDir, true);
                else RemoveStartupShortcut("MikuWallpaperWatchdog.lnk");
            }

            Log("安装完成。");
            MessageBox.Show("安装完成。如果桌面没变化，请在 Wallpaper Engine 的“已安装”里选择 Miku Study Room。", "完成", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            Log("失败：" + ex.Message);
            MessageBox.Show("安装失败：\r\n" + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    static void StartHidden(string exe, string work)
    {
        try
        {
            var psi = new ProcessStartInfo(exe);
            psi.WorkingDirectory = work;
            psi.UseShellExecute = true;
            psi.WindowStyle = ProcessWindowStyle.Hidden;
            Process.Start(psi);
        }
        catch { }
    }

    static void CreateStartupShortcut(string name, string target, string work, bool minimized)
    {
        try
        {
            var startup = Environment.GetFolderPath(Environment.SpecialFolder.Startup);
            var link = Path.Combine(startup, name);
            var shellType = Type.GetTypeFromProgID("WScript.Shell");
            var shell = Activator.CreateInstance(shellType);
            var shortcut = shellType.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] { link });
            shortcut.GetType().InvokeMember("TargetPath", BindingFlags.SetProperty, null, shortcut, new object[] { target });
            shortcut.GetType().InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, shortcut, new object[] { work });
            if (minimized) shortcut.GetType().InvokeMember("WindowStyle", BindingFlags.SetProperty, null, shortcut, new object[] { 7 });
            shortcut.GetType().InvokeMember("Save", BindingFlags.InvokeMethod, null, shortcut, null);
        }
        catch { }
    }

    static void RemoveStartupShortcut(string name)
    {
        try
        {
            var startup = Environment.GetFolderPath(Environment.SpecialFolder.Startup);
            var link = Path.Combine(startup, name);
            if (File.Exists(link)) File.Delete(link);
        }
        catch { }
    }

    void ApplyWallpaper()
    {
        try
        {
            var we = txtWe.Text.Trim();
            if (!ValidWe(we)) { MessageBox.Show("请先选择正确的 Wallpaper Engine 路径。"); return; }
            var wp = InstalledWallpaperPath();
            if (!File.Exists(wp))
            {
                MessageBox.Show("还没有安装壁纸，请先点击“安装 / 更新”。");
                return;
            }
            Process.Start(Path.Combine(we, "wallpaper32.exe"), "-control openWallpaper -file \"" + wp + "\"");
            Log("已打开壁纸。");
        }
        catch (Exception ex) { MessageBox.Show("打开壁纸失败：" + ex.Message); }
    }

    void OpenApiSettings()
    {
        try
        {
            var ai = Path.Combine(bridgeDir, "AiSettings.exe");
            if (!File.Exists(ai))
            {
                MessageBox.Show("请先完整安装一次，再设置 API。");
                return;
            }
            Process.Start(new ProcessStartInfo(ai) { WorkingDirectory = bridgeDir, UseShellExecute = true });
        }
        catch (Exception ex) { MessageBox.Show("打开设置失败：" + ex.Message); }
    }

    [STAThread]
    static void Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        var form = new InstallerForm();
        if (args.Length > 0 && args[0] == "--elevated") form.Text += "（管理员）";
        if (args.Length > 0 && args[0] == "--install")
        {
            form.Shown += delegate { form.DoInstall(); };
        }
        Application.Run(form);
    }
}
