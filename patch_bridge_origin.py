import io

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8").read()

# 1) CORS 头改成动态，并加 nosniff
t = t.replace(
'''            "Access-Control-Allow-Origin: *\\r\\n" +
            "Access-Control-Allow-Private-Network: true\\r\\n" +''',
'''            "Access-Control-Allow-Origin: " + _acao + "\\r\\n" +
            "Vary: Origin\\r\\n" +
            "X-Content-Type-Options: nosniff\\r\\n" +
            "Access-Control-Allow-Private-Network: true\\r\\n" +''')

# 2) 静态字段
if "private static string _acao" not in t:
    t = t.replace("    private static string Esc(string s)",
                  "    private static string _acao = \"null\";\n\n    private static string Esc(string s)", 1)

# 3) 请求来源校验（插在 path 解析之后）
anchor = "                        if (parts.Length > 1) { rawPath = parts[1]; path = rawPath.ToLowerInvariant(); }"
check = anchor + '''

                        string origin = GetHeader(request, "Origin");
                        string referer = GetHeader(request, "Referer");
                        bool blockedOrigin = false;

                        if (!string.IsNullOrEmpty(origin))
                        {
                            string o = origin.Trim().ToLowerInvariant();
                            if (o != "null" && !o.StartsWith("file:")) blockedOrigin = true;
                        }
                        else if (!string.IsNullOrEmpty(referer))
                        {
                            string rf = referer.Trim().ToLowerInvariant();
                            if (rf.StartsWith("http://") || rf.StartsWith("https://")) blockedOrigin = true;
                        }

                        if (blockedOrigin)
                        {
                            Send403(stream);
                            continue;
                        }

                        _acao = string.IsNullOrEmpty(origin) ? "null" : origin.Trim();'''
if "blockedOrigin" not in t:
    t = t.replace(anchor, check, 1)

# 4) 辅助方法
helpers = '''
    private static string GetHeader(string request, string name)
    {
        foreach (string line in request.Split('\\n'))
        {
            int c = line.IndexOf(':');
            if (c <= 0) continue;
            if (line.Substring(0, c).Trim().Equals(name, StringComparison.OrdinalIgnoreCase))
            {
                string v = line.Substring(c + 1).Trim();
                StringBuilder sb = new StringBuilder();
                foreach (char ch in v)
                {
                    if (ch >= 32 && ch != '"') sb.Append(ch);
                }
                return sb.ToString();
            }
        }
        return null;
    }

    private static void Send403(NetworkStream stream)
    {
        byte[] b = Encoding.ASCII.GetBytes("HTTP/1.1 403 Forbidden\\r\\nContent-Length: 0\\r\\nConnection: close\\r\\n\\r\\n");
        stream.Write(b, 0, b.Length);
        stream.Flush();
    }

'''
if "private static string GetHeader" not in t:
    t = t.replace("    private static void Main()", helpers + "    private static void Main()", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
