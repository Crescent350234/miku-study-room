import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_prompt = '\\"emphasis\\":[\\"歌词里最该强调的3-5个词\\"]}'
new_prompt = '\\"emphasis\\":[\\"歌词里最该强调的3-5个词\\"],\\"lineKeywords\\":[{\\"line\\":\\"原句\\",\\"keyword\\":\\"该句最关键的2-5字词语\\"}]}'

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if old_prompt in t:
        t = t.replace(old_prompt, new_prompt)
    else:
        print("prompt miss", d)

    # tilt: prefer per-line keyword
    old_key = """  function pickTiltKey(text, seed) {
    var candidates = [];"""
    new_key = """  function pickTiltKey(text, seed) {
    var candidates = [];

    if (S.aiTheme && S.aiTheme.lineKeywords) {
      for (var li = 0; li < S.aiTheme.lineKeywords.length; li++) {
        var lk = S.aiTheme.lineKeywords[li];
        if (lk && lk.line === text && lk.keyword && lk.keyword.length >= 2 && text.indexOf(lk.keyword) >= 0 && lk.keyword.length < text.length) {
          return lk.keyword;
        }
      }
    }"""
    if old_key in t:
        t = t.replace(old_key, new_key)
    else:
        print("tilt key anchor miss", d)

    # stack: prefer per-line keyword
    old_stack = """    var key = '';
    var keyColor = '';

    if (S.aiTheme && S.aiTheme.emphasis) {"""
    new_stack = """    var key = '';
    var keyColor = '';

    if (S.aiTheme && S.aiTheme.lineKeywords) {
      for (var li2 = 0; li2 < S.aiTheme.lineKeywords.length; li2++) {
        var lk2 = S.aiTheme.lineKeywords[li2];
        if (lk2 && lk2.line === text && lk2.keyword && lk2.keyword.length >= 2 && text.indexOf(lk2.keyword) >= 0 && lk2.keyword.length < text.length) {
          key = lk2.keyword;
          break;
        }
      }
    }

    if (!key && S.aiTheme && S.aiTheme.emphasis) {"""
    if old_stack in t:
        t = t.replace(old_stack, new_stack)
    else:
        print("stack key anchor miss", d)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=141", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
