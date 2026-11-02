import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

fn = r'''
  function buildQingshuLine(idx) {
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var text = S.lrc[idx].text || '';
    main.innerHTML = '';

    var wrap = document.createElement('div');
    wrap.className = 'qs-line';

    Array.from(text).forEach(function (ch, i) {
      var sp = document.createElement('span');
      sp.className = 'qs-char';
      sp.textContent = ch === ' ' ? '\u00a0' : ch;
      sp.style.animationDelay = (i * 0.05).toFixed(2) + 's';
      wrap.appendChild(sp);
    });

    main.appendChild(wrap);
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    t = t.replace("{ id: 'hanabi', name: '花火' }", "{ id: 'qingshu', name: '青书' }")

    if "function buildQingshuLine" not in t:
        t = t.replace("  function buildLumiLine(idx) {", fn + "\n  function buildLumiLine(idx) {", 1)

    if "buildQingshuLine(idx)" not in t:
        t = t.replace("if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }",
                      "if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }\n    if (S.lyricTheme === 'qingshu') { buildQingshuLine(idx); return; }")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书 v1" not in ct:
            ct += '''

/* 青书：青墨书信，逐字落笔 */
body.theme-qingshu .line {
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
}

body.theme-qingshu .line .main {
  display: inline-block;
}

body.theme-qingshu .qs-line {
  display: inline-block;
  letter-spacing: 0.14em;
  line-height: 1.4;
}

body.theme-qingshu .qs-char {
  display: inline-block;
  white-space: pre;
  color: #a9e3ee;
  opacity: 0;
  filter: blur(6px);
  transform: translateY(7px);
  text-shadow: 0 0 calc(18 * var(--s)) rgba(120, 220, 235, 0.35);
  animation: qsIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

@keyframes qsIn {
  to {
    opacity: 1;
    filter: blur(0);
    transform: translateY(0);
  }
}

body.theme-qingshu .line.active .main::after {
  content: '';
  display: block;
  width: 58%;
  height: 1px;
  margin: calc(14 * var(--s)) auto 0;
  background: linear-gradient(90deg, transparent, rgba(150, 225, 240, 0.75), transparent);
  opacity: 0.6;
}

body.theme-qingshu .line .sub {
  color: rgba(130, 200, 215, 0.7) !important;
  letter-spacing: 0.12em;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=165", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
