import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

fn = r'''
    private static bool WallpaperControl(string command)
    {
        try
        {
            string exe = null;

            Process[] p32 = Process.GetProcessesByName("wallpaper32");
            if (p32.Length > 0)
            {
                try { exe = p32[0].MainModule.FileName; } catch { }
            }

            if (string.IsNullOrEmpty(exe))
            {
                Process[] p64 = Process.GetProcessesByName("wallpaper64");
                if (p64.Length > 0)
                {
                    try { exe = p64[0].MainModule.FileName; } catch { }
                }
            }

            if (string.IsNullOrEmpty(exe))
            {
                string[] guesses = new string[]
                {
                    @"C:\Program Files (x86)\Steam\steamapps\common\wallpaper_engine\wallpaper32.exe",
                    @"D:\Steam\steamapps\common\wallpaper_engine\wallpaper32.exe",
                    @"E:\Steam\steamapps\common\wallpaper_engine\wallpaper32.exe"
                };
                foreach (string g in guesses)
                {
                    if (File.Exists(g)) { exe = g; break; }
                }
            }

            if (string.IsNullOrEmpty(exe) || !File.Exists(exe)) return false;

            ProcessStartInfo psi = new ProcessStartInfo(exe, "-control " + command);
            psi.CreateNoWindow = true;
            psi.UseShellExecute = false;
            Process.Start(psi);
            return true;
        }
        catch
        {
            return false;
        }
    }

'''

if "WallpaperControl" not in t:
    t = t.replace("    private static void Main()", fn + "    private static void Main()", 1)

old_routes = '''                    if (path.StartsWith("/next")) SendAction("next");
                    else if (path.StartsWith("/prev")) SendAction("prev");
                    else if (path.StartsWith("/playpause")) SendAction("playpause");'''

new_routes = '''                    if (path.StartsWith("/next")) SendAction("next");
                    else if (path.StartsWith("/prev")) SendAction("prev");
                    else if (path.StartsWith("/playpause")) SendAction("playpause");
                    else if (path.StartsWith("/hideicons")) WallpaperControl("hideIcons");
                    else if (path.StartsWith("/showicons")) WallpaperControl("showIcons");'''

if old_routes in t:
    t = t.replace(old_routes, new_routes, 1)
else:
    print("route anchor miss")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("icon control added")
