import io, re

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

# --- add ReadAiIni helper before ProxyAi ---
ini_fn = r'''
    private static Dictionary<string, string> ReadAiIni()
    {
        Dictionary<string, string> d = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        try
        {
            string file = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "ai.ini");
            if (!File.Exists(file)) return d;
            foreach (string raw in File.ReadAllLines(file, Encoding.UTF8))
            {
                string line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#") || line.StartsWith(";")) continue;
                int eq = line.IndexOf('=');
                if (eq <= 0) continue;
                d[line.Substring(0, eq).Trim()] = line.Substring(eq + 1).Trim();
            }
        }
        catch { }
        return d;
    }

'''

if "ReadAiIni" not in t:
    t = t.replace("    private static string ProxyAi(string path)", ini_fn + "    private static string ProxyAi(string path)", 1)

# --- ProxyAi: use ini config and only prompt param ---
start = t.index("    private static string ProxyAi(string path)")
end = t.index("    private static string Quote(string s)", start)

new_proxy = r'''    private static string ProxyAi(string path)
    {
        try
        {
            Dictionary<string, string> cfg = ReadAiIni();
            string enabled = cfg.ContainsKey("enabled") ? cfg["enabled"] : "0";
            if (enabled != "1")
                return "{\"error\":\"ai disabled in ai.ini\"}";

            string baseUrl = cfg.ContainsKey("base") ? cfg["base"].Trim().TrimEnd('/') : "";
            string key = cfg.ContainsKey("key") ? cfg["key"].Trim() : "";
            string model = cfg.ContainsKey("model") ? cfg["model"].Trim() : "";

            if (baseUrl.Length == 0 || key.Length == 0)
                return "{\"error\":\"ai.ini missing base or key\"}";

            string q = path.Contains("?") ? path.Substring(path.IndexOf('?')) : "";
            string prompt = B64(QueryValue(q, "p"));
            if (prompt.Length == 0)
                return "{\"error\":\"empty prompt\"}";

            JavaScriptSerializer ser = new JavaScriptSerializer();
            ser.MaxJsonLength = 1024 * 1024;

            var payload = new Dictionary<string, object>();
            payload["model"] = model.Length > 0 ? model : "deepseek-chat";
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

'''

t = t[:start] + new_proxy + t[end:]

# --- /ai.config route ---
route_new = '''                        else if (path.StartsWith("/ai.config"))
                        {
                            Dictionary<string, string> cfg = ReadAiIni();
                            string en = cfg.ContainsKey("enabled") && cfg["enabled"] == "1" ? "true" : "false";
                            string bse = cfg.ContainsKey("base") ? cfg["base"] : "";
                            string mdl = cfg.ContainsKey("model") ? cfg["model"] : "";
                            string json = "{\\"enabled\\":" + en + ",\\"base\\":\\"" + Esc(bse) + "\\",\\"model\\":\\"" + Esc(mdl) + "\\"}";
                            Send(stream, "application/json; charset=utf-8", Encoding.UTF8.GetBytes(json));
                        }
                        else if (path.StartsWith("/ai.theme"))'''

if "/ai.config" not in t:
    t = t.replace('                        else if (path.StartsWith("/ai.theme"))', route_new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge ai.ini support added")
