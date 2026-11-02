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

    var from = Math.max(0, idx - 1);
    var to = Math.min(S.lrc.length - 1, idx + 1);
    if (to - from < 2) {
      from = Math.max(0, idx - 2);
      to = Math.min(S.lrc.length - 1, idx + 1);
    }

    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';

    var wrap = document.createElement('div');
    wrap.className = 'stack-v';

    for (var i = from; i <= to; i++) {
      var line = S.lrc[i];
      var text = line.text || '';
      if (!text) continue;

      var pair = document.createElement('div');
      pair.className = 'stack-pair' + (i === idx ? ' current' : '');
      var order = i - from;
      pair.style.transform = 'translateX(' + ((order % 2 === 0 ? -1 : 1) * 96) + 'px)';

      var parts = splitLyricSegments(text, 2);
      if (!parts.length) parts = [text];

      parts.forEach(function (part) {
        var col = document.createElement('div');
        col.className = 'stack-col';
        col.textContent = part;
        if (i === idx) {
          col.style.color = accent;
          col.style.textShadow = '0 0 calc(24 * var(--s)) ' + accent + ', 0 calc(6 * var(--s)) calc(24 * var(--s)) rgba(0,0,0,0.45)';
        }
        pair.appendChild(col);
      });

      if (line.sub) {
        var subs = splitLyricSegments(line.sub, 2);
        subs.forEach(function (sp) {
          var sc = document.createElement('div');
          sc.className = 'stack-col stack-sub';
          sc.textContent = sp;
          pair.appendChild(sc);
        });
      }

      wrap.appendChild(pair);
    }

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
        if "云阶 v10" not in ct:
            ct += '''

/* 云阶 v10：一句一组、左右交替上升，当前句高光 */
body.theme-stack .stack-v {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  justify-content: flex-start;
  gap: calc(16 * var(--s));
  height: 60vh;
  width: min(92vw, calc(1400 * var(--s)));
  margin: 0 auto;
  padding-bottom: calc(24 * var(--s));
}

body.theme-stack .stack-pair {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(10 * var(--s));
  transition: transform 0.6s cubic-bezier(0.22, 0.8, 0.2, 1), opacity 0.5s ease;
  opacity: 0.42;
}

body.theme-stack .stack-pair.current {
  opacity: 1;
}

body.theme-stack .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(28 * var(--s)) !important;
  line-height: 1.05;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.86);
  max-height: 13vh;
}

body.theme-stack .stack-col.stack-sub {
  font-size: calc(15 * var(--s)) !important;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.6) !important;
  max-height: 10vh;
}

body.theme-stack .line:not(.active) .main {
  opacity: 0 !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=153", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
