import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

# ---------- index.html: theme button ----------
html_old = '''      <button class="chip" id="bgBtn" title="切换背景">'''
html_new = '''      <button class="chip" id="themeBtn" title="切换歌词主题">
        <span>主题</span>
      </button>
      <button class="chip" id="bgBtn" title="切换背景">'''

# ---------- app.js: wrap main text ----------
js_render_old = '''      div.innerHTML = esc(line.text) + (line.sub ? '<span class="sub">' + esc(line.sub) + '</span>' : '');'''
js_render_new = '''      div.innerHTML = '<span class="main">' + esc(line.text) + '</span>' +
        (line.sub ? '<span class="sub">' + esc(line.sub) + '</span>' : '');'''

# theme engine, inserted before init()
js_theme = '''
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
'''

css_add = '''

/* ---------------- 歌词主题系统 ---------------- */
.line .main { display: inline; }

/* 流光：渐变扫光 */
body.theme-flow .line.active .main {
  background: linear-gradient(100deg,
    #ffffff 0%, #ffffff 32%,
    color-mix(in srgb, var(--accent) 80%, #fff 20%) 48%,
    #ffffff 64%, #ffffff 100%);
  background-size: 260% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: lyricSweep 7s linear infinite;
}

@keyframes lyricSweep {
  from { background-position: 130% 0; }
  to   { background-position: -130% 0; }
}

/* 墨韵：宋/楷体，纸墨感 */
body.theme-ink .line {
  font-family: "KaiTi", "STKaiti", "SimSun", "Songti SC", serif;
  letter-spacing: 0.08em;
}
body.theme-ink .line.active {
  font-size: calc(54 * var(--s));
  color: #f6efe2;
  text-shadow: 0 calc(6 * var(--s)) calc(28 * var(--s)) rgba(0, 0, 0, 0.75);
}
body.theme-ink .line.active .sub { color: rgba(246, 239, 226, 0.6); }

/* 霓虹：粗体 + 双色辉光 */
body.theme-neon .line {
  font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
  font-weight: 800;
}
body.theme-neon .line.active .main {
  color: #ffffff;
  text-shadow:
    0 0 calc(18 * var(--s)) color-mix(in srgb, var(--accent) 90%, transparent),
    0 0 calc(46 * var(--s)) color-mix(in srgb, var(--pink) 60%, transparent),
    0 calc(6 * var(--s)) calc(24 * var(--s)) rgba(0, 0, 0, 0.6);
}
body.theme-neon .line.active { font-size: calc(62 * var(--s)); }

/* 轻语：细体 + 大字距 */
body.theme-soft .line {
  font-family: "DengXian Light", "Microsoft YaHei UI Light", "Segoe UI Light", sans-serif;
  font-weight: 300;
  letter-spacing: 0.16em;
}
body.theme-soft .line.active {
  font-size: calc(50 * var(--s));
  color: rgba(255, 255, 255, 0.94);
  text-shadow: 0 calc(4 * var(--s)) calc(30 * var(--s)) rgba(0, 0, 0, 0.55);
}
body.theme-soft .line.active .sub { color: rgba(255, 255, 255, 0.55); }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    j = os.path.join(d, "js", "app.js")
    c = os.path.join(d, "css", "style.css")

    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="themeBtn"' not in t and html_old in t:
            t = t.replace(html_old, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if js_render_old in t:
            t = t.replace(js_render_old, js_render_new)
        if "LYRIC_THEMES" not in t:
            t = t.replace("  function init() {", js_theme + "\n  function init() {", 1)
        if "themeBtn" not in t:
            t = t.replace("    bgBtn: $('bgBtn'),", "    bgBtn: $('bgBtn'),\n    themeBtn: $('themeBtn'),")
        if "el.themeBtn.addEventListener" not in t:
            t = t.replace("    el.bgBtn.addEventListener('click', function () {",
                          "    el.themeBtn.addEventListener('click', cycleLyricTheme);\n\n    el.bgBtn.addEventListener('click', function () {", 1)
        if "applyLyricTheme(saved" not in t:
            t = t.replace("    updatePomo();", "    updatePomo();\n    var savedTheme = 'flow';\n    try { savedTheme = localStorage.getItem('lyricTheme') || 'flow'; } catch (e) {}\n    applyLyricTheme(savedTheme);", 1)
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "歌词主题系统" not in ct:
            ct += css_add
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
