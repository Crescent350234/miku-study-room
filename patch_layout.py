import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()

        # remove flow theme, add plain
        old_themes = """  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
        new_themes = """  var LYRIC_THEMES = [
    { id: 'plain', name: '简洁' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
        if old_themes in t:
            t = t.replace(old_themes, new_themes)

        # migrate saved flow -> plain
        t = t.replace("try { savedTheme = localStorage.getItem('lyricTheme') || 'flow'; } catch (e) {}",
                      "try { savedTheme = localStorage.getItem('lyricTheme') || 'plain'; } catch (e) {}")
        t = t.replace("if (savedTheme === 'flow') savedTheme = 'plain';", "")
        t = t.replace("    var savedTheme = 'flow';", "    var savedTheme = 'plain';")
        t = t.replace("    var savedTheme = 'scatter';", "    var savedTheme = 'plain';")

        # poll faster
        t = t.replace("setInterval(pollNetease, 2000);", "setInterval(pollNetease, 600);")

        # scatter: smaller random offsets so words don't overlap
        t = t.replace("var rot = (r1 - 0.5) * 36;", "var rot = (r1 - 0.5) * 22;")
        t = t.replace("var dx = (r2 - 0.5) * 70;", "var dx = (r2 - 0.5) * 22;")
        t = t.replace("var dy = (r3 - 0.5) * 46;", "var dy = (r3 - 0.5) * 14;")
        t = t.replace("var scale = 0.8 + r4 * 0.8;", "var scale = 0.92 + r4 * 0.3;")
        t = t.replace("elWord.style.fontSize = (0.72 + r1 * 0.75).toFixed(2) + 'em';",
                      "elWord.style.fontSize = (0.82 + r1 * 0.36).toFixed(2) + 'em';")

        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".theme-plain" not in ct:
            ct += '''

/* ---------------- 简洁（无光效，纯排版） ---------------- */
body.theme-plain .line {
  filter: none;
  opacity: 0.22;
  font-size: calc(30 * var(--s));
  transform: none;
  text-shadow: none;
}

body.theme-plain .line.near {
  opacity: 0.4;
  font-size: calc(36 * var(--s));
}

body.theme-plain .line.active {
  opacity: 1;
  font-size: calc(54 * var(--s));
  color: #ffffff;
  text-shadow: 0 calc(4 * var(--s)) calc(24 * var(--s)) rgba(0, 0, 0, 0.55);
}

body.theme-plain .line .sub {
  color: rgba(255, 255, 255, 0.55);
}

body.theme-plain .line .kw {
  color: inherit !important;
}

/* 给歌词更多呼吸空间，避免上下行贴住 */
.lyrics-viewport { height: 58vh; }

.line {
  line-height: 1.38;
  padding: calc(2 * var(--s)) 0;
}

.line .main {
  display: inline-block;
  max-width: 86vw;
  overflow-wrap: break-word;
}

/* 散字：加大间距，禁止负外边距叠字 */
.scatter-wrap {
  gap: calc(10 * var(--s)) calc(22 * var(--s));
  padding: calc(14 * var(--s)) calc(18 * var(--s));
}

.sc-word {
  margin: 0;
  line-height: 1.1;
}

/* 叠字：允许换行，限制宽度 */
.tilt-seg, .stack-seg {
  white-space: normal;
  max-width: 86vw;
  text-align: center;
  line-height: 1.32;
}

.stack-wrap, .tilt-wrap {
  gap: calc(10 * var(--s));
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("js/app.js?v=45", "js/app.js?v=46").replace("js/app.js?v=44", "js/app.js?v=46").replace("js/app.js?v=43", "js/app.js?v=46").replace("js/app.js?v=42", "js/app.js?v=46")
        io.open(h, "w", encoding="utf-8", newline="").write(t)
