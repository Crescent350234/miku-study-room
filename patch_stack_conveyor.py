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
    S.stackItems = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    main.innerHTML = '';

    var wrap = document.createElement('div');
    wrap.className = 'stack-v';

    var from = Math.max(0, idx - 2);
    var to = Math.min(S.lrc.length - 1, idx + 2);

    for (var i = from; i <= to; i++) {
      var line = S.lrc[i];
      if (!line || !line.text) continue;

      var pair = document.createElement('div');
      pair.className = 'stack-pair';
      pair.style.top = '0px';

      var inner = document.createElement('div');
      inner.className = 'stack-inner';

      var parts = splitLyricSegments(line.text, 2);
      if (!parts.length) parts = [line.text];

      parts.forEach(function (part, pi) {
        var col = document.createElement('div');
        col.className = 'stack-col';
        col.textContent = part;
        if (pi === 1) col.style.transform = 'translateY(54px) rotate(-2.2deg)';
        inner.appendChild(col);
      });

      if (line.sub) {
        var subs = splitLyricSegments(line.sub, 2);
        subs.forEach(function (sp, si) {
          var sc = document.createElement('div');
          sc.className = 'stack-col stack-sub';
          sc.textContent = sp;
          if (si === 1) sc.style.transform = 'translateY(32px) rotate(-1.6deg)';
          inner.appendChild(sc);
        });
      }

      pair.appendChild(inner);
      wrap.appendChild(pair);
      S.stackItems.push({ i: i, el: pair });
    }

    main.appendChild(wrap);
    updateStack(0);
  }

  function updateStack(dt) {
    if (S.lyricTheme !== 'stack' || !S.stackItems || !S.stackItems.length) return;
    if (S.lrcIndex < 0 || !S.lrc.length) return;

    var cur = S.lrcIndex;
    var t0 = S.lrc[cur].t;
    var t1 = S.lrc[cur + 1] ? S.lrc[cur + 1].t : t0 + 4;
    var p = Math.max(0, Math.min(1, (S.position - t0) / Math.max(1.2, t1 - t0)));
    var currentFloat = cur + p;

    var H = window.innerHeight;
    var centerY = H * 0.46;
    var spacing = Math.max(120, H * 0.15);
    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';

    S.stackItems.forEach(function (item) {
      var y = centerY - (currentFloat - item.i) * spacing;
      var dist = Math.abs(item.i - currentFloat);
      var isCur = dist < 0.5;

      var dir = (item.i % 2 === 0) ? -1 : 1;
      item.el.style.transform = 'translate(calc(-50% + ' + (dir * 70) + 'px), ' + y.toFixed(1) + 'px)';
      item.el.style.opacity = Math.max(0, 1 - dist * 0.42).toFixed(3);
      item.el.classList.toggle('current', isCur);

      var colEls = item.el.querySelectorAll('.stack-col');
      for (var k = 0; k < colEls.length; k++) {
        if (colEls[k].classList.contains('stack-sub')) continue;
        if (isCur) {
          colEls[k].style.color = accent;
          colEls[k].style.textShadow = '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(8 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.45)';
          colEls[k].style.setProperty('font-size', 'calc(46 * var(--s))', 'important');
        } else {
          colEls[k].style.color = 'rgba(255,255,255,0.82)';
          colEls[k].style.textShadow = '0 calc(4 * var(--s)) calc(16 * var(--s)) rgba(0,0,0,0.4)';
          colEls[k].style.setProperty('font-size', 'calc(30 * var(--s))', 'important');
        }
      }
    });
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

    # call updateStack in main loop alongside updateBubbles
    if "updateStack(dt);" not in t:
        t = t.replace("    updateBubbles(dt);", "    updateBubbles(dt);\n    updateStack(dt);", 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v16" not in ct:
            ct += '''

/* 云阶 v16：连续向上滑动 */
body.theme-stack .stack-v {
  position: relative !important;
  display: block !important;
  height: 72vh !important;
  width: 100% !important;
}

body.theme-stack .stack-pair {
  position: absolute !important;
  left: 50%;
  top: 0;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(12 * var(--s));
  will-change: transform, opacity;
}

body.theme-stack .stack-inner {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(10 * var(--s));
  animation: none !important;
}

body.theme-stack .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(30 * var(--s)) !important;
  line-height: 1.05;
  letter-spacing: 0.09em;
  color: rgba(255, 255, 255, 0.82);
  max-height: 20vh;
}

body.theme-stack .stack-pair.current .stack-col {
  font-size: calc(46 * var(--s)) !important;
  font-weight: 700;
}

body.theme-stack .stack-col.stack-sub {
  font-size: calc(16 * var(--s)) !important;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.6) !important;
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
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=159", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
