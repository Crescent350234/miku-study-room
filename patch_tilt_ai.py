import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_prompt = """      'JSON 字段：{"name":"4字主题名","accent":"#RRGGBB","background":"#RRGGBB","primary":"#RRGGBB","secondary":"#RRGGBB","wordColors":[{"word":"歌词里的词","color":"#RRGGBB"}]}\\n' +"""
new_prompt = """      'JSON 字段：{"name":"4字主题名","accent":"#RRGGBB","background":"#RRGGBB","primary":"#RRGGBB","secondary":"#RRGGBB","wordColors":[{"word":"歌词里的词","color":"#RRGGBB"}],"emphasis":["歌词里最该强调的3-5个词"]}\\n' +"""

old_hl = """        var chars = Array.from(part);
        var hlStart = Math.max(0, Math.floor((chars.length - 2) / 2));
        chars.forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc2';
          if (ci >= hlStart && ci < hlStart + 2) c.className += ' tilt-hl';"""

new_hl = """        var chars = Array.from(part);
        var hlStart = Math.max(0, Math.floor((chars.length - 2) / 2));
        var hlLen = 2;
        var hlColor = '';

        if (S.aiTheme && S.aiTheme.emphasis && S.aiTheme.emphasis.length) {
          var bestWord = '';
          S.aiTheme.emphasis.forEach(function (w) {
            if (w && part.indexOf(w) >= 0 && w.length > bestWord.length) bestWord = w;
          });
          if (bestWord) {
            hlStart = part.indexOf(bestWord);
            hlLen = bestWord.length;
            if (S.aiTheme.wordColors) {
              S.aiTheme.wordColors.forEach(function (wc) {
                if (wc && wc.word === bestWord && wc.color) hlColor = wc.color;
              });
            }
          }
        }

        chars.forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc2';
          if (ci >= hlStart && ci < hlStart + hlLen) {
            c.className += ' tilt-hl';
            if (hlColor) c.style.color = hlColor;
          }"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old_prompt in t:
        t = t.replace(old_prompt, new_prompt)
    else:
        print("prompt miss", d)
    if old_hl in t:
        t = t.replace(old_hl, new_hl)
    else:
        print("hl miss", d)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=133", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
