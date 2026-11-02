import io, re

path = r"D:\MikuWallpaper\bridge\bridge.cs"
src = io.open(path, encoding="utf-8-sig").read()

# add using
if "using System.Collections.Generic;" not in src:
    src = src.replace("using System;\n", "using System;\nusing System.Collections.Generic;\n", 1)

# insert hotkey engine before Main
engine = r'''
    private static readonly Dictionary<string, List<byte>> Hotkeys = new Dictionary<string, List<byte>>();

    private static readonly Dictionary<string, byte> KeyMap = new Dictionary<string, byte>(StringComparer.OrdinalIgnoreCase)
    {
        { "ctrl", 0x11 }, { "control", 0x11 },
        { "alt", 0x12 }, { "menu", 0x12 },
        { "shift", 0x10 },
        { "win", 0x5B },
        { "left", 0x25 }, { "up", 0x26 }, { "right", 0x27 }, { "down", 0x28 },
        { "space", 0x20 }, { "enter", 0x0D }, { "tab", 0x09 }, { "esc", 0x1B },
        { "play", 0xB3 }, { "next", 0xB0 }, { "prev", 0xB1 }
    };

    private static byte KeyCode(string token)
    {
        byte code;
        if (KeyMap.TryGetValue(token, out code)) return code;
        if (token.Length == 1)
        {
            char c = char.ToUpperInvariant(token[0]);
            if (c >= 'A' && c <= 'Z') return (byte)c;
            if (c >= '0' && c <= '9') return (byte)c;
        }
        return 0;
    }

    private static void LoadHotkeys()
    {
        string file = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "hotkeys.ini");
        if (File.Exists(file))
        {
            foreach (string raw in File.ReadAllLines(file))
            {
                string line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#") || line.StartsWith(";")) continue;
                int eq = line.IndexOf('=');
                if (eq <= 0) continue;

                string name = line.Substring(0, eq).Trim().ToLowerInvariant();
                string combo = line.Substring(eq + 1).Trim();
                if (combo.Length == 0) continue;

                List<byte> keys = new List<byte>();
                bool ok = true;
                foreach (string token in combo.Split('+'))
                {
                    byte k = KeyCode(token.Trim());
                    if (k == 0) { ok = false; break; }
                    keys.Add(k);
                }
                if (ok && keys.Count > 0) Hotkeys[name] = keys;
            }
        }
    }

    private static void SendCombo(List<byte> keys)
    {
        for (int i = 0; i < keys.Count - 1; i++)
            keybd_event(keys[i], 0, 0, UIntPtr.Zero);

        byte main = keys[keys.Count - 1];
        keybd_event(main, 0, 0, UIntPtr.Zero);
        keybd_event(main, 0, 2, UIntPtr.Zero);

        for (int i = keys.Count - 2; i >= 0; i--)
            keybd_event(keys[i], 0, 2, UIntPtr.Zero);
    }

    private static void SendAction(string name)
    {
        List<byte> keys;
        if (Hotkeys.TryGetValue(name, out keys) && keys.Count > 0)
        {
            SendCombo(keys);
            return;
        }

        ushort vk = VK_MEDIA_PLAY_PAUSE;
        if (name == "next") vk = VK_MEDIA_NEXT;
        else if (name == "prev") vk = VK_MEDIA_PREV;
        PressMediaKey(vk);
    }

'''

if "private static void SendAction(string name)" not in src:
    src = src.replace("    private static void Main()", engine + "    private static void Main()", 1)

# load hotkeys at startup
if "LoadHotkeys();" not in src:
    src = src.replace("        using (var mutex = new Mutex(true, \"NowPlayingWallpaperBridge\", out createdNew))",
                      "        LoadHotkeys();\n\n        using (var mutex = new Mutex(true, \"NowPlayingWallpaperBridge\", out createdNew))", 1)

# replace route calls
src = src.replace('if (path.StartsWith("/next")) PressMediaKey(VK_MEDIA_NEXT);', 'if (path.StartsWith("/next")) SendAction("next");')
src = src.replace('else if (path.StartsWith("/prev")) PressMediaKey(VK_MEDIA_PREV);', 'else if (path.StartsWith("/prev")) SendAction("prev");')
src = src.replace('else if (path.StartsWith("/playpause")) PressMediaKey(VK_MEDIA_PLAY_PAUSE);', 'else if (path.StartsWith("/playpause")) SendAction("playpause");')

io.open(path, "w", encoding="utf-8", newline="").write(src)
print("bridge patched")
