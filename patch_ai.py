import io, re

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

# bigger buffer + read headers fully
t = t.replace("byte[] buffer = new byte[4096];", "byte[] buffer = new byte[65536];")

old_read = """                        int read = stream.Read(buffer, 0, buffer.Length);
                        if (read <= 0) continue;

                        string request = Encoding.ASCII.GetString(buffer, 0, read);"""
new_read = """                        int read = 0;
                        int total = 0;
                        while (total < buffer.Length)
                        {
                            read = stream.Read(buffer, total, buffer.Length - total);
                            if (read <= 0) break;
                            total += read;
                            string sofar = Encoding.ASCII.GetString(buffer, 0, total);
                            if (sofar.IndexOf("\\r\\n\\r\\n") >= 0) break;
                        }
                        if (total <= 0) continue;

                        string request = Encoding.ASCII.GetString(buffer, 0, total);"""
if old_read in t:
    t = t.replace(old_read, new_read, 1)

# insert route
route_anchor = '''                        }                        else if (path.StartsWith("/now.json"))'''
route_new = '''                        }
                        else if (path.StartsWith("/ai.theme"))
                        {
                            Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes(ProxyAi(path)));
                        }
                        else if (path.StartsWith("/now.json"))'''
if "/ai.theme" not in t and route_anchor in t:
    t = t.replace(route_anchor, route_new, 1)

fn = r'''
    private static string QueryValue(string query, string key)
    {
        if (string.IsNullOrEmpty(query)) return "";
        string q = query.StartsWith("?") ? query.Substring(1) : query;
        foreach (string pair in q.Split('&'))
        {
            int eq = pair.IndexOf('=');
            if (eq <= 0) continue;
            if (pair.Substring(0, eq) == key)
                return Uri.UnescapeDataString(pair.Substring(eq + 1).Replace("+", " "));
        }
        return "";
    }

    private static string B64(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        s = s.Replace(" ", "+");
        int mod = s.Length % 4;
        if (mod == 2) s += "==";
        else if (mod == 3) s += "=";
        else if (mod == 1) s += "===";
        return Encoding.UTF8.GetString(Convert.FromBase64String(s));
    }

    private static string ProxyAi(string path)
    {
        try
        {
            string q = path.Contains("?") ? path.Substring(path.IndexOf('?')) : "";
            string baseUrl = B64(QueryValue(q, "b")).Trim().TrimEnd('/');
            string key = B64(QueryValue(q, "k")).Trim();
            string model = B64(QueryValue(q, "m")).Trim();
            string prompt = B64(QueryValue(q, "p"));

            if (baseUrl.Length == 0 || key.Length == 0 || prompt.Length == 0)
                return "{\"error\":\"missing ai config\"}";

            JavaScriptSerializer ser = new JavaScriptSerializer();
            ser.MaxJsonLength = 1024 * 1024;

            var payload = new Dictionary<string, object>();
            payload["model"] = model.Length > 0 ? model : "gpt-4o-mini";
            payload["temperature"] = 0.8;
            payload["messages"] = new object[]
            {
                new Dictionary<string, object>
                {
                    { "role", "user" },
                    { "content", prompt }
                }
            };

            string body = ser.Serialize(payload);

            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
            HttpWebRequest req = (HttpWebRequest)WebRequest.Create(baseUrl + "/chat/completions");
            req.Method = "POST";
            req.ContentType = "application/json";
            req.Headers["Authorization"] = "Bearer " + key;
            req.Proxy = null;
            req.Timeout = 60000;

            byte[] bytes = Encoding.UTF8.GetBytes(body);
            req.ContentLength = bytes.Length;
            using (Stream rs = req.GetRequestStream()) rs.Write(bytes, 0, bytes.Length);

            using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
            using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
            {
                return sr.ReadToEnd();
            }
        }
        catch (WebException wex)
        {
            try
            {
                if (wex.Response != null)
                {
                    using (StreamReader er = new StreamReader(wex.Response.GetResponseStream(), Encoding.UTF8))
                        return "{\"error\":" + Quote(er.ReadToEnd()) + "}";
                }
            }
            catch { }
            return "{\"error\":" + Quote(wex.Message) + "}";
        }
        catch (Exception ex)
        {
            return "{\"error\":" + Quote(ex.Message) + "}";
        }
    }

    private static string Quote(string s)
    {
        return "\"" + Esc(s) + "\"";
    }

'''

if "private static string ProxyAi" not in t:
    t = t.replace("    private static void Main()", fn + "    private static void Main()", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("ai proxy added")
