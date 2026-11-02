import io, os

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

    var key = '';
    var keyColor = '';

    if (S.aiTheme && S.aiTheme.emphasis) {
      S.aiTheme.emphasis.forEach(function (w) {
        if (w && text.indexOf(w) >= 0 && w.length > key.length) key = w;
      });
    }
    if (!key && S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word && text.indexOf(wc.word) >= 0 && wc.word.length > key.length) key = wc.word;
      });
    }
    if (!key) {
      var chunks = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.length > 0; });
      key = chunks.sort(function (a, b) { return b.length - a.length; })[0] || text;
    }

    if (key.length >= text.length && text.length > 4) {
      key = text.slice(Math.max(0, text.length - 3));
    }

    var keyPos = text.indexOf(key);
    if (keyPos < 0) { key = text; keyPos = 0; }

    var before = text.slice(0, keyPos);
    var after = text.slice(keyPos + key.length);

    if (S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word === key && wc.color) keyColor = wc.color;
      });
    }

    var pal = lyricPalette();
    var s = Math.min(window.innerWidth * 0.000390625, window.innerHeight * 0.00069444) || 1;
    var base = 58 * s;
    var maxPx = window.innerWidth * 0.72 / Math.max(1, key.length);
    var bigEm = Math.min(2.3, Math.max(1.3, maxPx / base));

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'stack-line';

    function addText(part, cls, size, color, rotate) {
      if (!part) return;
      var sp = document.createElement('span');
      sp.className = cls;
      sp.textContent = part;
      sp.style.setProperty('font-size', size, 'important');
      if (color) sp.style.color = color;
      if (rotate) sp.style.transform = 'rotate(' + rotate + 'deg) skewX(-3deg)';
      wrap.appendChild(sp);
    }

    addText(before, 'stack-small', '0.55em', 'rgba(255,255,255,0.72)', -1.6);

    var keyEl = document.createElement('span');
    keyEl.className = 'stack-key';
    keyEl.textContent = key;
    keyEl.style.setProperty('font-size', bigEm.toFixed(2) + 'em', 'important');
    keyEl.style.color = keyColor || pal[1];
    keyEl.style.transform = 'rotate(-2.2deg) skewX(-6deg)';
    keyEl.style.textShadow = '0 0 calc(30 * var(--s)) ' + (keyColor || pal[1]) + ', 0 calc(8 * var(--s)) calc(30 * var(--s)) rgba(0,0,0,0.5)';
    wrap.appendChild(keyEl);

    addText(after, 'stack-small', '0.55em', 'rgba(255,255,255,0.72)', 1.6);

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
        if "云阶 v4" not in ct:
            ct += '''

/* 云阶 v4：AI 重点词放大变形，其余小字 */
body.theme-stack .stack-line {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: center;
  gap: 0.06em 0.12em;
  width: min(82vw, calc(1200 * var(--s)));
  margin: 0 auto;
  text-align: center;
  line-height: 1.1;
}

body.theme-stack .stack-small {
  display: inline-block;
  white-space: pre;
  font-weight: 400;
  letter-spacing: 0.08em;
}

body.theme-stack .stack-key {
  display: inline-block;
  white-space: nowrap;
  font-weight: 700;
  letter-spacing: 0.01em;
  position: relative;
}

body.theme-stack .stack-key::after {
  content: '';
  position: absolute;
  left: 6%;
  right: 6%;
  bottom: 0.04em;
  height: 1px;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: 0.5;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=136", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
