import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

helper = r'''
  function morandi(color, maxS, minL, maxL) {
    var c = cssHsl(color);
    var s = Math.min(maxS == null ? 0.30 : maxS, c.s);
    var l = Math.min(maxL == null ? 0.78 : maxL, Math.max(minL == null ? 0.42 : minL, c.l));
    return 'hsl(' + Math.round(c.h) + ', ' + Math.round(s * 100) + '%, ' + Math.round(l * 100) + '%)';
  }
'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function morandi(" not in t:
        t = t.replace("  function lyricPalette() {", helper + "\n  function lyricPalette() {", 1)

    # cover palette -> low saturation
    t = t.replace("document.body.style.setProperty('--accent', 'hsl(' + p.h2 + ' 72% 62%)');",
                  "document.body.style.setProperty('--accent', 'hsl(' + p.h2 + ' 30% 64%)');")
    t = t.replace("document.body.style.setProperty('--pink', 'hsl(' + ((p.h2 + 320) % 360) + ' 62% 64%)');",
                  "document.body.style.setProperty('--pink', 'hsl(' + ((p.h2 + 320) % 360) + ' 26% 68%)');")
    t = t.replace("document.body.style.setProperty('--theme-bg', 'hsl(' + p.h1 + ' 30% 10%)');",
                  "document.body.style.setProperty('--theme-bg', 'hsl(' + p.h1 + ' 12% 11%)');")
    t = t.replace("document.body.style.setProperty('--theme-primary', 'hsl(' + p.h1 + ' 28% 94%)');",
                  "document.body.style.setProperty('--theme-primary', 'hsl(' + p.h1 + ' 10% 92%)');")

    # AI theme colors desaturated
    t = t.replace("document.body.style.setProperty('--accent', t.accent);",
                  "document.body.style.setProperty('--accent', morandi(t.accent, 0.30, 0.45, 0.72));")
    t = t.replace("if (t.secondary) document.body.style.setProperty('--pink', t.secondary);",
                  "if (t.secondary) document.body.style.setProperty('--pink', morandi(t.secondary, 0.26, 0.50, 0.74));")
    t = t.replace("if (t.background) document.body.style.setProperty('--theme-bg', t.background);",
                  "if (t.background) document.body.style.setProperty('--theme-bg', morandi(t.background, 0.14, 0.08, 0.20));")
    t = t.replace("if (t.primary) document.body.style.setProperty('--theme-primary', t.primary);",
                  "if (t.primary) document.body.style.setProperty('--theme-primary', morandi(t.primary, 0.12, 0.82, 0.96));")

    # keyword colors -> muted
    t = t.replace("return '<span class=\"kw\" style=\"color:hsl(' + hue + ' 78% 72%)\">' + esc(part) + '</span>';",
                  "return '<span class=\"kw\" style=\"color:hsl(' + hue + ' 34% 70%)\">' + esc(part) + '</span>';")

    # lyric palette saturation clamp
    t = t.replace("var s = Math.max(0.35, Math.min(0.85, base.s));",
                  "var s = Math.max(0.16, Math.min(0.30, base.s));")

    # complement subdued
    t = t.replace("var s = Math.max(0.55, Math.min(0.9, base.s));",
                  "var s = Math.max(0.20, Math.min(0.32, base.s));")

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=114", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
