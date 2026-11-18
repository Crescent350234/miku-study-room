import io, re

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()
t = t.replace("['player', 'lyricsViewport'].forEach(function (id) {", "['player'].forEach(function (id) {")
io.open(p, "w", encoding="utf-8", newline="").write(t)

h = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\index.html"
s = io.open(h, encoding="utf-8").read()
s = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=286", s)
io.open(h, "w", encoding="utf-8", newline="").write(s)
print("lyrics region removed")

d = r"D:\MikuWallpaper\player\src\DesktopOverlay.cs"
c = io.open(d, encoding="utf-8-sig").read()

if "lastRegionTick" not in c:
    c = c.replace("long guardHeartbeat=Stopwatch.GetTimestamp();",
                  "long guardHeartbeat=Stopwatch.GetTimestamp();\n    long lastRegionTick=Stopwatch.GetTimestamp();")
    c = c.replace("pageWidth=data.width;pageHeight=data.height;",
                  "lastRegionTick=Stopwatch.GetTimestamp();pageWidth=data.width;pageHeight=data.height;")
    # auto-hide stale proxies inside guard
    c = c.replace("        Interlocked.Exchange(ref guardHeartbeat,Stopwatch.GetTimestamp());",
                  """        Interlocked.Exchange(ref guardHeartbeat,Stopwatch.GetTimestamp());
        if((Stopwatch.GetTimestamp()-Interlocked.Read(ref lastRegionTick))/(double)Stopwatch.Frequency>3&&proxies.Any(p=>p.Visible)){
            foreach(InputProxy proxy in proxies)proxy.Hide();
            presence.Active=false;
        }""", 1)
    print("stale proxy guard added")
else:
    print("exists")

io.open(d, "w", encoding="utf-8", newline="").write(c)
