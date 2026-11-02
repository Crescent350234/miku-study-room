import io

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = """  function colorizeLyric(text) {
    var base = (S.paletteHue != null ? S.paletteHue : 180);"""

new = """  function colorizeLyric(text) {
    var ai = S.aiTheme;
    if (ai && ai.wordColors && ai.wordColors.length) {
      var html = esc(text);
      ai.wordColors
        .filter(function (w) { return w && w.word && w.color; })
        .sort(function (a, b) { return b.word.length - a.word.length; })
        .forEach(function (w) {
          try {
            var safe = String(w.word).replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
            html = html.replace(new RegExp(safe, 'g'), '<span class="kw" style="color:' + w.color + '">' + esc(w.word) + '</span>');
          } catch (e) {}
        });
      return html;
    }

    var base = (S.paletteHue != null ? S.paletteHue : 180);"""

for d in dirs:
    p = d + r"\js\app.js"
    try:
        t = io.open(p, encoding="utf-8").read()
    except Exception:
        continue
    if "var ai = S.aiTheme;" not in t and old in t:
        t = t.replace(old, new, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("colorize", p)
