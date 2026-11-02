import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                            string pj = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "pomo.json");
                            string json = "{\\"focus\\":false,\\"running\\":false,\\"remain\\":1500}";
                            try { if (System.IO.File.Exists(pj)) json = System.IO.File.ReadAllText(pj); } catch { }'''
new = '''                            string pj = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "pomo.json");
                            string pj2 = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"MikuWallpaper\\bridge\\pomo.json");
                            string json = "{\\"focus\\":false,\\"running\\":false,\\"remain\\":1500}";
                            try
                            {
                                if (System.IO.File.Exists(pj2) && (!System.IO.File.Exists(pj) || System.IO.File.GetLastWriteTimeUtc(pj2) >= System.IO.File.GetLastWriteTimeUtc(pj)))
                                    json = System.IO.File.ReadAllText(pj2);
                                else if (System.IO.File.Exists(pj))
                                    json = System.IO.File.ReadAllText(pj);
                            }
                            catch { }'''
if old in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("bridge route patched")
else:
    print("anchor miss")
