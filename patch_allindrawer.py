import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '''      <div class="style-title">字体</div>
      <div class="chip-row" id="fontChips"></div>'''
html_new = html_anchor + '''
      <div class="style-title">背景</div>
      <div class="chip-row" id="bgChips"></div>
      <div class="style-title">音乐来源</div>
      <div class="chip-row" id="sourceChips"></div>
      <div class="style-title">AI</div>
      <div class="chip-row"><button class="style-chip" id="aiOpen">打开 AI 设置</button></div>'''

js_add = r'''
  function renderSceneChips() {
    if (el.bgChips) {
      el.bgChips.innerHTML = '';
      for (var i = 0; i < BACKGROUNDS.length; i++) {
        (function (idx) {
          var b = document.createElement('button');
          b.className = 'style-chip' + (S.bgIndex === idx ? ' on' : '');
          b.textContent = '场景 ' + (idx + 1);
          b.addEventListener('click', function () {
            applyBg(idx);
            renderSceneChips();
            toast('背景 · 场景 ' + (idx + 1));
          });
          el.bgChips.appendChild(b);
        })(i);
      }
    }

    if (el.sourceChips) {
      el.sourceChips.innerHTML = '';
      var modes = [
        { id: 'mirror', name: '跟随网易云' },
        { id: 'local', name: '内置播放' }
      ];
      modes.forEach(function (m) {
        var b = document.createElement('button');
        b.className = 'style-chip' + (S.mode === m.id ? ' on' : '');
        b.textContent = m.name;
        b.addEventListener('click', function () {
          setMode(m.id, true);
          renderSceneChips();
          toast('音乐来源 · ' + m.name);
        });
        el.sourceChips.appendChild(b);
      });
    }
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="bgChips"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function renderSceneChips" not in t:
            t = t.replace("  function closePickers() {", js_add + "\n  function closePickers() {", 1)
        if "bgChips: $('bgChips')," not in t:
            t = t.replace("    fontChips: $('fontChips'),", "    fontChips: $('fontChips'),\n    bgChips: $('bgChips'),\n    sourceChips: $('sourceChips'),\n    aiOpen: $('aiOpen'),")
        if "renderSceneChips();" not in t:
            t = t.replace("    renderStyleChips();\n    renderPickers();", "    renderStyleChips();\n    renderSceneChips();\n    renderPickers();")
        if "el.aiOpen.addEventListener" not in t:
            t = t.replace("    document.addEventListener('click', closePickers);", "    document.addEventListener('click', closePickers);\n    if (el.aiOpen) el.aiOpen.addEventListener('click', function (e) { e.stopPropagation(); fetch(BRIDGE + 'ai.open', { cache: 'no-store' }).catch(function () {}); });")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".hud-right" not in ct.split("/* 全部收进抽屉 */")[-1]:
            ct += '''

/* 全部收进抽屉：隐藏右上角胶囊 */
.hud-right { display: none !important; }

/* 抽屉内容多时可滚动 */
.drawer { overflow-y: auto; }
.drawer .playlist { max-height: 30vh; }
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=54", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
