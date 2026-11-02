using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Effects;
using System.Windows.Threading;

public class OverlayWindow : Window
{
    [DllImport("user32.dll")]
    private static extern int GetWindowLong(IntPtr h, int index);
    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr h, int index, int value);

    private const int GWL_EXSTYLE = -20;
    private const int WS_EX_TRANSPARENT = 0x20;
    private const int WS_EX_TOOLWINDOW = 0x80;
    private const int WS_EX_NOACTIVATE = 0x08000000;

    private StackPanel currentPanel;
    private TextBlock next;
    private double fade = 0;
    private int shownIndex = -1;
    private double indexChangedAt = 0;

    private class CharAnim
    {
        public TextBlock El;
        public TranslateTransform Tf;
        public double BaseX;
        public double BaseY;
        public double Ax;
        public double Ay;
        public double Speed;
        public double Phase;
    }

    private List<CharAnim> anims = new List<CharAnim>();

    private string baseUrl = "http://127.0.0.1:51789/";
    private string statePath;
    private string songId = "";
    private List<LrcLine> lines = new List<LrcLine>();
    private DateTime songStarted = DateTime.Now;
    private bool visibleWanted = false;
    private string pos = "top";

    private DispatcherTimer dataTimer;
    private DispatcherTimer uiTimer;
    private DispatcherTimer stateTimer;

    private class LrcLine
    {
        public double T;
        public string Text;
    }

    public OverlayWindow()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        WindowStyle = WindowStyle.None;
        AllowsTransparency = true;
        Background = Brushes.Transparent;
        Topmost = true;
        ShowInTaskbar = false;
        ResizeMode = ResizeMode.NoResize;
        ShowActivated = false;
        Focusable = false;
        IsHitTestVisible = false;
        Width = SystemParameters.WorkArea.Width;
        Height = 190;
        Left = 0;
        Top = 40;

        statePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            @"MikuWallpaper\overlay.json");
        baseUrl = ResolveBase();

        var root = new Grid();
        root.IsHitTestVisible = false;

        var stack = new StackPanel();
        stack.HorizontalAlignment = HorizontalAlignment.Center;
        stack.VerticalAlignment = VerticalAlignment.Center;
        stack.IsHitTestVisible = false;

        currentPanel = new StackPanel();
        currentPanel.Orientation = Orientation.Horizontal;
        currentPanel.HorizontalAlignment = HorizontalAlignment.Center;
        currentPanel.IsHitTestVisible = false;
        currentPanel.Opacity = 0;

        next = new TextBlock();
        next.FontFamily = new FontFamily("Microsoft YaHei UI");
        next.FontSize = 21;
        next.FontWeight = FontWeights.Light;
        next.Foreground = new SolidColorBrush(Color.FromArgb(150, 210, 228, 222));
        next.TextAlignment = TextAlignment.Center;
        next.Margin = new Thickness(0, 10, 0, 0);
        next.Opacity = 0.0;

        stack.Children.Add(currentPanel);
        stack.Children.Add(next);
        root.Children.Add(stack);
        Content = root;

        SourceInitialized += delegate
        {
            IntPtr h = new WindowInteropHelper(this).Handle;
            int ex = GetWindowLong(h, GWL_EXSTYLE);
            SetWindowLong(h, GWL_EXSTYLE, ex | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE);
        };

        LoadState();

        dataTimer = new DispatcherTimer();
        dataTimer.Interval = TimeSpan.FromSeconds(1);
        dataTimer.Tick += delegate { RefreshData(); };
        dataTimer.Start();

        uiTimer = new DispatcherTimer();
        uiTimer.Interval = TimeSpan.FromMilliseconds(33);
        uiTimer.Tick += delegate { Animate(); };
        uiTimer.Start();

        stateTimer = new DispatcherTimer();
        stateTimer.Interval = TimeSpan.FromMilliseconds(500);
        stateTimer.Tick += delegate { LoadState(); };
        stateTimer.Start();

        RefreshData();
    }

    private static string ResolveBase()
    {
        try
        {
            string p = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"MikuWallpaper\bridge\port.txt");
            if (File.Exists(p))
            {
                int port;
                if (int.TryParse(File.ReadAllText(p).Trim(), out port)) return "http://127.0.0.1:" + port + "/";
            }
        }
        catch { }
        return "http://127.0.0.1:51789/";
    }

    private void LoadState()
    {
        try
        {
            if (!File.Exists(statePath)) { ApplyVisible(false); return; }
            string json = File.ReadAllText(statePath);
            bool on = json.IndexOf("\"on\":true", StringComparison.Ordinal) >= 0;
            string p = Field(json, "pos");
            if (!string.IsNullOrEmpty(p)) pos = p;
            ApplyVisible(on);
        }
        catch { }
    }

    private void ApplyVisible(bool on)
    {
        visibleWanted = on;
        if (on)
        {
            Show();
            if (pos == "bottom")
            {
                Top = SystemParameters.WorkArea.Bottom - Height - 80;
            }
            else
            {
                Top = SystemParameters.WorkArea.Top + 40;
            }
        }
        else
        {
            Hide();
        }
    }

    private string Get(string path, int timeoutMs)
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create(baseUrl + path);
            req.Timeout = timeoutMs;
            req.ReadWriteTimeout = timeoutMs;
            req.UserAgent = "MikuLyrics/1.0";
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                return sr.ReadToEnd();
        }
        catch { return null; }
    }

    private void RefreshData()
    {
        if (!visibleWanted) return;

        string json = Get("now.json", 1200);
        if (string.IsNullOrEmpty(json)) return;

        string id = Field(json, "id");
        string lrcUrl = Field(json, "lrc");

        if (!string.IsNullOrEmpty(id) && id != songId)
        {
            songId = id;
            songStarted = DateTime.Now;
            lines = new List<LrcLine>();
            shownIndex = -1;
            if (!string.IsNullOrEmpty(lrcUrl)) LoadLrc(lrcUrl);
        }
    }

    private void LoadLrc(string url)
    {
        try
        {
            var req = (HttpWebRequest)WebRequest.Create(url);
            req.Timeout = 4000;
            req.ReadWriteTimeout = 4000;
            req.UserAgent = "MikuLyrics/1.0";
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
            {
                string text = sr.ReadToEnd();
                lines = ParseLrc(text);
            }
        }
        catch { }
    }

    private static readonly Regex TagRe = new Regex(@"\[(\d{1,3}):(\d{1,2})(?:[.:](\d{1,3}))?\]", RegexOptions.Compiled);

    private static List<LrcLine> ParseLrc(string text)
    {
        var list = new List<LrcLine>();
        if (string.IsNullOrEmpty(text)) return list;

        foreach (string raw in text.Replace("\r", "").Split('\n'))
        {
            string line = raw.Trim();
            if (line.Length < 5) continue;

            var matches = TagRe.Matches(line);
            if (matches.Count == 0) continue;

            string content = TagRe.Replace(line, "").Trim();
            if (content.Length == 0) continue;

            foreach (Match m in matches)
            {
                int min = int.Parse(m.Groups[1].Value, CultureInfo.InvariantCulture);
                int sec = int.Parse(m.Groups[2].Value, CultureInfo.InvariantCulture);
                string frac = m.Groups[3].Value;
                double ms = 0;
                if (frac.Length == 1) ms = int.Parse(frac) * 100;
                else if (frac.Length == 2) ms = int.Parse(frac) * 10;
                else if (frac.Length >= 3) ms = int.Parse(frac.Substring(0, 3));
                double t = min * 60 + sec + ms / 1000.0;
                list.Add(new LrcLine { T = t, Text = content });
            }
        }

        list.Sort(delegate (LrcLine a, LrcLine b) { return a.T.CompareTo(b.T); });
        return list;
    }

    private void Animate()
    {
        if (!visibleWanted) return;

        double posSec = (DateTime.Now - songStarted).TotalSeconds;

        int idx = -1;
        for (int i = 0; i < lines.Count; i++)
        {
            if (lines[i].T <= posSec) idx = i;
            else break;
        }

        if (idx != shownIndex)
        {
            shownIndex = idx;
            indexChangedAt = posSec;
            if (idx >= 0 && idx < lines.Count)
            {
                SetScatter(lines[idx].Text);
                next.Text = (idx + 1 < lines.Count) ? lines[idx + 1].Text : "";
            }
            else
            {
                SetScatter("");
                next.Text = "";
            }
            DebugLog(posSec, idx, idx >= 0 && idx < lines.Count ? lines[idx].Text : "");
        }

        double age = posSec - indexChangedAt;
        fade = Math.Min(1.0, age / 0.35);
        currentPanel.Opacity = fade;
        next.Opacity = fade * 0.55;

        double t = DateTime.Now.TimeOfDay.TotalSeconds;
        for (int i = 0; i < anims.Count; i++)
        {
            var a = anims[i];
            double ph = t * a.Speed + a.Phase;
            a.Tf.X = a.BaseX + Math.Sin(ph) * a.Ax;
            a.Tf.Y = a.BaseY + Math.Cos(ph * 1.13) * a.Ay;
        }
    }

    private void SetScatter(string text)
    {
        currentPanel.Children.Clear();
        anims.Clear();
        if (string.IsNullOrEmpty(text)) return;

        var units = new List<string>();
        foreach (string part in Regex.Split(text, @"[，。！？、；：\s]+"))
        {
            if (part.Length > 0) units.Add(part);
        }
        if (units.Count < 3)
        {
            units.Clear();
            foreach (char ch in text)
                if (!char.IsWhiteSpace(ch)) units.Add(ch.ToString());
        }

        int seed = text.GetHashCode();
        double baseSize = units.Count > 16 ? 28 : (units.Count > 11 ? 32 : 38);

        for (int i = 0; i < units.Count; i++)
        {
            double r = Frac(Math.Sin(seed + i * 13) * 10000);
            double r2 = Frac(Math.Sin(seed + i * 23) * 10000);
            double r3 = Frac(Math.Sin(seed + i * 31) * 10000);

            var tb = new TextBlock();
            tb.Text = units[i];
            tb.FontFamily = new FontFamily("Microsoft YaHei UI");
            tb.FontSize = baseSize * (0.9 + r * 0.6);
            tb.FontWeight = FontWeights.Light;
            tb.Foreground = new SolidColorBrush(Color.FromRgb(246, 252, 250));
            tb.Effect = new DropShadowEffect
            {
                Color = Color.FromRgb(143, 240, 226),
                BlurRadius = 18,
                ShadowDepth = 0,
                Opacity = 0.5
            };
            tb.IsHitTestVisible = false;

            double dx = (r2 - 0.5) * 18;
            double dy = (r3 - 0.5) * 46;

            var group = new TransformGroup();
            group.Children.Add(new SkewTransform((r2 - 0.5) * 16, 0));
            group.Children.Add(new RotateTransform((r - 0.5) * 32));
            var tf = new TranslateTransform(dx, dy);
            group.Children.Add(tf);
            tb.RenderTransform = group;
            tb.RenderTransformOrigin = new Point(0.5, 0.5);

            currentPanel.Children.Add(tb);
            anims.Add(new CharAnim
            {
                El = tb,
                Tf = tf,
                BaseX = dx,
                BaseY = dy,
                Ax = 4 + r * 10,
                Ay = 3 + r2 * 9,
                Speed = 2 * Math.PI / (3.2 + r * 4.5),
                Phase = -r2 * 3
            });
        }
    }

    private static double Frac(double v)
    {
        return Math.Abs(v - Math.Truncate(v));
    }

    private static void DebugLog(double posSec, int idx, string text)
    {
        try
        {
            string p = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"MikuWallpaper\lyrics-overlay.log");
            File.WriteAllText(p, DateTime.Now.ToString("HH:mm:ss") + " pos=" + posSec.ToString("F1") +
                " idx=" + idx + " lines=" + text, new UTF8Encoding(false));
        }
        catch { }
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

    [STAThread]
    public static void Main()
    {
        bool created;
        using (var mutex = new System.Threading.Mutex(true, "MikuLyricsOverlay", out created))
        {
            if (!created) return;
            var app = new Application();
            app.ShutdownMode = ShutdownMode.OnMainWindowClose;
            app.Run(new OverlayWindow());
        }
    }
}
