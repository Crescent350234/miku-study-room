import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

block = r'''
  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];

  function applyLyricTheme(id) {
    document.body.classList.remove('theme-flow', 'theme-ink', 'theme-neon', 'theme-soft');
    document.body.classList.add('theme-' + id);
    try { localStorage.setItem('lyricTheme', id); } catch (e) {}
    S.lyricTheme = id;
  }

  function cycleLyricTheme() {
    var cur = S.lyricTheme || 'flow';
    var idx = 0;
    for (var i = 0; i < LYRIC_THEMES.length; i++) if (LYRIC_THEMES[i].id === cur) idx = i;
    var next = LYRIC_THEMES[(idx + 1) % LYRIC_THEMES.length];
    applyLyricTheme(next.id);
    toast('歌词主题 · ' + next.name);
  }

  var LYRIC_FONTS = [
    { id: 'sans', name: '黑体' },
    { id: 'serif', name: '宋体' },
    { id: 'kai', name: '楷体' },
    { id: 'light', name: '细体' }
  ];

  function applyLyricFont(id) {
    document.body.classList.remove('font-sans', 'font-serif', 'font-kai', 'font-light');
    document.body.classList.add('font-' + id);
    try { localStorage.setItem('lyricFont', id); } catch (e) {}
    S.lyricFont = id;
  }

  function cycleLyricFont() {
    var cur = S.lyricFont || 'sans';
    var idx = 0;
    for (var i = 0; i < LYRIC_FONTS.length; i++) if (LYRIC_FONTS[i].id === cur) idx = i;
    var next = LYRIC_FONTS[(idx + 1) % LYRIC_FONTS.length];
    applyLyricFont(next.id);
    toast('歌词字体 · ' + next.name);
  }

  var paletteCache = {};

  function rgbHue(r, g, b) {
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    if (max === min) return 0;
    var d = max - min, h;
    if (max === r) h = ((g - b) / d) % 6;
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    return (h * 60 + 360) % 360;
  }

  function setCoverPalette(p) {
    S.paletteHue = p.h1;
    document.body.style.setProperty('--accent', 'hsl(' + p.h2 + ' 72% 62%)');
    document.body.style.setProperty('--pink', 'hsl(' + ((p.h2 + 320) % 360) + ' 62% 64%)');
    document.body.style.setProperty('--theme-bg', 'hsl(' + p.h1 + ' 30% 10%)');
    document.body.style.setProperty('--theme-primary', 'hsl(' + p.h1 + ' 28% 94%)');
  }

  function applyCoverPalette(url) {
    if (!url) return;
    if (paletteCache[url]) { setCoverPalette(paletteCache[url]); return; }

    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      try {
        var size = 32;
        var c = document.createElement('canvas');
        c.width = size; c.height = size;
        var g = c.getContext('2d');
        g.drawImage(img, 0, 0, size, size);
        var data = g.getImageData(0, 0, size, size).data;
        var buckets = {};

        for (var i = 0; i < data.length; i += 4) {
          var r = data[i], gg = data[i + 1], b = data[i + 2], a = data[i + 3];
          if (a < 200) continue;
          var max = Math.max(r, gg, b), min = Math.min(r, gg, b);
          var sat = (max - min) / 255;
          if (sat < 0.12 || max < 40) continue;
          var key = Math.round(rgbHue(r, gg, b) / 15) * 15 % 360;
          buckets[key] = (buckets[key] || 0) + sat;
        }

        var keys = Object.keys(buckets).sort(function (a, b) { return buckets[b] - buckets[a]; });
        if (!keys.length) return;

        var h1 = +keys[0], h2 = +keys[0];
        for (var k = 1; k < keys.length; k++) {
          if (Math.abs(+keys[k] - h1) > 40) { h2 = +keys[k]; break; }
        }

        var p = { h1: h1, h2: h2 };
        paletteCache[url] = p;
        setCoverPalette(p);
      } catch (e) {}
    };
    img.src = url;
  }

  var LYRIC_KEYWORDS = ['雨', '夜', '梦', '光', '风', '海', '天空', '星', '月', '花', '夏', '冬',
    '心', '爱', '时间', '远方', '青春', '回忆', '世界', '孤单', '温柔', '离别', '永远',
    '沉默', '城市', '街', '黄昏', '清晨', '眼泪', '微笑', '呼吸', '拥抱', '失眠'];

  function colorizeLyric(text) {
    var base = (S.paletteHue != null ? S.paletteHue : 180);
    var parts = String(text).split(new RegExp('(' + LYRIC_KEYWORDS.join('|') + ')', 'g'));

    return parts.map(function (part) {
      var idx = LYRIC_KEYWORDS.indexOf(part);
      if (idx < 0) return esc(part);
      var hue = (base + 30 + idx * 41) % 360;
      return '<span class="kw" style="color:hsl(' + hue + ' 78% 72%)">' + esc(part) + '</span>';
    }).join('');
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if "function applyLyricTheme" not in t:
        if "  function start() {" in t:
            t = t.replace("  function start() {", block + "  function start() {", 1)
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            print("inserted", p)
        else:
            print("start anchor miss", p)
    else:
        print("already", p)
