import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildStackLine(idx) {
    S.charSpans = [];
    S.scatterWords = [];
    S.tiltSegs = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    main.innerHTML = '';

    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';
    var dir = (idx % 2 === 0) ? -1 : 1;

    var wrap = document.createElement('div');
    wrap.className = 'stack-v';

    function addPair(i, cls, bottomVh, xPx) {
      if (i < 0 || i >= S.lrc.length) return;
      var line = S.lrc[i];
      if (!line || !line.text) return;

      var pair = document.createElement('div');
      pair.className = 'stack-pair ' + cls;
      pair.style.bottom = bottomVh + 'vh';
      pair.style.transform = 'translateX(calc(-50% + ' + xPx + 'px))';

      var inner = document.createElement('div');
      inner.className = 'stack-inner';

      var parts = splitLyricSegments(line.text, 2);
      if (!parts.length) parts = [line.text];

      parts.forEach(function (part) {
        var col = document.createElement('div');
        col.className = 'stack-col';
        col.textContent = part;
        if (cls === 'current') {
          col.style.color = accent;
          col.style.textShadow = '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(8 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.45)';
        }
        inner.appendChild(col);
      });

      if (line.sub) {
        var subs = splitLyricSegments(line.sub, 2);
        subs.forEach(function (sp) {
          var sc = document.createElement('div');
          sc.className = 'stack-col stack-sub';
          sc.textContent = sp;
          inner.appendChild(sc);
        });
      }

      pair.appendChild(inner);
      wrap.appendChild(pair);
    }

    addPair(idx - 1, 'leaving', 38, dir * 70);
    addPair(idx, 'current', 38, dir * 70);
    addPair(idx + 1, 'next', 14, -dir * 260);

    main.appendChild(wrap);
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildStackLine(idx) {")
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
        if "云阶 v14" not in ct:
            ct += '''

/* 云阶 v14：两行左右交替，当前居中高光，旧句上飘淡出 */
body.theme-stack .stack-v {
  position: relative !important;
  display: block !important;
  height: 72vh !important;
  width: 100% !important;
}

body.theme-stack .stack-pair {
  position: absolute;
  left: 50%;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(12 * var(--s));
  opacity: 0.4;
  transform-origin: center bottom;
}

body.theme-stack .stack-pair.current {
  opacity: 1;
  z-index: 3;
}

body.theme-stack .stack-pair.next {
  opacity: 0.38;
  z-index: 1;
}

body.theme-stack .stack-pair.leaving {
  opacity: 0.5;
  z-index: 2;
}

body.theme-stack .stack-inner {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(10 * var(--s));
}

body.theme-stack .stack-pair.current .stack-inner {
  animation: stackRise 0.7s cubic-bezier(0.22, 0.8, 0.2, 1) both;
}

body.theme-stack .stack-pair.next .stack-inner {
  animation: stackFadeIn 0.7s ease both;
}

body.theme-stack .stack-pair.leaving .stack-inner {
  animation: stackLeave 0.75s ease both;
}

@keyframes stackRise {
  from { opacity: 0.2; transform: translateY(36px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes stackFadeIn {
  from { opacity: 0; transform: translateY(22px); }
  to { opacity: 0.38; transform: translateY(0); }
}

@keyframes stackLeave {
  from { opacity: 0.5; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-64px); }
}

body.theme-stack .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(30 * var(--s)) !important;
  line-height: 1.05;
  letter-spacing: 0.09em;
  color: rgba(255, 255, 255, 0.86);
  max-height: 20vh;
}

body.theme-stack .stack-pair.current .stack-col {
  font-size: calc(48 * var(--s)) !important;
  font-weight: 700;
}

body.theme-stack .stack-col.stack-sub {
  font-size: calc(16 * var(--s)) !important;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.6) !important;
  max-height: 15vh;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=157", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
