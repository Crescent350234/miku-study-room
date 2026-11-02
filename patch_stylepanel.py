import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '    <div class="scroll-pager">'
html_new = '''    <div class="style-box">
      <div class="style-title">歌词特效</div>
      <div class="chip-row" id="modeChips"></div>
      <div class="style-title">字体</div>
      <div class="chip-row" id="fontChips"></div>
    </div>
    <div class="scroll-pager">'''

js = r'''
  function renderStyleChips() {
    if (el.modeChips) {
      el.modeChips.innerHTML = '';
      LYRIC_THEMES.forEach(function (t) {
        var b = document.createElement('button');
        b.className = 'style-chip' + (S.lyricTheme === t.id ? ' on' : '');
        b.textContent = t.name;
        b.addEventListener('click', function () {
          applyLyricTheme(t.id);
          renderStyleChips();
          toast('歌词特效 · ' + t.name);
        });
        el.modeChips.appendChild(b);
      });
    }

    if (el.fontChips) {
      el.fontChips.innerHTML = '';
      LYRIC_FONTS.forEach(function (f) {
        var b = document.createElement('button');
        b.className = 'style-chip' + (S.lyricFont === f.id ? ' on' : '');
        b.textContent = f.name;
        b.addEventListener('click', function () {
          applyLyricFont(f.id);
          renderStyleChips();
          toast('字体 · ' + f.name);
        });
        el.fontChips.appendChild(b);
      });
    }
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="modeChips"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function renderStyleChips" not in t:
            t = t.replace("  function buildActiveChars(idx) {", js + "\n  function buildActiveChars(idx) {", 1)
        if "modeChips: $('modeChips')," not in t:
            t = t.replace("    offVal: $('offVal'),", "    offVal: $('offVal'),\n    modeChips: $('modeChips'),\n    fontChips: $('fontChips'),")
        if "renderStyleChips();" not in t:
            t = t.replace("    loadAiSettings();", "    loadAiSettings();\n    renderStyleChips();")
        # rebuild current line when mode changes
        if "S.lrcIndex = -999;\n    updateLyrics(S.position);\n    toast('歌词主题" not in t:
            t = t.replace("    toast('歌词主题 · ' + next.name);", "    S.lrcIndex = -999;\n    updateLyrics(S.position);\n    toast('歌词主题 · ' + next.name);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".style-box" not in ct:
            ct += '''

/* 歌词特效 / 字体选择面板 */
.style-box {
  padding: 0 calc(14 * var(--s)) calc(12 * var(--s));
}

.style-title {
  color: var(--muted);
  font-size: calc(12 * var(--s));
  letter-spacing: 0.08em;
  margin: calc(8 * var(--s)) 0 calc(6 * var(--s));
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: calc(6 * var(--s));
}

.style-chip {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  border-radius: 999px;
  padding: calc(5 * var(--s)) calc(12 * var(--s));
  font-size: calc(12 * var(--s));
  cursor: pointer;
}

.style-chip.on {
  background: var(--accent, #3cc5bb);
  border-color: transparent;
  color: #08110f;
  font-weight: 600;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=50", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
