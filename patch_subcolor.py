import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

fn = r'''
  function colorizeSub(text) {
    var pal = lyricPalette();
    var chars = Array.from(String(text || ''));
    var out = '';

    chars.forEach(function (ch, i) {
      if (/\s/.test(ch)) {
        out += ' ';
        return;
      }

      var color = '';
      if (i % 5 === 2) color = pal[1];
      else if (i % 5 === 4) color = pal[2];

      out += color
        ? '<span class="sub-ch" style="color:' + color + '">' + esc(ch) + '</span>'
        : esc(ch);
    });

    return out;
  }
'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function colorizeSub" not in t:
        t = t.replace("  function colorizeLyric(text) {", fn + "\n  function colorizeLyric(text) {", 1)

    t = t.replace("(line.sub ? '<span class=\"sub\">' + esc(line.sub) + '</span>' : '')",
                  "(line.sub ? '<span class=\"sub\">' + colorizeSub(line.sub) + '</span>' : '')")

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "翻译逐字变色" not in ct:
            ct += '''

/* 翻译逐字变色（不发光） */
.line .sub .sub-ch {
  display: inline;
  text-shadow: none !important;
  filter: none !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=123", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
