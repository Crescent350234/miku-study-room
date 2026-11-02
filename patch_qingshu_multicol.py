import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildQingshuLine(idx) {
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    main.innerHTML = '';

    var parts = splitLyricSegments(text, 3);
    if (!parts.length) parts = [text];

    var wrap = document.createElement('div');
    wrap.className = 'qs-cols';

    parts.forEach(function (part) {
      var col = document.createElement('div');
      col.className = 'qs-col';

      var fit = Math.min(1, 14 / Math.max(1, Array.from(part).length));
      col.style.setProperty('font-size', 'calc(' + (42 * fit).toFixed(1) + ' * var(--s))', 'important');

      Array.from(part).forEach(function (ch, ci) {
        var sp = document.createElement('span');
        sp.className = 'qs-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        sp.style.animationDelay = (ci * 0.04).toFixed(2) + 's';
        col.appendChild(sp);
      });

      wrap.appendChild(col);
    });

    if (line.sub) {
      var subCol = document.createElement('div');
      subCol.className = 'qs-col qs-sub-col';
      Array.from(line.sub).forEach(function (ch) {
        var sp = document.createElement('span');
        sp.className = 'qs-sub-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        subCol.appendChild(sp);
      });
      wrap.appendChild(subCol);
    }

    main.appendChild(wrap);
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildQingshuLine(idx) {")
    nxt = t.find("\n  function ", start + 10)
    if start < 0 or nxt < 0:
        print("anchor miss", d)
        continue

    t = t[:start] + new_fn + t[nxt + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书 v7：多列分栏" not in ct:
            ct += '''

/* 青书 v7：多列竖排，列间青色细线 */
body.theme-qingshu .qs-cols {
  display: flex;
  flex-direction: row-reverse;
  align-items: center;
  justify-content: center;
  animation: qsDrift 20s ease-in-out infinite alternate;
}

body.theme-qingshu .qs-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  white-space: nowrap;
  padding: 0 calc(26 * var(--s));
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: calc(42 * var(--s));
}

body.theme-qingshu .qs-col + .qs-col {
  border-right: 1px solid rgba(140, 220, 215, 0.28);
}

body.theme-qingshu .qs-char {
  display: inline-block;
  white-space: pre;
  color: #cfece6;
  font-size: 1em;
  line-height: 1.08;
  letter-spacing: 0.12em;
  opacity: 0;
  filter: blur(5px);
  transform: translateY(6px);
  text-shadow: 0 0 calc(16 * var(--s)) rgba(150, 225, 220, 0.22);
  animation: qsIn 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

body.theme-qingshu .qs-sub-col {
  font-size: calc(19 * var(--s)) !important;
  opacity: 0.62;
}

body.theme-qingshu .qs-sub-char {
  display: inline-block;
  white-space: pre;
  color: rgba(160, 210, 205, 0.8);
  font-size: 1em;
  line-height: 1.12;
  letter-spacing: 0.08em;
}

@keyframes qsDrift {
  from { transform: translateX(-3vw); }
  to { transform: translateX(3vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=172", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
