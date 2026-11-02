import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

old = """            if (!RegisterHotKey(IntPtr.Zero, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_F)) return;"""
new = """            bool ok = RegisterHotKey(IntPtr.Zero, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_F);
            try { File.AppendAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "focus.log"), DateTime.Now.ToString("HH:mm:ss") + " hotkey=" + ok + "\\r\\n"); } catch { }
            if (!ok) return;"""
if old in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("patched log")
else:
    print("anchor miss")
