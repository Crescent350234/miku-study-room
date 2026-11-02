import io, re

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

helper = r'''
    private static string Norm(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        StringBuilder sb = new StringBuilder();
        foreach (char ch in s.ToLowerInvariant())
        {
            if (char.IsLetterOrDigit(ch)) sb.Append(ch);
        }
        return sb.ToString();
    }

    private static bool FindInQueue(string title, string artist, out string id, out long duration)
    {
        id = "";
        duration = 0;
        try
        {
            string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                @"NetEase\CloudMusic\webdata\file\playingList");
            if (!File.Exists(path)) return false;

            JavaScriptSerializer ser = new JavaScriptSerializer();
            Dictionary<string, object> root = ser.Deserialize<Dictionary<string, object>>(File.ReadAllText(path, Encoding.UTF8));
            System.Collections.IList list = root.ContainsKey("list") ? root["list"] as System.Collections.IList : null;
            if (list == null) return false;

            string wantName = Norm(title);
            string wantArtist = Norm(artist);
            int best = 0;

            foreach (object item in list)
            {
                Dictionary<string, object> it = item as Dictionary<string, object>;
                if (it == null || !it.ContainsKey("track")) continue;
                Dictionary<string, object> tr = it["track"] as Dictionary<string, object>;
                if (tr == null || !tr.ContainsKey("name")) continue;

                string nm = Norm(Convert.ToString(tr["name"]));
                int score = 0;
                if (nm.Length > 0 && nm == wantName) score += 100;
                else if (nm.Length > 0 && wantName.Length > 0 && (nm.Contains(wantName) || wantName.Contains(nm))) score += 60;
                else continue;

                System.Collections.IList ar = tr.ContainsKey("artists") ? tr["artists"] as System.Collections.IList : null;
                if (ar != null)
                {
                    foreach (object ao in ar)
                    {
                        Dictionary<string, object> a = ao as Dictionary<string, object>;
                        if (a == null) continue;
                        string an = Norm(Convert.ToString(a["name"]));
                        if (an.Length == 0) continue;
                        if (an == wantArtist) { score += 60; break; }
                        if (wantArtist.Length > 0 && (an.Contains(wantArtist) || wantArtist.Contains(an))) { score += 30; break; }
                    }
                }

                if (score > best)
                {
                    best = score;
                    id = Convert.ToString(tr["id"]);
                    duration = 0;
                    if (tr.ContainsKey("duration") && tr["duration"] != null)
                        long.TryParse(Convert.ToString(tr["duration"]), out duration);
                }
            }

            return !string.IsNullOrEmpty(id);
        }
        catch
        {
            return false;
        }
    }

'''

if "private static bool FindInQueue" not in t:
    t = t.replace("    private static string SearchSong(string title, string artist", helper + "    private static string SearchSong(string title, string artist", 1)

# replace local delegate with Norm
t = re.sub(
    r'Func<string, string> norm = delegate\(string s\)\s*\{.*?\n\s*\};\r?\n',
    'Func<string, string> norm = Norm;\n',
    t,
    count=1,
    flags=re.S,
)

# queue-first in GetNowJson
old = '''                string found = SearchSong(title, artist, out id, out duration);

                if (!string.IsNullOrEmpty(found))'''
new = '''                string found = null;
                if (!FindInQueue(title, artist, out id, out duration))
                {
                    found = SearchSong(title, artist, out id, out duration);
                }

                if (!string.IsNullOrEmpty(found))'''
if old in t:
    t = t.replace(old, new, 1)
else:
    print("GetNowJson anchor miss")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("queue lookup patched")
