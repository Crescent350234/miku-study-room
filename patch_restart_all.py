import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

route = '''                        else if (path.StartsWith("/restart.all"))
                        {
                            Send(stream, "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("ok"));
                            ThreadPool.QueueUserWorkItem(delegate
                            {
                                try { EnsureWatchdog(); } catch { }
                                Thread.Sleep(800);
                                try
                                {
                                    var wq = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:51790/restart");
                                    wq.Timeout = 2000;
                                    using (var wr = (HttpWebResponse)wq.GetResponse()) { }
                                }
                                catch { }
                                Thread.Sleep(300);
                                Environment.Exit(0);
                            });
                        }
'''

if "/restart.all" not in t:
    anchor = 'else if (path.StartsWith("/hideicons"))'
    t = t.replace(anchor, route + '                        ' + anchor, 1)

method = '''
    private static void EnsureWatchdog()
    {
        try
        {
            if (Process.GetProcessesByName("watchdog").Length > 0) return;

            string[] cands = new string[]
            {
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "watchdog.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\\bridge\\watchdog.exe")
            };

            foreach (string c in cands)
            {
                if (!File.Exists(c)) continue;
                var psi = new ProcessStartInfo(c, "");
                psi.WorkingDirectory = Path.GetDirectoryName(c);
                psi.UseShellExecute = true;
                psi.WindowStyle = ProcessWindowStyle.Hidden;
                Process.Start(psi);
                return;
            }
        }
        catch { }
    }

'''

if "private static void EnsureWatchdog" not in t:
    anchor = "    internal static bool WallpaperControl(string command)"
    t = t.replace(anchor, method + anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge patched")
