import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '    <div class="scroll-pager">'
html_new = '''    <div class="lyric-offset">
      <button id="offMinus" title="歌词提前 0.5 秒">−0.5s</button>
      <span id="offVal">0.0s</span>
      <button id="offPlus" title="歌词再提前 0.5 秒">+0.5s</button>
    </div>
    <div class="scroll-pager">'''

js_set = '''
  function setLyricOffset(v) {
    v = Math.max(-5, Math.min(5, Math.round(v * 10) / 10));
    S.lyricOffset = v;
    try { localStorage.setItem('lyricOffset', String(v)); } catch (e) {}
    if (el.offVal) el.offVal.textContent = (v > 0 ? '+' : '') + v.toFixed(1) + 's';
    S.lrcIndex = -999;
    updateLyrics(S.position);
  }
'''

js_update_old = '''  function updateLyrics(time) {
    if (!S.lrc.length) return;
    var idx = -1;
    for (var i = 0; i < S.lrc.length; i++) {
      if (S.lrc[i].t <= time + 0.15) idx = i; else break;
    }'''

js_update_new = '''  function updateLyrics(time) {
    if (!S.lrc.length) return;
    var t = time + (S.lyricOffset || 0);
    var idx = -1;
    for (var i = 0; i < S.lrc.length; i++) {
      if (S.lrc[i].t <= t + 0.15) idx = i; else break;
    }'''

css_add = '''

/* ---------------- 歌词偏移校准 ---------------- */
.lyric-offset {
  display: flex;
  align-items: center;
  gap: calc(8 * var(--s));
  padding: 0 calc(14 * var(--s)) calc(10 * var(--s));
  font-size: calc(12 * var(--s));
  color: var(--muted);
}

.lyric-offset button {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: var(--text);
  border-radius: 999px;
  padding: calc(4 * var(--s)) calc(10 * var(--s));
  font-size: calc(12 * var(--s));
  cursor: pointer;
}

.lyric-offset button:hover {
  background: rgba(255, 255, 255, 0.12);
}

.lyric-offset span {
  min-width: calc(46 * var(--s));
  text-align: center;
  font-variant-numeric: tabular-nums;
}
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    j = os.path.join(d, "js", "app.js")
    c = os.path.join(d, "css", "style.css")

    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="offMinus"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function setLyricOffset" not in t:
            t = t.replace("  function updateLyrics(time) {", js_set + "\n  function updateLyrics(time) {", 1)
        if js_update_old in t:
            t = t.replace(js_update_old, js_update_new)
        if "offMinus: $('offMinus')," not in t:
            t = t.replace("    themeBtn: $('themeBtn'),", "    themeBtn: $('themeBtn'),\n    offMinus: $('offMinus'),\n    offPlus: $('offPlus'),\n    offVal: $('offVal'),")
        if "el.offMinus.addEventListener" not in t:
            t = t.replace("    if (el.fontBtn) el.fontBtn.addEventListener('click', cycleLyricFont);",
                          "    if (el.fontBtn) el.fontBtn.addEventListener('click', cycleLyricFont);\n    if (el.offMinus) el.offMinus.addEventListener('click', function () { setLyricOffset((S.lyricOffset || 0) - 0.5); });\n    if (el.offPlus) el.offPlus.addEventListener('click', function () { setLyricOffset((S.lyricOffset || 0) + 0.5); });")
        if "setLyricOffset(savedOff)" not in t:
            t = t.replace("    applyLyricFont(savedFont);",
                          "    applyLyricFont(savedFont);\n    var savedOff = 0;\n    try { savedOff = parseFloat(localStorage.getItem('lyricOffset') || '0') || 0; } catch (e) {}\n    setLyricOffset(savedOff);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "歌词偏移校准" not in ct:
            ct += css_add
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
