import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_pal = """  function lyricPalette() {
    var cs = getComputedStyle(document.body);
    var a = (cs.getPropertyValue('--accent') || '').trim() || '#7fd6ff';
    var p = (cs.getPropertyValue('--pink') || '').trim() || '#ff9ecb';
    return ['#ffffff', a, p, '#ffd479', '#c9a7ff'];
  }"""

new_pal = r"""  function cssHsl(input) {
    var m = String(input || '').match(/rgba?\(([^)]+)\)/);
    if (!m) return { h: 190, s: 0.55, l: 0.6 };
    var p = m[1].split(',').map(function (v) { return parseFloat(v); });
    var r = p[0] / 255, g = p[1] / 255, b = p[2] / 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h = 0, s = 0, l = (max + min) / 2;
    if (max !== min) {
      var d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      if (max === r) h = ((g - b) / d) % 6;
      else if (max === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h = (h * 60 + 360) % 360;
    }
    return { h: h, s: s, l: l };
  }

  function hslStr(h, s, l) {
    return 'hsl(' + Math.round((h + 360) % 360) + ', ' + Math.round(s * 100) + '%, ' + Math.round(l * 100) + '%)';
  }

  function lyricPalette() {
    var cs = getComputedStyle(document.body);
    var base = cssHsl(cs.getPropertyValue('--accent'));
    var h = base.h;
    var s = Math.max(0.35, Math.min(0.85, base.s));

    return [
      hslStr(h, s * 0.18, 0.96),
      hslStr(h, s * 0.85, 0.74),
      hslStr(h + 18, s * 0.72, 0.66),
      hslStr(h - 18, s * 0.72, 0.70),
      hslStr(h, s * 0.45, 0.86)
    ];
  }

  function aiWordColor(text) {
    var t = S.aiTheme;
    if (!t || !t.wordColors) return '';
    for (var i = 0; i < t.wordColors.length; i++) {
      var w = t.wordColors[i];
      if (w && w.word && w.color && text.indexOf(w.word) >= 0) return w.color;
    }
    return '';
  }

  function lyricWordColor(text, i, pal) {
    var c = aiWordColor(text);
    if (c) return c;
    return pal[i % pal.length];
  }"""

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if old_pal in t:
        t = t.replace(old_pal, new_pal)
    elif "function cssHsl" not in t:
        print("palette anchor miss", d)

    t = t.replace("      var __pal = lyricPalette();\n      elWord.style.color = __pal[i % __pal.length];",
                  "      var __pal = lyricPalette();\n      elWord.style.color = lyricWordColor(unit, i, __pal);")

    t = t.replace("      var __pal2 = lyricPalette();\n      seg.style.color = __pal2[i % __pal2.length];",
                  "      var __pal2 = lyricPalette();\n      seg.style.color = lyricWordColor(part, i, __pal2);")

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=60", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
