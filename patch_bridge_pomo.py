import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

if "/pomo.json" not in t:
    anchor = """                        else if (path.StartsWith("/now.json"))
                        {
                            Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes(GetNowJson()));
                        }"""
    add = anchor + """
                        else if (path.StartsWith("/pomo.json"))
                        {
                            string pj = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "pomo.json");
                            string json = "{\\"focus\\":false,\\"running\\":false,\\"remain\\":1500}";
                            try { if (System.IO.File.Exists(pj)) json = System.IO.File.ReadAllText(pj); } catch { }
                            Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes(json));
                        }"""
    t = t.replace(anchor, add, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("bridge patched")
else:
    print("already")
