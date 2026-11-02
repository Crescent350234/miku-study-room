import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

old = """            bool ok = RegisterHotKey(IntPtr.Zero, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_F);
            try { File.AppendAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "focus.log"), DateTime.Now.ToString("HH:mm:ss") + " hotkey=" + ok + "\\r\\n"); } catch { }
            if (!ok) return;"""

new = """            uint[][] combos = new uint[][]
            {
                new uint[] { MOD_CONTROL | MOD_ALT, 0x46 },   // Ctrl+Alt+F
                new uint[] { MOD_CONTROL | MOD_ALT, 0x4D },   // Ctrl+Alt+M
                new uint[] { MOD_CONTROL | MOD_SHIFT, 0x46 }, // Ctrl+Shift+F
                new uint[] { MOD_ALT | MOD_SHIFT, 0x46 },     // Alt+Shift+F
                new uint[] { 0, 0x77 }                        // F8
            };
            bool ok = false;
            string picked = "";
            foreach (uint[] c in combos)
            {
                if (RegisterHotKey(IntPtr.Zero, HOTKEY_ID, c[0], c[1])) { ok = true; picked = c[0] + "/" + c[1]; break; }
            }
            try { File.AppendAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "focus.log"), DateTime.Now.ToString("HH:mm:ss") + " hotkey=" + ok + " " + picked + "\\r\\n"); } catch { }
            if (!ok) return;"""

if old in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("patched combos")
else:
    print("anchor miss")
