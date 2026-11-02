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

    var line = S.lrc[idx];
    var text = line.text || '';

    var parts = splitLyricSegments(text, 3);
    if (!parts.length) parts = [text];

    var subParts = [];
    if (line.sub) subParts = splitLyricSegments(line.sub, parts.length);

    var key = '';
    if (S.aiTheme && S.aiTheme.lineKeywords) {
      for (var li = 0; li < S.aiTheme.lineKeywords.length; li++) {
        var lk = S.aiTheme.lineKeywords[li];
        if (lk && lk.line === text && lk.keyword && text.indexOf(lk.keyword) >= 0 && keyBoundaryOk(text, lk.keyword)) {
          key = lk.keyword;
          break;
        }
      }
    }
    if (!key && S.aiTheme && S.aiTheme.emphasis) {
      S.aiTheme.emphasis.forEach(function (w) {
        if (w && text.indexOf(w) >= 0 && w.length > key.length && keyBoundaryOk(text, w)) key = w;
      });
    }

    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';
    var keyColor = '';
    if (S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word === key && wc.color) keyColor = wc.color;
      });
    }

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'stack-v';

    parts.forEach(function (part, i) {
      var pair = document.createElement('div');
      pair.className = 'stack-pair';
      pair.style.transform = 'translateX(' + ((i % 2 === 0 ? -1 : 1) * 44) + 'px)';

      var col = document.createElement('div');
      col.className = 'stack-col';
      col.textContent = part;

      if (key && part.indexOf(key) >= 0) {
        col.classList.add('key');
        col.style.color = keyColor || accent;
        col.style.textShadow = '0 0 calc(26 * var(--s)) ' + (keyColor || accent) + ', 0 calc(8 * var(--s)) calc(28 * var(--s)) rgba(0,0,0,0.45)';
      }
      pair.appendChild(col);

      if (subParts[i]) {
        var sc = document.createElement('div');
        sc.className = 'stack-col sub';
        sc.textContent = subParts[i];
        pair.appendChild(sc);
      }

      wrap.appendChild(pair);
    });

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
        if "云阶 v8：原文翻译同组" not in ct:
            ct += '''

/* 云阶 v8：原文+翻译同一组，左右交替向上 */
body.theme-stack .stack-v {
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  justify-content: flex-start;
  gap: calc(10 * var(--s));
  height: 54vh;
  width: min(92vw, calc(1400 * var(--s)));
  margin: 0 auto;
  padding-bottom: calc(20 * var(--s));
}

body.theme-stack .stack-pair {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(8 * var(--s));
  transition: transform 0.5s cubic-bezier(0.22, 0.8, 0.2, 1);
}

body.theme-stack .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(28 * var(--s)) !important;
  line-height: 1.05;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.88);
  max-height: 15vh;
}

body.theme-stack .stack-col.sub {
  font-size: calc(15 * var(--s)) !important;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.55) !important;
  max-height: 12vh;
}

body.theme-stack .stack-col.key {
  font-size: calc(38 * var(--s)) !important;
  font-weight: 700;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=150", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
