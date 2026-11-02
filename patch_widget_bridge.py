import io

p = r"D:\MikuWallpaper\pomodoro\Pomodoro.cs"
t = io.open(p, encoding="utf-8").read()

if "bridgePath" not in t:
    t = t.replace(
        "    private string statePath;",
        "    private string statePath;\n    private string bridgePath;",
    )
    t = t.replace(
        "            if (proj != null) statePath = Path.Combine(proj, \"pomo.json\");",
        "            if (proj != null) statePath = Path.Combine(proj, \"pomo.json\");\n"
        "            bridgePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @\"MikuWallpaper\\bridge\\pomo.json\");",
    )
    t = t.replace(
        "            File.WriteAllText(statePath, json, new UTF8Encoding(false));",
        "            File.WriteAllText(statePath, json, new UTF8Encoding(false));\n"
        "            if (!string.IsNullOrEmpty(bridgePath)) File.WriteAllText(bridgePath, json, new UTF8Encoding(false));",
    )
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("patched")
else:
    print("already")
