import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

t = t.replace(
    "private static bool FindInQueue(string title, string artist, out string id, out long duration)",
    "private static bool FindInQueue(string title, string artist, out string id, out long duration, out string pic)"
)
t = t.replace(
    "        id = \"\";\n        duration = 0;\n        try",
    "        id = \"\";\n        duration = 0;\n        pic = \"\";\n        try",
    1
)
t = t.replace(
    "                    id = Convert.ToString(tr[\"id\"]);\n                    duration = 0;",
    "                    id = Convert.ToString(tr[\"id\"]);\n                    duration = 0;\n                    pic = \"\";\n                    if (tr.ContainsKey(\"album\"))\n                    {\n                        Dictionary<string, object> al = tr[\"album\"] as Dictionary<string, object>;\n                        if (al != null && al.ContainsKey(\"picUrl\")) pic = Convert.ToString(al[\"picUrl\"]);\n                    }"
)

t = t.replace(
    "                string found = null;\n                if (!FindInQueue(title, artist, out id, out duration))",
    "                string found = null;\n                string queuePic;\n                if (!FindInQueue(title, artist, out id, out duration, out queuePic))"
)
t = t.replace(
    "                    string pic = GetCover(id);\n                    if (string.IsNullOrEmpty(pic)) pic = \"https://api.injahow.cn/meting/?server=netease&type=pic&id=\" + id;",
    "                    string pic = queuePic;\n                    if (string.IsNullOrEmpty(pic)) pic = GetCover(id);\n                    if (string.IsNullOrEmpty(pic)) pic = \"https://api.injahow.cn/meting/?server=netease&type=pic&id=\" + id;"
)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("queue pic patched")
