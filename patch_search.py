import io, re

p = r"D:\MikuWallpaper\bridge\bridge.cs"
t = io.open(p, encoding="utf-8-sig").read()

if "using System.Text;" not in t:
    t = t.replace("using System.Collections.Generic;", "using System.Collections.Generic;\nusing System.Text;", 1)

t = t.replace('&type=1&offset=0&total=true&limit=1', '&type=1&offset=0&total=true&limit=10')

# remove debug log line
t = re.sub(r'\s*try \{ File\.AppendAllText\(@"D:\\MikuWallpaper\\bridge\\search\.log".*?\} catch \{ \}\r?\n', '\n', t, flags=re.S)

old_start = '                Dictionary<string, object> song = songs[0] as Dictionary<string, object>;'
old_end = '                string name = Convert.ToString(song["name"]);'

i = t.index(old_start)
j = t.index(old_end, i)

new_block = '''                Func<string, string> norm = delegate(string s)
                {
                    if (string.IsNullOrEmpty(s)) return "";
                    StringBuilder sb = new StringBuilder();
                    foreach (char ch in s.ToLowerInvariant())
                    {
                        if (char.IsLetterOrDigit(ch)) sb.Append(ch);
                    }
                    return sb.ToString();
                };

                string wantName = norm(title);
                string wantArtist = norm(artist);
                string titleLow = title.ToLowerInvariant();

                Dictionary<string, object> bestSong = null;
                int bestScore = -1000;

                foreach (object item in songs)
                {
                    Dictionary<string, object> so = item as Dictionary<string, object>;
                    if (so == null) continue;

                    string nm = Convert.ToString(so["name"]);
                    string nn = norm(nm);
                    int score = 0;

                    if (nn.Length > 0 && nn == wantName) score += 100;
                    else if (nn.Length > 0 && wantName.Length > 0 && (nn.Contains(wantName) || wantName.Contains(nn))) score += 65;

                    System.Collections.IList ar = so.ContainsKey("artists") ? so["artists"] as System.Collections.IList : null;
                    if (ar != null)
                    {
                        foreach (object ao in ar)
                        {
                            Dictionary<string, object> a = ao as Dictionary<string, object>;
                            if (a == null) continue;
                            string an = norm(Convert.ToString(a["name"]));
                            if (an.Length == 0) continue;
                            if (an == wantArtist) { score += 60; break; }
                            if (wantArtist.Length > 0 && (an.Contains(wantArtist) || wantArtist.Contains(an))) { score += 35; break; }
                        }
                    }

                    string low = nm.ToLowerInvariant();
                    bool suspicious = low.Contains("cover") || low.Contains("翻唱") || low.Contains("伴奏")
                        || low.Contains("dj") || low.Contains("live") || low.Contains("remix");
                    if (suspicious && !titleLow.Contains("live") && !titleLow.Contains("dj")) score -= 35;

                    if (score > bestScore) { bestScore = score; bestSong = so; }
                }

                Dictionary<string, object> song = bestSong != null ? bestSong : (songs[0] as Dictionary<string, object>);
                if (song == null) return null;
                string name = Convert.ToString(song["name"]);'''

t = t[:i] + new_block + t[j + len(old_end):]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("bridge search patched")
