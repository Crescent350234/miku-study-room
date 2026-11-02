import io

p = r"D:\MikuWallpaper\watchdog.cs"
t = io.open(p, encoding="utf-8").read()

# 1) Origin 校验
if "blockedOrigin" not in t:
    anchor = '                        string req = Encoding.ASCII.GetString(buf, 0, n);\n'
    check = anchor + '''
                        string origin = Hdr(req, "Origin");
                        string referer = Hdr(req, "Referer");
                        bool blockedOrigin = false;
                        if (!string.IsNullOrEmpty(origin))
                        {
                            string o = origin.ToLowerInvariant();
                            if (o != "null" && !o.StartsWith("file:")) blockedOrigin = true;
                        }
                        else if (!string.IsNullOrEmpty(referer))
                        {
                            string rf = referer.ToLowerInvariant();
                            if (rf.StartsWith("http://") || rf.StartsWith("https://")) blockedOrigin = true;
                        }
                        if (blockedOrigin)
                        {
                            Write(ns, "HTTP/1.1 403 Forbidden\\r\\nContent-Length: 0\\r\\nConnection: close\\r\\n\\r\\n");
                            continue;
                        }
'''
    assert anchor in t
    t = t.replace(anchor, check, 1)

# 2) ACAO 回显（整行替换）
out = []
for line in t.split("\n"):
    if "Access-Control-Allow-Origin: *" in line:
        indent = line[:len(line) - len(line.lstrip())]
        out.append(indent + '"Access-Control-Allow-Origin: " + (string.IsNullOrEmpty(origin) ? "null" : origin) + "\\r\\n" +')
    else:
        out.append(line)
t = "\n".join(out)

# 3) Hdr 辅助
helper = '''
    static string Hdr(string req, string name)
    {
        foreach (string line in req.Split('\\n'))
        {
            int c = line.IndexOf(':');
            if (c <= 0) continue;
            if (line.Substring(0, c).Trim().Equals(name, StringComparison.OrdinalIgnoreCase))
                return line.Substring(c + 1).Trim();
        }
        return null;
    }

'''
if "static string Hdr(" not in t:
    t = t.replace("    static void Write(NetworkStream ns, string s)", helper + "    static void Write(NetworkStream ns, string s)", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("watchdog patched")
