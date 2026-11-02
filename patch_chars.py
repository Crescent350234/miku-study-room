import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js_funcs = r'''
  function buildActiveChars(idx) {
    S.charSpans = [];
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var t0 = line.t;
    var t1 = S.lrc[idx + 1] ? S.lrc[idx + 1].t : t0 + Math.max(4, text.length * 0.35);
    var dur = Math.max(0.8, t1 - t0);
    var chars = Array.from(text);
    var per = dur / Math.max(1, chars.length);

    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#8ef';

    main.innerHTML = '';
    for (var i = 0; i < chars.length; i++) {
      var span = document.createElement('span');
      span.className = 'ch';
      span.textContent = chars[i];
      span.dataset.t0 = (t0 + i * per).toFixed(3);
      span.dataset.t1 = (t0 + (i + 1) * per).toFixed(3);
      main.appendChild(span);
      S.charSpans.push(span);
    }
  }

  function paintChars(pos) {
    if (!S.charSpans || !S.charSpans.length) return;
    var accent = S.charAccent || '#8ef';

    for (var i = 0; i < S.charSpans.length; i++) {
      var s = S.charSpans[i];
      var t0 = +s.dataset.t0;
      var t1 = +s.dataset.t1;
      var p = (pos - t0) / Math.max(0.05, t1 - t0);
      if (p < 0) p = 0;
      else if (p > 1) p = 1;

      s.style.opacity = (0.35 + 0.65 * p).toFixed(3);
      s.style.color = p >= 1 ? '#ffffff' : 'rgba(255,255,255,' + (0.35 + 0.55 * p).toFixed(3) + ')';
      s.style.textShadow = p > 0.02 ? '0 0 ' + (8 + 14 * p).toFixed(1) + 'px ' + accent : 'none';
    }
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "function paintChars" not in t:
        t = t.replace("  function updateLyrics(time) {", js_funcs + "  function updateLyrics(time) {", 1)

    if "buildActiveChars(idx);" not in t:
        t = t.replace("    centerActive();", "    centerActive();\n    buildActiveChars(idx);", 1)

    if "paintChars(S.position);" not in t:
        t = t.replace("    tickPomo(dt);", "    paintChars(S.position);\n\n    tickPomo(dt);", 1)

    old_fonts = """  var LYRIC_FONTS = [
    { id: 'sans', name: '黑体' },
    { id: 'serif', name: '宋体' },
    { id: 'kai', name: '楷体' },
    { id: 'light', name: '细体' }
  ];"""
    new_fonts = """  var LYRIC_FONTS = [
    { id: 'sans', name: '黑体' },
    { id: 'serif', name: '宋体' },
    { id: 'kai', name: '楷体' },
    { id: 'fangsong', name: '仿宋' },
    { id: 'dengxian', name: '等线' },
    { id: 'youyuan', name: '幼圆' },
    { id: 'mono', name: '等宽' },
    { id: 'lishu', name: '隶书' }
  ];"""
    if old_fonts in t:
        t = t.replace(old_fonts, new_fonts)

    t = t.replace("document.body.classList.remove('font-sans', 'font-serif', 'font-kai', 'font-light');",
                  "document.body.classList.remove('font-sans', 'font-serif', 'font-kai', 'font-light', 'font-fangsong', 'font-dengxian', 'font-youyuan', 'font-mono', 'font-lishu');")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".line .ch" not in ct:
            ct += '''

/* 逐字扫光 */
.line .ch {
  display: inline-block;
  white-space: pre;
  transition: none;
}

.line:not(.active) .ch {
  color: inherit !important;
  opacity: 1 !important;
  text-shadow: none !important;
}

/* 更多字体 */
body.font-fangsong .line, body.font-fangsong .line .main {
  font-family: "FangSong", "STFangsong", "SimSun", serif;
}

body.font-dengxian .line, body.font-dengxian .line .main {
  font-family: "DengXian", "Microsoft YaHei UI", sans-serif;
}

body.font-youyuan .line, body.font-youyuan .line .main {
  font-family: "YouYuan", "Microsoft YaHei UI", sans-serif;
}

body.font-mono .line, body.font-mono .line .main {
  font-family: "Sarasa Mono SC", "Cascadia Mono", "Consolas", "Microsoft YaHei UI", monospace;
}

body.font-lishu .line, body.font-lishu .line .main {
  font-family: "LiSu", "STLiti", "KaiTi", serif;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("js/app.js?v=38", "js/app.js?v=39")
        io.open(h, "w", encoding="utf-8", newline="").write(t)
