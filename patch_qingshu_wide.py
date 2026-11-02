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

    main.innerHTML = '';

    var scroll = document.createElement('div');
    scroll.className = 'qs-scroll';

    function addColumn(li, isCurrent) {
      var line = S.lrc[li];
      if (!line || !line.text) return;

      var col = document.createElement('div');
      col.className = 'qs-text' + (isCurrent ? ' qs-current' : '');

      Array.from(line.text).forEach(function (ch, ci) {
        var sp = document.createElement('span');
        sp.className = 'qs-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        if (isCurrent) sp.style.animationDelay = (ci * 0.045).toFixed(2) + 's';
        col.appendChild(sp);
      });

      scroll.appendChild(col);

      if (isCurrent && line.sub) {
        var subCol = document.createElement('div');
        subCol.className = 'qs-text qs-sub-text';
        Array.from(line.sub).forEach(function (ch) {
          var sp = document.createElement('span');
          sp.className = 'qs-sub-char';
          sp.textContent = ch === ' ' ? '\u00a0' : ch;
          subCol.appendChild(sp);
        });
        scroll.appendChild(subCol);
      }
    }

    if (idx > 0) addColumn(idx - 1, false);
    addColumn(idx, true);
    if (idx + 1 < S.lrc.length) addColumn(idx + 1, false);

    main.appendChild(scroll);
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
        if "青书 v4：铺开卷轴" not in ct:
            ct += '''

/* 青书 v4：横向铺开的卷轴 */
body.theme-qingshu .qs-scroll {
  min-width: 42vw;
  justify-content: center;
  gap: calc(34 * var(--s));
  padding: calc(34 * var(--s)) calc(80 * var(--s));
  animation: qsUnroll 0.9s cubic-bezier(0.22, 0.8, 0.2, 1) both;
}

@keyframes qsUnroll {
  from { opacity: 0; transform: scaleX(0.82); }
  to { opacity: 1; transform: scaleX(1); }
}

body.theme-qingshu .qs-scroll::before,
body.theme-qingshu .qs-scroll::after {
  width: calc(22 * var(--s));
  top: calc(-16 * var(--s));
  bottom: calc(-16 * var(--s));
  background: linear-gradient(90deg, #0e1712, #4a6b52 35%, #2a4033 65%, #0b120e);
}

body.theme-qingshu .qs-scroll::before { left: calc(-14 * var(--s)); }
body.theme-qingshu .qs-scroll::after { right: calc(-14 * var(--s)); }

body.theme-qingshu .qs-text:not(.qs-current) .qs-char {
  color: rgba(190, 215, 180, 0.34);
}

body.theme-qingshu .qs-current .qs-char {
  color: #f0f5dc;
}

body.theme-qingshu .qs-text {
  flex: 0 0 auto;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=169", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
