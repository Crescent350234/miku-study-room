import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function pickTiltKey(text, seed) {
    var candidates = [];

    if (S.aiTheme && S.aiTheme.emphasis) {
      S.aiTheme.emphasis.forEach(function (w) {
        if (w && w.length >= 2 && w.length <= 6 && text.indexOf(w) >= 0 && w.length < text.length) {
          candidates.push(w);
        }
      });
    }
    if (!candidates.length && S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word && wc.word.length >= 2 && wc.word.length <= 6 && text.indexOf(wc.word) >= 0 && wc.word.length < text.length) {
          candidates.push(wc.word);
        }
      });
    }

    if (!candidates.length) {
      var chunks = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.length >= 2; });
      chunks.forEach(function (chunk) {
        var arr = Array.from(chunk);
        for (var i = 0; i + 2 <= arr.length; i += 1) {
          candidates.push(arr.slice(i, i + Math.min(3, arr.length - i)).join(''));
        }
      });
      candidates = candidates.filter(function (w) { return w.length >= 2 && w.length <= 4 && w.length < text.length; });
    }

    if (!candidates.length) return '';
    return candidates[Math.abs(seed) % candidates.length];
  }

  function buildTiltLine(idx) {
    S.charSpans = [];
    S.tiltSegs = [];
    S.scatterWords = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var seed = Math.floor(line.t * 1000) + text.length;

    var key = pickTiltKey(text, seed);
    if (!key) key = text;

    var keyPos = text.indexOf(key);
    if (keyPos < 0) { key = text; keyPos = 0; }

    var before = text.slice(0, keyPos);
    var after = text.slice(keyPos + key.length);

    var keyColor = '';
    if (S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word === key && wc.color) keyColor = wc.color;
      });
    }
    var accentKey = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';

    var s = Math.min(window.innerWidth * 0.000390625, window.innerHeight * 0.00069444) || 1;
    var base = 58 * s;
    var maxPx = window.innerWidth * 0.68 / Math.max(1, key.length);
    var keyEm = Math.min(2.6, Math.max(1.5, maxPx / base));

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'tilt-line';

    function addSmall(part, align) {
      if (!part) return;
      var row = document.createElement('div');
      row.className = 'tilt-small';
      row.style.justifyContent = align;

      Array.from(part).forEach(function (ch, ci) {
        var sp = document.createElement('span');
        sp.className = 'tilt-sm-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        var rr = Math.abs((Math.sin(seed + ci * 9) * 10000) % 1);
        sp.style.fontSize = (0.55 + rr * 0.18).toFixed(2) + 'em';
        sp.style.transform = 'translateY(' + ((rr - 0.5) * 9).toFixed(1) + 'px) rotate(' + ((rr - 0.5) * 9).toFixed(1) + 'deg)';
        if (ci % 5 === 2) sp.style.color = accentKey;
        row.appendChild(sp);
      });

      wrap.appendChild(row);
    }

    addSmall(before, 'center');

    var keyEl = document.createElement('div');
    keyEl.className = 'tilt-key';
    keyEl.textContent = key;
    keyEl.style.setProperty('font-size', keyEm.toFixed(2) + 'em', 'important');
    keyEl.style.color = keyColor || accentKey;
    keyEl.style.transform = 'rotate(-3deg) skewX(-7deg) translateY(4px)';
    keyEl.style.textShadow = '0 0 calc(34 * var(--s)) ' + (keyColor || accentKey) + ', 0 calc(10 * var(--s)) calc(32 * var(--s)) rgba(0,0,0,0.45)';
    wrap.appendChild(keyEl);

    addSmall(after, 'center');

    main.appendChild(wrap);
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildTiltLine(idx) {")
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
        if "倾诉 v5：关键词放大" not in ct:
            ct += '''

/* 倾诉 v5：只放关键词，其余小字错落 */
body.theme-tilt .tilt-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: calc(4 * var(--s));
  width: min(82vw, calc(1200 * var(--s)));
  margin: 0 auto;
  text-align: center;
}

body.theme-tilt .tilt-small {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.04em 0.06em;
  width: 100%;
  opacity: 0.85;
  line-height: 1.2;
}

body.theme-tilt .tilt-sm-char {
  display: inline-block;
  white-space: pre;
  font-weight: 400;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.78);
}

body.theme-tilt .tilt-key {
  display: inline-block;
  white-space: nowrap;
  font-weight: 700;
  letter-spacing: 0.02em;
  line-height: 1.05;
  position: relative;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=140", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
