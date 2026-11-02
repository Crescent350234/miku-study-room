import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '      <button class="chip" id="bgBtn" title="切换背景">'
html_new = '''      <button class="chip" id="fontBtn" title="切换歌词字体">
        <span>字体</span>
      </button>
''' + html_anchor

js_funcs = r'''
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
'''

css_add = '''

/* ---------------- 封面取色 + 逐词着色 + 字体切换 ---------------- */
.kw { transition: color 0.4s ease; }

.line:not(.active) .kw {
  color: inherit !important;
  opacity: 0.9;
}

body.font-serif .line,
body.font-serif .line .main {
  font-family: "SimSun", "Songti SC", "STSong", serif;
}

body.font-kai .line,
body.font-kai .line .main {
  font-family: "KaiTi", "STKaiti", "Kaiti SC", serif;
}

body.font-light .line,
body.font-light .line .main {
  font-family: "DengXian Light", "Microsoft YaHei UI Light", "Segoe UI Light", sans-serif;
  font-weight: 300;
  letter-spacing: 0.14em;
}

body.font-sans .line,
body.font-sans .line .main {
  font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
}
'''

js_render_old = '''      div.innerHTML = '<span class="main">' + esc(line.text) + '</span>' +'''
js_render_new = '''      div.innerHTML = '<span class="main">' + colorizeLyric(line.text) + '</span>' +'''

poll_old = '''          if (d.pic) el.cover.src = d.pic;'''
poll_new = '''          if (d.pic) { el.cover.src = d.pic; applyCoverPalette(d.pic); }'''

select_old = '''      if (song.pic) {
        el.cover.src = song.pic;
      }'''
select_new = '''      if (song.pic) {
        el.cover.src = song.pic;
        applyCoverPalette(song.pic);
      }'''

for d in dirs:
    h = os.path.join(d, "index.html")
    j = os.path.join(d, "js", "app.js")
    c = os.path.join(d, "css", "style.css")

    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="fontBtn"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function colorizeLyric" not in t:
            t = t.replace("  function init() {", js_funcs + "\n  function init() {", 1)
        if js_render_old in t:
            t = t.replace(js_render_old, js_render_new)
        if poll_old in t:
            t = t.replace(poll_old, poll_new)
        if select_old in t:
            t = t.replace(select_old, select_new)
        if "fontBtn: $('fontBtn')," not in t:
            t = t.replace("    themeBtn: $('themeBtn'),", "    themeBtn: $('themeBtn'),\n    fontBtn: $('fontBtn'),")
        if "el.fontBtn.addEventListener" not in t:
            t = t.replace("el.themeBtn.addEventListener('click', cycleLyricTheme);",
                          "el.themeBtn.addEventListener('click', cycleLyricTheme);\n    el.fontBtn.addEventListener('click', cycleLyricFont);")
        if "applyLyricFont(savedFont" not in t:
            t = t.replace("    applyLyricTheme(savedTheme);",
                          "    applyLyricTheme(savedTheme);\n    var savedFont = 'sans';\n    try { savedFont = localStorage.getItem('lyricFont') || 'sans'; } catch (e) {}\n    applyLyricFont(savedFont);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "逐词着色" not in ct:
            ct += css_add
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
