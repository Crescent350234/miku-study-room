using System;
using System.Collections.Generic;
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
    private List<CharAnim> anims = new List<CharAnim>();
    private string fontId = "sans";
    private string currentText = "";
    private string pushText = "";
    private DateTime pushAt = DateTime.MinValue;
    private DateTime pushTextAt = DateTime.MinValue;
    private bool visibleWanted = false;
    private string pos = "top";

    private string baseUrl = "http://127.0.0.1:51789/";
    private string statePath;

    private DispatcherTimer pushTimer;
    private DispatcherTimer stateTimer;
    private DispatcherTimer uiTimer;

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

    private class FontPick
    {
        public FontFamily Family;
        public FontWeight Weight;
        public FontPick(FontFamily f, FontWeight w) { Family = f; Weight = w; }
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

        stack.Children.Add(currentPanel);
        root.Children.Add(stack);
        Content = root;

        SourceInitialized += delegate
        {
            IntPtr h = new WindowInteropHelper(this).Handle;
            int ex = GetWindowLong(h, GWL_EXSTYLE);
            SetWindowLong(h, GWL_EXSTYLE, ex | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE);
        };

        LoadState();

        pushTimer = new DispatcherTimer();
        pushTimer.Interval = TimeSpan.FromMilliseconds(150);
        pushTimer.Tick += delegate { FetchPush(); };
        pushTimer.Start();

        stateTimer = new DispatcherTimer();
        stateTimer.Interval = TimeSpan.FromMilliseconds(500);
        stateTimer.Tick += delegate { LoadState(); LoadUiFont(); };
        stateTimer.Start();

        uiTimer = new DispatcherTimer();
        uiTimer.Interval = TimeSpan.FromMilliseconds(33);
        uiTimer.Tick += delegate { Animate(); };
        uiTimer.Start();
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
            string p = StrField(json, "pos");
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
            Top = pos == "bottom" ? SystemParameters.WorkArea.Bottom - Height - 80 : SystemParameters.WorkArea.Top + 40;
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
            req.UserAgent = "MikuLyrics/2.0";
            using (var resp = (HttpWebResponse)req.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
                return sr.ReadToEnd();
        }
        catch { return null; }
    }

    private void FetchPush()
    {
        if (!visibleWanted) return;
        string j = Get("lyrics.json", 600);
        if (string.IsNullOrEmpty(j)) return;

        long ageMs = NumField(j, "age");
        if (ageMs < 0 || ageMs > 2000) return;

        string txt = StrField(j, "text");
        pushAt = DateTime.Now;
        if (txt != pushText)
        {
            pushText = txt;
            pushTextAt = DateTime.Now;
            SetScatter(txt);
            Log(@"MikuWallpaper\lyrics-overlay-push.log", txt);
        }
    }

    private void LoadUiFont()
    {
        string j = Get("ui.json", 800);
        if (string.IsNullOrEmpty(j)) return;
        string f = StrField(j, "font");
        if (!string.IsNullOrEmpty(f) && f != fontId)
        {
            fontId = f;
            if (!string.IsNullOrEmpty(currentText)) SetScatter(currentText);
            Log(@"MikuWallpaper\lyrics-overlay-font.log", "font=" + f);
        }
    }

    private void Animate()
    {
        if (!visibleWanted) return;

        double age = (DateTime.Now - pushAt).TotalSeconds;
        if (age > 2.5)
        {
            currentPanel.Opacity = 0;
            return;
        }

        currentPanel.Opacity = Math.Min(1.0, (DateTime.Now - pushTextAt).TotalSeconds / 0.35);

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
        currentText = text;
        if (string.IsNullOrEmpty(text)) return;

        var units = new List<string>();
        foreach (string part in Regex.Split(text, @"[，。！？、；：\s]+"))
            if (part.Length > 0) units.Add(part);

        if (units.Count < 3)
        {
            units.Clear();
            foreach (char ch in text)
                if (!char.IsWhiteSpace(ch)) units.Add(ch.ToString());
        }

        int seed = text.GetHashCode();
        double baseSize = units.Count > 16 ? 28 : (units.Count > 11 ? 32 : 38);
        var fp = FontFor(fontId);

        for (int i = 0; i < units.Count; i++)
        {
            double r = Frac(Math.Sin(seed + i * 13) * 10000);
            double r2 = Frac(Math.Sin(seed + i * 23) * 10000);
            double r3 = Frac(Math.Sin(seed + i * 31) * 10000);

            var tb = new TextBlock();
            tb.Text = units[i];
            tb.FontFamily = fp.Family;
            tb.FontWeight = fp.Weight;
            tb.FontSize = baseSize * (0.9 + r * 0.6);
            tb.Margin = new Thickness(0, 0, baseSize * 0.28, 0);
            tb.Foreground = new SolidColorBrush(PickColor(r, r2, r3));
            tb.Effect = new DropShadowEffect
            {
                Color = Color.FromRgb(10, 22, 20),
                BlurRadius = 1.6,
                ShadowDepth = 0,
                Opacity = 0.62
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

    private static readonly Color[] MintPalette = new Color[]
    {
        Color.FromRgb(47, 107, 98),
        Color.FromRgb(63, 143, 132),
        Color.FromRgb(95, 179, 166),
        Color.FromRgb(143, 240, 226),
        Color.FromRgb(214, 242, 236)
    };

    private static Color PickColor(double r, double r2, double r3)
    {
        double v = r * 0.45 + r2 * 0.35 + r3 * 0.2;
        if (v < 0.30) return MintPalette[0];
        if (v < 0.58) return MintPalette[1];
        if (v < 0.80) return MintPalette[2];
        if (v < 0.93) return MintPalette[3];
        return MintPalette[4];
    }

    private static FontFamily EnSerifFamily()
    {
        try
        {
            string[] cands = new string[]
            {
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, @"fonts\Playfair.ttf"),
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Playfair.ttf"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\fonts\Playfair.ttf")
            };
            foreach (string f in cands)
            {
                if (!File.Exists(f)) continue;
                string dir = Path.GetDirectoryName(f).Replace('\\', '/');
                return new FontFamily(new Uri("file:///" + dir + "/"), "./Playfair.ttf#Playfair Display");
            }
        }
        catch { }
        return new FontFamily("Georgia");
    }

    private static FontPick FontFor(string id)
    {
        switch (id)
        {
            case "kai": return new FontPick(new FontFamily("KaiTi"), FontWeights.Normal);
            case "serif": return new FontPick(new FontFamily("SimSun"), FontWeights.Normal);
            case "fangsong": return new FontPick(new FontFamily("FangSong"), FontWeights.Normal);
            case "dengxian": return new FontPick(new FontFamily("DengXian"), FontWeights.Normal);
            case "youyuan": return new FontPick(new FontFamily("YouYuan"), FontWeights.Normal);
            case "mono": return new FontPick(new FontFamily("Consolas"), FontWeights.Normal);
            case "lishu": return new FontPick(new FontFamily("LiSu"), FontWeights.Normal);
            case "light": return new FontPick(new FontFamily("DengXian Light"), FontWeights.Light);
            case "hei": return new FontPick(new FontFamily("Microsoft YaHei UI"), FontWeights.Bold);
            case "en-serif": return new FontPick(EnSerifFamily(), FontWeights.Normal);
            default: return new FontPick(new FontFamily("Microsoft YaHei UI"), FontWeights.Light);
        }
    }

    private static double Frac(double v)
    {
        return Math.Abs(v - Math.Truncate(v));
    }

    private static string StrField(string json, string key)
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

    private static long NumField(string json, string key)
    {
        string pat = "\"" + key + "\":";
        int i = json.IndexOf(pat, StringComparison.Ordinal);
        if (i < 0) return -1;
        i += pat.Length;
        int start = i;
        while (i < json.Length && (char.IsDigit(json[i]) || json[i] == '-')) i++;
        long v;
        return long.TryParse(json.Substring(start, i - start), out v) ? v : -1;
    }

    private static void Log(string relativePath, string text)
    {
        try
        {
            string p = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), relativePath);
            File.WriteAllText(p, DateTime.Now.ToString("HH:mm:ss") + " " + text, new UTF8Encoding(false));
        }
        catch { }
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
