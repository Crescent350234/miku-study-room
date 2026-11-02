import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    t = t.replace("var guideBtn2 = guideBtn2;", "var guideBtn2 = document.getElementById('guideBtn2');")
    t = t.replace("var openGuideBtn = openGuide;", "var openGuideBtn = document.getElementById('openGuide');")
    t = t.replace("var restartBridgeBtn = restartBridge;", "var restartBridgeBtn = document.getElementById('restartBridge');")

    t = t.replace("""    if (S.mode === 'mirror') {
      sendAction('playpause').catch(function () {});
      S.mirrorUserPaused = !S.playing;
      setPlaying(!S.playing);
      return;
    }""", """    if (S.mode === 'mirror') {
      var wasPlaying = S.playing;
      sendAction('playpause').catch(function () {});
      S.mirrorUserPaused = wasPlaying;
      setPlaying(!wasPlaying);
      return;
    }""")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=199", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
