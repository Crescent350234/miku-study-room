import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '''      <button class="chip" id="fontBtn" title="切换歌词字体">
        <span>字体</span>
      </button>'''
html_new = html_anchor + '''
      <div class="picker" id="modePicker"></div>
      <div class="picker" id="fontPicker"></div>'''

js = r'''
  function closePickers() {
    if (el.modePicker) el.modePicker.classList.remove('open');
    if (el.fontPicker) el.fontPicker.classList.remove('open');
  }

  function renderPickers() {
    function fill(host, items, current) {
      if (!host) return;
      host.innerHTML = '';
      items.forEach(function (it) {
        var b = document.createElement('button');
        b.className = 'picker-item' + (current === it.id ? ' on' : '');
        b.textContent = it.name;
        b.addEventListener('click', function (e) {
          e.stopPropagation();
          if (host === el.modePicker) {
            applyLyricTheme(it.id);
            toast('歌词特效 · ' + it.name);
          } else {
            applyLyricFont(it.id);
            toast('字体 · ' + it.name);
          }
          renderStyleChips();
          renderPickers();
          closePickers();
        });
        host.appendChild(b);
      });
    }

    fill(el.modePicker, LYRIC_THEMES, S.lyricTheme);
    fill(el.fontPicker, LYRIC_FONTS, S.lyricFont);
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="modePicker"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function renderPickers" not in t:
            t = t.replace("  function buildActiveChars(idx) {", js + "\n  function buildActiveChars(idx) {", 1)
        if "modePicker: $('modePicker')," not in t:
            t = t.replace("    modeChips: $('modeChips'),", "    modeChips: $('modeChips'),\n    modePicker: $('modePicker'),\n    fontPicker: $('fontPicker'),")
        if "el.themeBtn.addEventListener('click', function (e) {" not in t:
            t = t.replace("if (el.themeBtn) el.themeBtn.addEventListener('click', cycleLyricTheme);",
                          "if (el.themeBtn) el.themeBtn.addEventListener('click', function (e) { e.stopPropagation(); renderPickers(); closePickers(); el.modePicker.classList.add('open'); });")
            t = t.replace("if (el.fontBtn) el.fontBtn.addEventListener('click', cycleLyricFont);",
                          "if (el.fontBtn) el.fontBtn.addEventListener('click', function (e) { e.stopPropagation(); renderPickers(); closePickers(); el.fontPicker.classList.add('open'); });")
        if "document.addEventListener('click', closePickers)" not in t:
            t = t.replace("    renderStyleChips();", "    renderStyleChips();\n    renderPickers();\n    document.addEventListener('click', closePickers);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".picker {" not in ct:
            ct += '''

/* 主题/字体 下拉选择 */
.picker {
  position: fixed;
  top: calc(64 * var(--s));
  right: calc(24 * var(--s));
  z-index: 20;
  display: none;
  flex-direction: column;
  gap: calc(2 * var(--s));
  padding: calc(8 * var(--s));
  min-width: calc(150 * var(--s));
  background: rgba(8, 14, 16, 0.92);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: calc(14 * var(--s));
  box-shadow: 0 calc(20 * var(--s)) calc(50 * var(--s)) rgba(0, 0, 0, 0.5);
}

.picker.open { display: flex; }

.picker-item {
  border: 0;
  background: transparent;
  color: var(--text);
  text-align: left;
  padding: calc(7 * var(--s)) calc(12 * var(--s));
  border-radius: calc(8 * var(--s));
  font-size: calc(13 * var(--s));
  cursor: pointer;
}

.picker-item:hover { background: rgba(255, 255, 255, 0.08); }

.picker-item.on {
  background: var(--accent, #3cc5bb);
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
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=52", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
