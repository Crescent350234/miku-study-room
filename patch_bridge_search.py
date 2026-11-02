import io, re

path = r"D:\MikuWallpaper\bridge\bridge.cs"
src = io.open(path, encoding="utf-8-sig").read()

# 1) usings
if "using System.Collections.Generic;" not in src:
    src = src.replace("using System;\n", "using System;\nusing System.Collections.Generic;\n", 1)
if "using System.Web.Script.Serialization;" not in src:
    src = src.replace("using System.Threading;\n", "using System.Threading;\nusing System.Web.Script.Serialization;\n", 1)

# 2) replace old GetNowJson block with search-enabled version
start = src.index("    private static string GetNowJson()")
# find the matching end: the method ends before "    private static void Main()"
end = src.index("    private static void Main()", start)
old_block = src[start:end]

new_block = r'''    private static readonly Dictionary<string, string> NowCache = new Dictionary<string, string>();

    private static string SearchSong(string title, string artist, out string id, out long duration)
    {
        id = "";
        duration = 0;

        try
        {
            string q = Uri.EscapeDataString((title + " " + artist).Trim());
            string url = "https://music.163.com/api/search/get/web?csrf_token=&s=" + q + "&type=1&offset=0&total=true&limit=1";

            HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
            req.UserAgent = "Mozilla/5.0";
            req.Referer = "https://music.163.com/";
            req.Timeout = 4000;

            using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
            using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8))
            {
                string json = sr.ReadToEnd();
                JavaScriptSerializer ser = new JavaScriptSerializer();
                Dictionary<string, object> root = ser.Deserialize<Dictionary<string, object>>(json);
                if (root == null || !root.ContainsKey("result")) return null;

                Dictionary<string, object> result = root["result"] as Dictionary<string, object>;
                if (result == null || !result.ContainsKey("songs")) return null;

                object[] songs = result["songs"] as object[];
                if (songs == null || songs.Length == 0) return null;

                Dictionary<string, object> song = songs[0] as Dictionary<string, object>;
                if (song == null) return null;

                id = Convert.ToString(song["id"]);
                if (song.ContainsKey("duration") && song["duration"] != null)
                    long.TryParse(Convert.ToString(song["duration"]), out duration);

                string name = Convert.ToString(song["name"]);
                string art = "";
                object[] artists = song.ContainsKey("artists") ? song["artists"] as object[] : null;
                if (artists != null && artists.Length > 0)
                {
                    Dictionary<string, object> a = artists[0] as Dictionary<string, object>;
                    if (a != null) art = Convert.ToString(a["name"]);
                }

                return name + "\u0001" + art;
            }
        }
        catch
        {
            return null;
        }
    }

    private static string GetNowJson()
    {
        try
        {
            foreach (Process p in Process.GetProcessesByName("cloudmusic"))
            {
                string t = p.MainWindowTitle;
                if (string.IsNullOrWhiteSpace(t)) continue;

                string title = t;
                string artist = "";
                int idx = t.LastIndexOf(" - ", StringComparison.Ordinal);
                if (idx > 0)
                {
                    title = t.Substring(0, idx).Trim();
                    artist = t.Substring(idx + 3).Trim();
                }

                string key = title + "|" + artist;
                if (NowCache.ContainsKey(key)) return NowCache[key];

                string id;
                long duration;
                string found = SearchSong(title, artist, out id, out duration);

                if (!string.IsNullOrEmpty(found))
                {
                    string[] parts = found.Split('\u0001');
                    if (parts.Length > 1 && !string.IsNullOrEmpty(parts[1])) artist = parts[1];
                }

                string json;
                if (!string.IsNullOrEmpty(id))
                {
                    string pic = "https://api.injahow.cn/meting/?server=netease&type=pic&id=" + id;
                    string lrc = "https://api.injahow.cn/meting/?server=netease&type=lrc&id=" + id;
                    json = "{\"ok\":true,\"title\":\"" + Esc(title) + "\",\"artist\":\"" + Esc(artist) +
                           "\",\"id\":\"" + id + "\",\"pic\":\"" + Esc(pic) + "\",\"lrc\":\"" + Esc(lrc) +
                           "\",\"duration\":" + (duration / 1000) + "}";
                }
                else
                {
                    json = "{\"ok\":true,\"title\":\"" + Esc(title) + "\",\"artist\":\"" + Esc(artist) + "\",\"id\":\"\"}";
                }

                if (NowCache.Count > 80) NowCache.Clear();
                NowCache[key] = json;
                return json;
            }
        }
        catch { }

        return "{\"ok\":false}";
    }

'''

src = src[:start] + new_block + src[end:]
io.open(path, "w", encoding="utf-8", newline="").write(src)
print("patched")
