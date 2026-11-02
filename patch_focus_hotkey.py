import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) 让 FocusMode 能调用 WallpaperControl
t = t.replace("private static bool WallpaperControl(string command)", "internal static bool WallpaperControl(string command)")

# 2) 在 Main 启动热键
if "FocusMode.Start();" not in t:
    t = t.replace("        LoadHotkeys();\n", "        LoadHotkeys();\n        FocusMode.Start();\n", 1)

# 3) 加 /focus.toggle 路由
if "/focus.toggle" not in t:
    anchor = 'else if (path.StartsWith("/hideicons")) WallpaperControl("hideIcons");'
    add = 'else if (path.StartsWith("/focus.toggle")) { FocusMode.Toggle(); Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes("{\\"focus\\":" + (FocusMode.IsOn ? "true" : "false") + "}")); }\n                        ' + anchor
    t = t.replace(anchor, add, 1)

# 4) 追加 FocusMode 类
focus = r'''

internal static class FocusMode
{
    [DllImport("user32.dll")]
    private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);
    [DllImport("user32.dll")]
    private static extern bool UnregisterHotKey(IntPtr hWnd, int id);
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    private static extern IntPtr FindWindow(string cls, string win);
    [DllImport("user32.dll")]
    private static extern bool ShowWindow(IntPtr h, int cmd);

    [StructLayout(LayoutKind.Sequential)]
    private struct MSG
    {
        public IntPtr hwnd;
        public uint message;
        public IntPtr wParam;
        public IntPtr lParam;
        public uint time;
        public int ptX;
        public int ptY;
    }

    [DllImport("user32.dll")]
    private static extern int GetMessage(out MSG lpMsg, IntPtr hWnd, uint wMsgFilterMin, uint wMsgFilterMax);
    [DllImport("user32.dll")]
    private static extern bool TranslateMessage(ref MSG lpMsg);
    [DllImport("user32.dll")]
    private static extern IntPtr DispatchMessage(ref MSG lpMsg);

    private const int HOTKEY_ID = 0xB10F;
    private const uint MOD_ALT = 0x0001;
    private const uint MOD_CONTROL = 0x0002;
    private const uint VK_F = 0x46;

    public static bool IsOn { get; private set; }

    public static void Start()
    {
        var th = new Thread(Loop);
        th.IsBackground = true;
        th.Start();
    }

    private static void Loop()
    {
        try
        {
            if (!RegisterHotKey(IntPtr.Zero, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_F)) return;
        }
        catch { return; }

        MSG msg;
        while (GetMessage(out msg, IntPtr.Zero, 0, 0) > 0)
        {
            if (msg.message == 0x0312 && msg.wParam.ToInt32() == HOTKEY_ID) Toggle();
            TranslateMessage(ref msg);
            DispatchMessage(ref msg);
        }
    }

    public static void Toggle()
    {
        IsOn = !IsOn;

        try
        {
            Bridge.WallpaperControl(IsOn ? "hideIcons" : "showIcons");
        }
        catch { }

        try
        {
            IntPtr tray = FindWindow("Shell_TrayWnd", null);
            if (tray != IntPtr.Zero) ShowWindow(tray, IsOn ? 0 : 5);
        }
        catch { }
    }
}
'''

if "internal static class FocusMode" not in t:
    t = t.rstrip() + "\n" + focus

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
