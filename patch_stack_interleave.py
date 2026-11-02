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
    if (line.sub) {
      subParts = splitLyricSegments(line.sub, parts.length);
    }

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

    var seq = [];
    parts.forEach(function (part, i) {
      seq.push({ text: part, sub: false });
      if (subParts[i]) seq.push({ text: subParts[i], sub: true });
    });
    for (var si = parts.length; si < subParts.length; si++) {
      seq.push({ text: subParts[si], sub: true });
    }

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'stack-v';

    seq.forEach(function (item, j) {
      var col = document.createElement('div');
      col.className = 'stack-col' + (item.sub ? ' sub' : '');
      col.textContent = item.text;

      var dir = (j % 2 === 0) ? -1 : 1;
      col.style.transform = 'translate(' + (dir * 16) + 'px,' + (-j * 30) + 'px)';
      col.style.zIndex = String(200 - j);

      if (!item.sub && key && item.text.indexOf(key) >= 0) {
        col.classList.add('key');
        col.style.color = keyColor || accent;
        col.style.textShadow = '0 0 calc(26 * var(--s)) ' + (keyColor || accent) + ', 0 calc(8 * var(--s)) calc(28 * var(--s)) rgba(0,0,0,0.45)';
      }

      wrap.appendChild(col);
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
        if "云阶 v7：原文翻译交替" not in ct:
            ct += '''

/* 云阶 v7：原文与翻译交替、左右错开向上 */
body.theme-stack .stack-v {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: center;
  gap: calc(14 * var(--s));
  height: 50vh;
  width: min(92vw, calc(1400 * var(--s)));
  margin: 0 auto;
}

body.theme-stack .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(30 * var(--s)) !important;
  line-height: 1.08;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.85);
  max-height: 100%;
  transition: transform 0.5s cubic-bezier(0.22, 0.8, 0.2, 1), color 0.3s ease;
}

body.theme-stack .stack-col.sub {
  font-size: calc(17 * var(--s)) !important;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.52) !important;
  max-height: 30vh;
}

body.theme-stack .stack-col.key {
  font-size: calc(42 * var(--s)) !important;
  font-weight: 700;
  letter-spacing: 0.05em;
}

body.theme-stack .stack-group,
body.theme-stack .stack-v.sub-v {
  display: none !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=149", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
