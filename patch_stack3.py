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

    var parts = splitLyricSegments(text, 3);
    if (parts.length < 2 && text.length >= 4) {
      var cut = Math.max(2, Math.min(text.length - 2, Math.floor(text.length * 0.55)));
      parts = [text.slice(0, cut), text.slice(cut)].filter(function (s) { return s.length > 0; });
    }
    if (!parts.length) parts = [text];

    var bigIdx = 0;
    for (var pi = 1; pi < parts.length; pi++) {
      if (parts[pi].length > parts[bigIdx].length) bigIdx = pi;
    }

    var big = parts[bigIdx];
    var s = Math.min(window.innerWidth * 0.000390625, window.innerHeight * 0.00069444) || 1;
    var base = 58 * s;
    var maxPx = window.innerWidth * 0.80 / Math.max(2, big.length);
    var bigEm = Math.min(2.1, maxPx / base);

    var pal = lyricPalette();

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'stack-wrap';

    parts.forEach(function (part, i) {
      var seg = document.createElement('div');
      seg.className = 'stack-seg' + (i === bigIdx ? ' big' : '');
      seg.textContent = part;

      if (i === bigIdx) {
        seg.style.setProperty('font-size', bigEm.toFixed(2) + 'em', 'important');
        seg.style.color = '#ffffff';
        seg.style.textShadow = '0 0 calc(34 * var(--s)) ' + pal[1] + ', 0 calc(8 * var(--s)) calc(30 * var(--s)) rgba(0,0,0,0.5)';
        seg.style.alignSelf = 'center';
      } else {
        seg.style.setProperty('font-size', '0.55em', 'important');
        seg.style.color = pal[i % pal.length];
        seg.style.opacity = '0.85';
        seg.style.alignSelf = (i % 2 === 0) ? 'flex-start' : 'flex-end';
        seg.style.transform = 'rotate(' + ((i % 2 === 0) ? -2.2 : 2.2) + 'deg)';
      }

      wrap.appendChild(seg);
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
    if start < 0:
        print("start miss", d)
        continue
    nxt = t.find("\n  function ", start + 10)
    if nxt < 0:
        print("end miss", d)
        continue

    t = t[:start] + new_fn + t[nxt + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v3" not in ct:
            ct += '''

/* 云阶 v3：一个巨大主句 + 小字段落 */
body.theme-stack .stack-wrap {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: calc(6 * var(--s));
  width: min(80vw, calc(1100 * var(--s)));
  margin: 0 auto;
  text-align: center;
}

body.theme-stack .stack-seg {
  white-space: normal;
  line-height: 1.12;
}

body.theme-stack .stack-seg.big {
  letter-spacing: 0.01em;
}

body.theme-stack .stack-seg.big::after {
  content: '';
  display: block;
  width: 46%;
  height: 1px;
  margin: calc(10 * var(--s)) auto 0;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: 0.55;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=135", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
