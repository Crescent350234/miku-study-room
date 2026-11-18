using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;
using Microsoft.VisualBasic;
using Microsoft.Win32;

public class TrayApp : ApplicationContext
{
    private NotifyIcon icon;
    private ContextMenuStrip menu;
    private ToolStripMenuItem songItem;
    private ToolStripMenuItem playItem;
    private ToolStripMenuItem focusItem;
    private ToolStripMenuItem overlayItem;
    private ToolStripMenuItem playlistMenu;
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

        playlistMenu = new ToolStripMenuItem("歌单");
        playlistMenu.DropDownOpening += delegate { BuildPlaylistMenu(); };
        menu.Items.Add(playlistMenu);

        menu.Opening += delegate { SyncOverlayChecks(); };

        menu.Items.Add(new ToolStripMenuItem("重启桥接", null, delegate { RestartBridge(); }));
        menu.Items.Add(new ToolStripMenuItem("恢复桌面图标", null, delegate
        {
            try
            {
                string j = Get("focus.json");
                if (j != null && j.IndexOf("\"focus\":true", StringComparison.OrdinalIgnoreCase) >= 0) Get("focus.toggle");
                Get("showicons");
                icon.ShowBalloonTip(1200, "Miku", "已恢复桌面图标", ToolTipIcon.None);
            }
            catch { }
        }));
        menu.Items.Add(new ToolStripMenuItem("打开桌面播放器", null, delegate { OpenPlayer(); }));
        var playerStartup = new ToolStripMenuItem("桌面播放器开机自启");
        playerStartup.Checked = File.Exists(PlayerStartupLnk());
        playerStartup.CheckOnClick = true;
        playerStartup.Click += delegate { TogglePlayerStartup(playerStartup.Checked); };
        menu.Items.Add(playerStartup);
        menu.Items.Add(new ToolStripMenuItem("打开设置", null, delegate { OpenSettings(); }));
        menu.Items.Add(new ToolStripMenuItem("启用精确进度…", null, delegate { EnableExact(); }));
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
        timer.Tick += delegate { try { RefreshNow(); } catch { } };
        timer.Start();

        healthTimer = new System.Threading.Timer(delegate { try { CheckPageHealth(); } catch { } }, null, 10000, 30000);

        StartPlaybackAgent();

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

    private void EnableExact()
    {
        try
        {
            string port = GetCdpPort();
            if (!string.IsNullOrEmpty(port))
            {
                SavePortIni(port);
                icon.ShowBalloonTip(1500, "Miku", "精确进度已连接（端口 " + port + "）", ToolTipIcon.None);
                return;
            }
            var r = MessageBox.Show("精确进度需要重启一次网易云（会中断当前播放几秒）。\n是否继续？", "Miku",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (r != DialogResult.Yes) return;
            int free = PickFreePort();
            RestartNetease(port: free.ToString());
            Thread.Sleep(12000);
            if (ProbeCdp(free.ToString()))
            {
                SavePortIni(free.ToString());
                icon.ShowBalloonTip(1800, "Miku", "精确进度已启用（端口 " + free + "）", ToolTipIcon.None);
            }
            else
            {
                icon.ShowBalloonTip(1800, "Miku", "精确进度启用失败，仍使用估算", ToolTipIcon.Warning);
            }
        }
        catch { }
    }

    private void RestartNetease(string port = "")
    {
        try
        {
            string exe = null;
            foreach (var p in Process.GetProcessesByName("cloudmusic"))
            {
                try { exe = p.MainModule.FileName; } catch { }
                try { p.Kill(); } catch { }
            }
            if (string.IsNullOrEmpty(exe)) exe = @"E:\CloudMusic\cloudmusic.exe";
            Thread.Sleep(1500);
            if (string.IsNullOrEmpty(port)) port = ReadPortIni();
            if (string.IsNullOrEmpty(port)) port = PickFreePort().ToString();
            Process.Start(new ProcessStartInfo(exe, "--remote-debugging-port=" + port + " --orpheus-startup=autorun") { UseShellExecute = false });
            icon.ShowBalloonTip(1500, "Miku", "正在重启网易云（启用精确进度）", ToolTipIcon.None);
        }
        catch { }
    }

    private void RestartBridge()
    {
        Get("restart.all");
        icon.ShowBalloonTip(1500, "Miku", "正在重启 bridge 和 watchdog…", ToolTipIcon.None);
    }

    private static string PlayerExe()
    {
        string local = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\DesktopPlayer\MikuPlayer.exe");
        if (File.Exists(local)) return local;
        string dev = System.IO.Path.Combine(@"D:\MikuWallpaper\player", "bin", "MikuPlayer.exe");
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

    private static string PlayerStartupLnk()
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

    private class PlEntry
    {
        public string Id = "";
        public string Name = "";
        public List<string> Songs = new List<string>();
    }

    private static readonly string[] AudioExts = { ".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".opus" };

    private static string MusicDirPath()
    {
        string d = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\music");
        Directory.CreateDirectory(d);
        return d;
    }

    private static string PlaylistsPath()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\playlists.json");
    }

    private static string PlEsc(string s)
    {
        return (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"");
    }

    private static List<PlEntry> LoadPlaylists(out string active)
    {
        active = "meting";
        var list = new List<PlEntry>();
        try
        {
            if (!File.Exists(PlaylistsPath())) return list;
            foreach (string line in File.ReadLines(PlaylistsPath()))
            {
                var a = Regex.Match(line, "\"active\"\\s*:\\s*\"([^\"]*)\"");
                if (a.Success) active = a.Groups[1].Value;
                string trimmed = line.TrimStart();
                if (!trimmed.StartsWith("{\"id\"")) continue;
                var id = Regex.Match(trimmed, "\"id\":\"([^\"]*)\"");
                var name = Regex.Match(trimmed, "\"name\":\"([^\"]*)\"");
                var songs = Regex.Match(trimmed, "\"songs\":\\[(.*?)\\]");
                var e = new PlEntry();
                if (id.Success) e.Id = id.Groups[1].Value;
                if (name.Success) e.Name = name.Groups[1].Value;
                if (songs.Success)
                    foreach (Match m in Regex.Matches(songs.Groups[1].Value, "\"([^\"]*)\""))
                        e.Songs.Add(m.Groups[1].Value);
                list.Add(e);
            }
        }
        catch { }
        return list;
    }

    private static void SavePlaylists(List<PlEntry> list, string active)
    {
        try
        {
            var sb = new StringBuilder();
            sb.Append("{\"active\":\"").Append(PlEsc(active)).Append("\",\"ts\":").Append(DateTime.Now.Ticks).Append(",\"playlists\":[\n");
            for (int i = 0; i < list.Count; i++)
            {
                var p = list[i];
                sb.Append("{\"id\":\"").Append(PlEsc(p.Id)).Append("\",\"name\":\"").Append(PlEsc(p.Name)).Append("\",\"songs\":[");
                for (int j = 0; j < p.Songs.Count; j++)
                {
                    if (j > 0) sb.Append(",");
                    sb.Append("\"").Append(PlEsc(p.Songs[j])).Append("\"");
                }
                sb.Append("]}");
                if (i < list.Count - 1) sb.Append(",");
                sb.Append("\n");
            }
            sb.Append("]}");
            Directory.CreateDirectory(Path.GetDirectoryName(PlaylistsPath()));
            File.WriteAllText(PlaylistsPath(), sb.ToString(), new UTF8Encoding(false));
        }
        catch { }
    }

    private void BuildPlaylistMenu()
    {
        try
        {
            playlistMenu.DropDownItems.Clear();
            string active;
            var list = LoadPlaylists(out active);

            var builtin = new ToolStripMenuItem("STUDY WITH MIKU（内置）");
            builtin.Checked = active == "meting";
            builtin.Click += delegate
            {
                string cur;
                var all = LoadPlaylists(out cur);
                SavePlaylists(all, "meting");
                icon.ShowBalloonTip(1000, "Miku", "已切换回内置歌单", ToolTipIcon.None);
            };
            playlistMenu.DropDownItems.Add(builtin);

            foreach (var p in list)
            {
                var item = new ToolStripMenuItem(p.Name + "  (" + p.Songs.Count + ")");
                item.Checked = p.Id == active;
                string id = p.Id;
                item.Click += delegate
                {
                    string cur;
                    var all = LoadPlaylists(out cur);
                    SavePlaylists(all, id);
                    icon.ShowBalloonTip(1000, "Miku", "已切换到歌单「" + p.Name + "」", ToolTipIcon.None);
                };
                playlistMenu.DropDownItems.Add(item);
            }
            if (list.Count > 0) playlistMenu.DropDownItems.Add(new ToolStripSeparator());

            playlistMenu.DropDownItems.Add(new ToolStripMenuItem("新建歌单…", null, delegate { NewPlaylist(); }));
            playlistMenu.DropDownItems.Add(new ToolStripMenuItem("导入音乐到当前歌单", null, delegate { ImportToCurrent(); }));
            playlistMenu.DropDownItems.Add(new ToolStripMenuItem("从网易云歌单 ID 导入（临时）…", null, delegate { ImportNeteaseTemp(); }));
            playlistMenu.DropDownItems.Add(new ToolStripMenuItem("打开音乐文件夹", null, delegate { OpenMusicFolder(); }));
            playlistMenu.DropDownItems.Add(new ToolStripMenuItem("删除当前歌单", null, delegate { DeleteCurrentPlaylist(); }));
        }
        catch { }
    }

    private void NewPlaylist()
    {
        try
        {
            string name = Interaction.InputBox("给新歌单起个名字：", "新建歌单", "我的歌单");
            if (string.IsNullOrWhiteSpace(name)) return;
            string active;
            var list = LoadPlaylists(out active);
            var p = new PlEntry();
            p.Id = "pl" + DateTime.Now.Ticks;
            p.Name = name.Trim();
            list.Add(p);
            SavePlaylists(list, p.Id);
            icon.ShowBalloonTip(1000, "Miku", "已新建歌单「" + p.Name + "」", ToolTipIcon.None);
        }
        catch { }
    }

    private void ImportToCurrent()
    {
        try
        {
            string active;
            var list = LoadPlaylists(out active);
            PlEntry p = null;
            foreach (var x in list) if (x.Id == active) p = x;
            if (p == null)
            {
                p = new PlEntry();
                p.Id = "pl" + DateTime.Now.Ticks;
                p.Name = "我的音乐";
                list.Add(p);
                active = p.Id;
            }
            int added = 0;
            foreach (string f in Directory.GetFiles(MusicDirPath()))
            {
                string ext = Path.GetExtension(f).ToLowerInvariant();
                if (Array.IndexOf(AudioExts, ext) < 0) continue;
                string fn = Path.GetFileName(f);
                if (p.Songs.Contains(fn)) continue;
                p.Songs.Add(fn);
                added++;
            }
            SavePlaylists(list, active);
            icon.ShowBalloonTip(1400, "Miku", added > 0 ? ("已导入 " + added + " 首到「" + p.Name + "」") : "没有新文件", ToolTipIcon.None);
        }
        catch { }
    }

    private void ImportNeteaseTemp()
    {
        try
        {
            string id = Interaction.InputBox("网易云歌单 ID（playlist?id= 后面那串数字）：", "临时歌单", "");
            id = (id ?? "").Trim();
            if (!Regex.IsMatch(id, "^[0-9]{3,}$")) return;

            string url = "https://api.injahow.cn/meting/?server=netease&type=playlist&id=" + id;
            var req = (HttpWebRequest)WebRequest.Create(url);
            req.Timeout = 20000;
            req.UserAgent = "MikuTray/1.0";
            string body;
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                body = sr.ReadToEnd();

            var p = new PlEntry();
            p.Id = "pl" + DateTime.Now.Ticks;
            p.Name = "临时歌单 " + id;
            foreach (Match m in Regex.Matches(body, "\\{[^{}]*\\}"))
            {
                string obj = m.Value;
                var nm = Regex.Match(obj, "\"name\":\"((?:[^\"\\\\]|\\\\.)*)\"");
                var uu = Regex.Match(obj, "\"url\":\"((?:[^\"\\\\]|\\\\.)*)\"");
                if (!nm.Success || !uu.Success) continue;
                string name = Regex.Unescape(nm.Groups[1].Value);
                string songUrl = Regex.Unescape(uu.Groups[1].Value).Replace("\\/", "/");
                if (songUrl.Length == 0) continue;
                p.Songs.Add(name + "|||" + songUrl);
            }
            if (p.Songs.Count == 0) { icon.ShowBalloonTip(1500, "Miku", "没有取到歌曲", ToolTipIcon.None); return; }

            string active;
            var list = LoadPlaylists(out active);
            list.Add(p);
            SavePlaylists(list, p.Id);
            icon.ShowBalloonTip(1500, "Miku", "已创建「" + p.Name + "」，共 " + p.Songs.Count + " 首", ToolTipIcon.None);
        }
        catch { icon.ShowBalloonTip(1500, "Miku", "导入失败，检查 ID 或网络", ToolTipIcon.None); }
    }

    private void OpenMusicFolder()
    {
        try { Process.Start("explorer.exe", "\"" + MusicDirPath() + "\""); } catch { }
    }

    private void DeleteCurrentPlaylist()
    {
        try
        {
            string active;
            var list = LoadPlaylists(out active);
            if (active == "meting") { icon.ShowBalloonTip(1000, "Miku", "默认歌单不能删除", ToolTipIcon.None); return; }
            list.RemoveAll(delegate (PlEntry x) { return x.Id == active; });
            SavePlaylists(list, "meting");
            icon.ShowBalloonTip(1000, "Miku", "已删除当前歌单", ToolTipIcon.None);
        }
        catch { }
    }

    private System.Threading.Timer healthTimer;
    private int healthTick = 0;
    private DateTime lastAutoReload = DateTime.MinValue;

    private int healthBusy = 0;
    private DateTime recoveryGrace = DateTime.MinValue;
    private DateTime lastRecovery = DateTime.MinValue;
    private DateTime recoveryCooldown = DateTime.MinValue;

    private double PingAge()
    {
        string j = Get("page.status");
        if (string.IsNullOrEmpty(j)) return -2;
        var m = Regex.Match(j, "\"age\"\\s*:\\s*(-?[0-9.]+)");
        if (!m.Success) return -1;
        double a;
        return double.TryParse(m.Groups[1].Value, System.Globalization.NumberStyles.Float,
            System.Globalization.CultureInfo.InvariantCulture, out a) ? a : -1;
    }

    private int bridgeFails = 0;

    private void StartBridgeIfDead()
    {
        try
        {
            string root = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\bridge");
            string bridge = Path.Combine(root, "bridge.exe");
            string watchdog = Path.Combine(root, "watchdog.exe");
            if (Process.GetProcessesByName("bridge").Length == 0 && File.Exists(bridge))
            {
                Process.Start(new ProcessStartInfo(bridge) { WorkingDirectory = root, UseShellExecute = true });
                LogHealth("bridge restarted");
            }
            if (Process.GetProcessesByName("watchdog").Length == 0 && File.Exists(watchdog))
            {
                Process.Start(new ProcessStartInfo(watchdog) { WorkingDirectory = root, UseShellExecute = true });
                LogHealth("watchdog restarted");
            }
        }
        catch { }
    }

    private static bool GameRunning()
    {
        try
        {
            string[] names = { "Overwatch", "VALORANT", "cs2", "r5apex", "GTA5" };
            foreach (string n in names)
                if (Process.GetProcessesByName(n).Length > 0) return true;
        }
        catch { }
        return false;
    }

    private void CheckRendererMemory()
    {
        try
        {
            if (GameRunning()) return;
            string exe = WallpaperExe();
            if (string.IsNullOrEmpty(exe)) return;
            string dir = Path.GetDirectoryName(exe);
            foreach (var p in Process.GetProcessesByName("webwallpaper64"))
            {
                try
                {
                    long mb = p.WorkingSet64 / (1024 * 1024);
                    if (mb < 750) continue;
                    string path = null;
                    try { path = p.MainModule.FileName; } catch { }
                    if (string.IsNullOrEmpty(path) || !path.StartsWith(dir, StringComparison.OrdinalIgnoreCase)) continue;
                    LogHealth("renderer mem " + mb + "MB -> reload");
                    try { p.Kill(); } catch { }
                    Thread.Sleep(800);
                    RunControl(exe, "-control reloadWallpaper");
                    return;
                }
                catch { }
            }
        }
        catch { }
    }

    private void CheckPageHealth()
    {
        if (Interlocked.CompareExchange(ref healthBusy, 1, 0) != 0) return;
        try
        {
            try { CheckRendererMemory(); } catch { }
            try
            {
                if (OverlayOn() && Process.GetProcessesByName("MikuLyrics").Length == 0)
                {
                    EnsureOverlay();
                    LogHealth("overlay restarted");
                }
            }
            catch { }
            double age = PingAge();
            LogHealthLive("check age=" + (age == -2 ? "bridge-down" : age.ToString("F0")));
            if (GameRunning()) return;
            if (age == -2)
            {
                bridgeFails++;
                if (bridgeFails >= 3) { bridgeFails = 0; StartBridgeIfDead(); }
                return;
            }
            bridgeFails = 0;
            if (age >= 0 && age < 90) return;
            if (DateTime.Now < recoveryGrace) return;
            if (DateTime.Now < recoveryCooldown) return;
            if ((DateTime.Now - lastRecovery).TotalSeconds < 45) return;
            lastRecovery = DateTime.Now;
            recoveryCooldown = DateTime.Now.AddMinutes(5);
            LogHealth("stale age=" + age.ToString("F0") + " -> recover");
            Recover();
        }
        catch (Exception ex) { LogHealth("health error: " + ex.Message); }
        finally { Interlocked.Exchange(ref healthBusy, 0); }
    }

    private void RunControl(string exe, string args)
    {
        try
        {
            var psi = new ProcessStartInfo(exe, args);
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            Process.Start(psi);
        }
        catch (Exception ex) { LogHealth("control failed: " + ex.Message); }
    }

    private static void KillByDir(string name, string dir)
    {
        foreach (var p in Process.GetProcessesByName(name))
        {
            try
            {
                string path = null;
                try { path = p.MainModule.FileName; } catch { }
                if (string.IsNullOrEmpty(path) || path.StartsWith(dir, StringComparison.OrdinalIgnoreCase)) p.Kill();
            }
            catch { }
        }
    }

    private static string ProjectIndex(string weDir)
    {
        try
        {
            string ini = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\installer.ini");
            if (File.Exists(ini))
            {
                foreach (string line in File.ReadLines(ini))
                    if (line.StartsWith("we=", StringComparison.OrdinalIgnoreCase))
                    {
                        string we = line.Substring(3).Trim();
                        string p2 = Path.Combine(we, @"projects\myprojects\Miku Study Room\index.html");
                        if (File.Exists(p2)) return p2;
                    }
            }
        }
        catch { }
        return Path.Combine(weDir, @"projects\myprojects\Miku Study Room\index.html");
    }

    private void Recover()
    {
        try
        {
            string exe = WallpaperExe();
            if (string.IsNullOrEmpty(exe)) { LogHealth("no wallpaper exe"); return; }
            recoveryGrace = DateTime.Now.AddSeconds(150);
            string dir = Path.GetDirectoryName(exe);

            KillByDir("webwallpaper64", dir);
            KillByDir("webwallpaper32", dir);
            RunControl(exe, "-control reloadWallpaper");
            Thread.Sleep(4000);
            RunControl(exe, "-control play");
            Thread.Sleep(6000);
            double a1 = PingAge();
            if (a1 >= 0 && a1 < 30) { LogHealth("soft reload ok"); return; }

            LogHealth("soft reload failed -> full restart");
            KillByDir("wallpaperui", dir);
            KillByDir("wallpaper64", dir);
            KillByDir("wallpaper32", dir);
            Thread.Sleep(2000);

            string ui = Path.Combine(dir, "bin", "wallpaperui.exe");
            if (File.Exists(ui))
            {
                Process.Start(new ProcessStartInfo(ui) { WorkingDirectory = Path.GetDirectoryName(ui), UseShellExecute = true, WindowStyle = ProcessWindowStyle.Minimized });
                Thread.Sleep(8000);
            }
            string main = File.Exists(Path.Combine(dir, "wallpaper64.exe")) ? Path.Combine(dir, "wallpaper64.exe") : exe;
            Process.Start(new ProcessStartInfo(main) { UseShellExecute = true });
            Thread.Sleep(5000);
            RunControl(main, "-control openWallpaper -file \"" + ProjectIndex(dir) + "\"");
            Thread.Sleep(3000);
            RunControl(main, "-control play");
            Thread.Sleep(8000);
            LogHealth("restart result age=" + PingAge().ToString("F0"));
        }
        catch (Exception ex) { LogHealth("recover error: " + ex.Message); }
    }

    private void TryToast(string text)
    {
        // 静默恢复：不在桌面弹气球提示，避免打断使用
    }

    private static void LogHealth(string s)
    {
        LogHealthLive("ACTION " + s);
    }
    private static void LogHealthLive(string s)
    {
        try
        {
            string p = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\tray-health.log");
            var fi = new FileInfo(p);
            if (fi.Exists && fi.Length > 400 * 1024)
            {
                try { File.Delete(p); } catch { }
            }
            File.AppendAllText(p, DateTime.Now.ToString("HH:mm:ss") + " " + s + "\r\n");
        }
        catch { }
    }

    private void StartPlaybackAgent()
    {
        var th = new Thread(PlaybackLoop);
        th.IsBackground = true;
        th.Start();
    }

    private static string PbPath()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\playback.json");
    }

    private static void WritePb(string json)
    {
        try
        {
            string p = PbPath();
            Directory.CreateDirectory(Path.GetDirectoryName(p));
            string tmp = p + ".tmp";
            File.WriteAllText(tmp, json, new UTF8Encoding(false));
            if (File.Exists(p)) File.Delete(p);
            File.Move(tmp, p);
        }
        catch { }
    }

    private static string HttpGetShort(string url)
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create(url);
            req.Timeout = 2500;
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                return sr.ReadToEnd();
        }
        catch { return null; }
    }

    private static string cdpPort = "";
    private static readonly object cdpLock = new object();

    private static string PortIni()
    {
        return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\netease.ini");
    }

    private static string ReadPortIni()
    {
        try
        {
            if (!File.Exists(PortIni())) return "";
            foreach (string line in File.ReadLines(PortIni()))
                if (line.StartsWith("port=", StringComparison.OrdinalIgnoreCase))
                    return line.Substring(5).Trim();
        }
        catch { }
        return "";
    }

    private static void SavePortIni(string port)
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(PortIni()));
            File.WriteAllText(PortIni(), "port=" + port + "\r\n", new UTF8Encoding(false));
        }
        catch { }
    }

    private static bool ProbeCdp(string port)
    {
        if (string.IsNullOrEmpty(port)) return false;
        string j = HttpGetShort("http://127.0.0.1:" + port + "/json/version");
        return !string.IsNullOrEmpty(j) && j.IndexOf("Browser", StringComparison.OrdinalIgnoreCase) >= 0;
    }

    private static System.Collections.Generic.List<int> CloudMusicPorts()
    {
        var ports = new System.Collections.Generic.List<int>();
        try
        {
            var pids = new System.Collections.Generic.HashSet<int>();
            foreach (var pr in Process.GetProcessesByName("cloudmusic")) pids.Add(pr.Id);
            if (pids.Count == 0) return ports;
            var psi = new ProcessStartInfo("netstat.exe", "-ano -p TCP");
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.RedirectStandardOutput = true;
            using (var ps = Process.Start(psi))
            {
                string output = ps.StandardOutput.ReadToEnd();
                ps.WaitForExit(4000);
                foreach (string raw in output.Split('\n'))
                {
                    string line = raw.Trim();
                    if (line.IndexOf("LISTENING", StringComparison.OrdinalIgnoreCase) < 0) continue;
                    string[] parts = Regex.Split(line, "\\s+");
                    if (parts.Length < 5) continue;
                    int pid;
                    if (!int.TryParse(parts[parts.Length - 1], out pid)) continue;
                    if (!pids.Contains(pid)) continue;
                    string local = parts[1];
                    int idx = local.LastIndexOf(':');
                    if (idx < 0) continue;
                    int port;
                    if (int.TryParse(local.Substring(idx + 1), out port)) ports.Add(port);
                }
            }
        }
        catch { }
        return ports;
    }

    private static string GetCdpPort()
    {
        lock (cdpLock)
        {
            if (ProbeCdp(cdpPort)) return cdpPort;
            string ini = ReadPortIni();
            if (ProbeCdp(ini)) { cdpPort = ini; return cdpPort; }
            foreach (int port in CloudMusicPorts())
            {
                if (ProbeCdp(port.ToString())) { cdpPort = port.ToString(); SavePortIni(cdpPort); return cdpPort; }
            }
            cdpPort = "";
            return "";
        }
    }

    private static string PickTarget(string targets)
    {
        if (string.IsNullOrEmpty(targets)) return null;
        string first = null;
        foreach (Match m in Regex.Matches(targets, "\\{[^{}]*\\}"))
        {
            string block = m.Value;
            var w = Regex.Match(block, "\"webSocketDebuggerUrl\"\\s*:\\s*\"([^\"]+)\"");
            if (!w.Success) continue;
            if (first == null) first = w.Groups[1].Value;
            if (block.IndexOf("orpheus", StringComparison.OrdinalIgnoreCase) >= 0) return w.Groups[1].Value;
        }
        return first;
    }

    private static int PickFreePort()
    {
        for (int p = 17800; p <= 17899; p++)
        {
            try
            {
                var l = new System.Net.Sockets.TcpListener(IPAddress.Loopback, p);
                l.Start();
                l.Stop();
                return p;
            }
            catch { }
        }
        return 17877;
    }

    private void PlaybackLoop()
    {
        const string expr = "(()=>{const rs=[...document.querySelectorAll('input[type=range]')];const s=rs.find(x=>parseFloat(x.max)>100)||rs[0];const pos=s?parseFloat(s.value):-1;const max=s?parseFloat(s.max):0;const now=Date.now();const st=window.__mikuPbState||{pos:-1,change:now,playing:false};let playing=st.playing;if(pos>st.pos+0.05){playing=true;st.change=now;}else if(Math.abs(pos-st.pos)<0.01&&now-st.change>2000){playing=false;}const btn=[...document.querySelectorAll('button')].some(b=>/暂停/.test((b.title||'')+(b.getAttribute('aria-label')||'')));if(btn){playing=true;st.change=now;}window.__mikuPbState={pos:pos,change:st.change||now,playing:playing};return JSON.stringify({ok:!!s,pos:pos,max:max,playing:playing,ts:now});})()";
        while (true)
        {
            try
            {
                string port = GetCdpPort();
                if (string.IsNullOrEmpty(port))
                {
                    WritePb("{\"ok\":false,\"ts\":" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() + "}");
                    Thread.Sleep(3000);
                    continue;
                }
                string targets = HttpGetShort("http://127.0.0.1:" + port + "/json");
                string wsUrl = PickTarget(targets);
                if (wsUrl == null)
                {
                    WritePb("{\"ok\":false,\"ts\":" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() + "}");
                    Thread.Sleep(3000);
                    continue;
                }
                using (var ws = new ClientWebSocket())
                {
                    ws.ConnectAsync(new Uri(wsUrl), CancellationToken.None).Wait(4000);
                    while (ws.State == WebSocketState.Open)
                    {
                        string payload = "{\"id\":1,\"method\":\"Runtime.evaluate\",\"params\":{\"expression\":" + JsonQuote(expr) + ",\"returnByValue\":true}}";
                        byte[] send = Encoding.UTF8.GetBytes(payload);
                        ws.SendAsync(new ArraySegment<byte>(send), WebSocketMessageType.Text, true, CancellationToken.None).Wait(4000);
                        string resp = ReceiveAll(ws);
                        string val = ExtractValue(resp);
                        if (val == null) break;
                        WritePb(val);
                        Thread.Sleep(300);
                    }
                }
            }
            catch
            {
                WritePb("{\"ok\":false,\"ts\":" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() + "}");
                Thread.Sleep(4000);
            }
        }
    }

    private static string ReceiveAll(ClientWebSocket ws)
    {
        var sb = new StringBuilder();
        var buf = new byte[64 * 1024];
        while (true)
        {
            var seg = new ArraySegment<byte>(buf);
            var r = ws.ReceiveAsync(seg, CancellationToken.None).Result;
            sb.Append(Encoding.UTF8.GetString(buf, 0, r.Count));
            if (r.EndOfMessage) break;
        }
        return sb.ToString();
    }

    private static string ExtractValue(string resp)
    {
        if (string.IsNullOrEmpty(resp)) return null;
        const string marker = "\"value\":\"";
        int i = resp.IndexOf(marker, StringComparison.Ordinal);
        if (i < 0) return null;
        i += marker.Length;
        var sb = new StringBuilder();
        for (int j = i; j < resp.Length; j++)
        {
            char c = resp[j];
            if (c == '\\' && j + 1 < resp.Length)
            {
                char n = resp[++j];
                switch (n)
                {
                    case 'n': sb.Append('\n'); break;
                    case 'r': sb.Append('\r'); break;
                    case 't': sb.Append('\t'); break;
                    case '"': sb.Append('"'); break;
                    case '\\': sb.Append('\\'); break;
                    default: sb.Append(n); break;
                }
                continue;
            }
            if (c == '"') break;
            sb.Append(c);
        }
        return sb.ToString();
    }

    private static string JsonQuote(string s)
    {
        var sb = new StringBuilder("\"");
        foreach (char c in s)
        {
            switch (c)
            {
                case '"': sb.Append("\\\""); break;
                case '\\': sb.Append("\\\\"); break;
                case '\n': sb.Append("\\n"); break;
                case '\r': sb.Append("\\r"); break;
                case '\t': sb.Append("\\t"); break;
                default: sb.Append(c); break;
            }
        }
        sb.Append('"');
        return sb.ToString();
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
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string[] cands = new string[]
            {
                OverlayExe(),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\MikuLyrics.exe"),
                Path.Combine(baseDir, "MikuLyrics.exe"),
                Path.Combine(baseDir, @"..\lyrics\MikuLyrics.exe")
            };
            foreach (string exe in cands)
            {
                if (string.IsNullOrEmpty(exe) || !File.Exists(exe)) continue;
                Process.Start(new ProcessStartInfo(exe) { WorkingDirectory = Path.GetDirectoryName(exe), UseShellExecute = true });
                return;
            }
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
