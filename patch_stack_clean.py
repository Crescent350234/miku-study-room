import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = r'''  function stackItemFor(i) {
    if (!S.stackMap) S.stackMap = {};
    if (S.stackMap[i]) return S.stackMap[i];

    var line = S.lrc[i];
    if (!line || !line.text) return null;

    var pair = document.createElement('div');
    pair.className = 'stack-pair';
    pair.style.top = '0px';

    var inner = document.createElement('div');
    inner.className = 'stack-inner';

    var s = Math.min(window.innerWidth * 0.000390625, window.innerHeight * 0.00069444) || 1;
    var fpx = 42 * s;
    var maxChars = Math.max(3, Math.floor(window.innerHeight * 0.62 / fpx));

    var mainCol = document.createElement('div');
    mainCol.className = 'stack-col';
    mainCol.textContent = line.text;
    if (line.text.length > maxChars) {
      mainCol.style.setProperty('font-size', (window.innerHeight * 0.62 / line.text.length).toFixed(1) + 'px', 'important');
    }
    inner.appendChild(mainCol);

    if (line.sub) {
      var subCol = document.createElement('div');
      subCol.className = 'stack-col stack-sub';
      subCol.textContent = line.sub;
      inner.appendChild(subCol);
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
    var centerY = H * 0.47;
    var spacing = H * 0.36;
    var accent = (getComputedStyle(document.body).getPropertyValue('--accent') || '').trim() || '#7fd6ff';

    var from = cur;
    var to = Math.min(S.lrc.length - 1, cur + 1);

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

      pair.style.transform = 'translate(-50%, ' + y.toFixed(1) + 'px)';
      pair.style.opacity = isCur ? '1' : '0.32';
      pair.classList.toggle('current', isCur);

      var colEls = pair.querySelectorAll('.stack-col');
      for (var k2 = 0; k2 < colEls.length; k2++) {
        if (colEls[k2].classList.contains('stack-sub')) continue;
        if (isCur) {
          colEls[k2].style.color = accent;
          colEls[k2].style.textShadow = '0 0 calc(26 * var(--s)) ' + accent + ', 0 calc(8 * var(--s)) calc(26 * var(--s)) rgba(0,0,0,0.45)';
        } else {
          colEls[k2].style.color = 'rgba(255,255,255,0.8)';
          colEls[k2].style.textShadow = '0 calc(4 * var(--s)) calc(16 * var(--s)) rgba(0,0,0,0.4)';
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

    start = t.find("  function stackItemFor(i) {")
    if start < 0:
        print("start miss", d)
        continue
    # ensure old updateStack removed after new block: find old updateStack after start
    old_up = t.find("  function updateStack(dt) {", start)
    nxt = t.find("\n  function ", old_up + 10) if old_up >= 0 else -1
    if old_up < 0 or nxt < 0:
        print("end miss", d)
        continue

    t = t[:start] + new_block + t[nxt + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "云阶 v18" not in ct:
            ct += '''

/* 云阶 v18：一列到底，干净清晰 */
body.theme-stack .stack-layer .stack-pair {
  left: 50% !important;
  gap: 0 !important;
}

body.theme-stack .stack-layer .stack-inner {
  gap: calc(14 * var(--s)) !important;
}

body.theme-stack .stack-layer .stack-col {
  writing-mode: vertical-rl !important;
  text-orientation: upright !important;
  font-size: calc(42 * var(--s)) !important;
  line-height: 1.06 !important;
  letter-spacing: 0.1em !important;
  max-height: 64vh !important;
  font-weight: 500;
}

body.theme-stack .stack-layer .stack-pair.current .stack-col {
  font-size: calc(46 * var(--s)) !important;
  font-weight: 700;
}

body.theme-stack .stack-layer .stack-col.stack-sub {
  font-size: calc(17 * var(--s)) !important;
  letter-spacing: 0.05em !important;
  color: rgba(255, 255, 255, 0.55) !important;
  max-height: 52vh !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=163", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
