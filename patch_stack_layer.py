import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_update = r'''  function stackItemFor(i) {
    if (!S.stackMap) S.stackMap = {};
    if (S.stackMap[i]) return S.stackMap[i];

    var line = S.lrc[i];
    if (!line || !line.text) return null;

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

    var layer = $('stackLayer');
    if (!layer) return null;
    layer.appendChild(pair);

    S.stackMap[i] = pair;
    return pair;
  }

  function clearStackLayer() {
    var layer = $('stackLayer');
    if (layer) layer.innerHTML = '';
    S.stackMap = {};
  }

  function updateStack(dt) {
    if (S.lyricTheme !== 'stack') {
      if (S.stackMap && Object.keys(S.stackMap).length) clearStackLayer();
      return;
    }
    if (S.lrcIndex < 0 || !S.lrc.length) return;

    var cur = S.lrcIndex;
    var t0 = S.lrc[cur].t;
    var t1 = S.lrc[cur + 1] ? S.lrc[cur + 1].t : t0 + 4;
    var p = Math.max(0, Math.min(1, (S.position - t0) / Math.max(1.2, t1 - t0)));
    var currentFloat = cur + p;

    var H = window.innerHeight;
    var centerY = H * 0.46;
    var spacing = Math.max(130, H * 0.15);
    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';

    var from = Math.max(0, cur - 2);
    var to = Math.min(S.lrc.length - 1, cur + 2);

    if (S.stackMap) {
      Object.keys(S.stackMap).forEach(function (k) {
        var ki = +k;
        if (ki < from || ki > to) {
          var el = S.stackMap[k];
          if (el && el.parentNode) el.parentNode.removeChild(el);
          delete S.stackMap[k];
        }
      });
    }

    for (var i = from; i <= to; i++) {
      var pair = stackItemFor(i);
      if (!pair) continue;

      var y = centerY - (currentFloat - i) * spacing;
      var dist = Math.abs(i - currentFloat);
      var isCur = dist < 0.5;
      var dir = (i % 2 === 0) ? -1 : 1;

      pair.style.transform = 'translate(calc(-50% + ' + (dir * 70) + 'px), ' + y.toFixed(1) + 'px)';
      pair.style.opacity = Math.max(0, 1 - dist * 0.42).toFixed(3);
      pair.classList.toggle('current', isCur);

      var colEls = pair.querySelectorAll('.stack-col');
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
    }
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

    t = t[:start] + new_update + t[nxt + 1:]

    # stack branch no longer builds per-line DOM
    t = t.replace("if (S.lyricTheme === 'stack') { buildStackLine(idx); return; }",
                  "if (S.lyricTheme === 'stack') { return; }")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    # add layer div
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="stackLayer"' not in ht:
            ht = ht.replace('<div id="bubbleLayer"', '<div id="stackLayer" class="stack-layer"></div>\n    <div id="bubbleLayer"', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=160", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v17" not in ct:
            ct += '''

/* 云阶 v17：独立常驻图层，连续滑动 */
.stack-layer {
  position: fixed;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  overflow: hidden;
}

body.theme-stack .lyrics {
  opacity: 0 !important;
}

body.theme-stack .stack-layer .stack-pair {
  position: absolute !important;
  left: 50%;
  top: 0;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(12 * var(--s));
  will-change: transform, opacity;
}

body.theme-stack .stack-layer .stack-inner {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: calc(10 * var(--s));
}

body.theme-stack .stack-layer .stack-col {
  writing-mode: vertical-rl;
  text-orientation: upright;
  font-size: calc(30 * var(--s)) !important;
  line-height: 1.05;
  letter-spacing: 0.09em;
  color: rgba(255, 255, 255, 0.82);
  max-height: 20vh;
}

body.theme-stack .stack-layer .stack-pair.current .stack-col {
  font-size: calc(46 * var(--s)) !important;
  font-weight: 700;
}

body.theme-stack .stack-layer .stack-col.stack-sub {
  font-size: calc(16 * var(--s)) !important;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.6) !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
