import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function clearCylinder() {
    var layer = $('cylLayer');
    if (layer) layer.innerHTML = '';
  }

  function buildCylinderLine(idx) {
    var layer = $('cylLayer');
    if (!layer) return;
    if (idx < 0 || idx >= S.lrc.length) { layer.innerHTML = ''; return; }

    layer.innerHTML = '';

    var scene = document.createElement('div');
    scene.className = 'cyl3-scene';

    var wheel = document.createElement('div');
    wheel.className = 'cyl3-wheel';

    var chamberWrap = document.createElement('div');
    chamberWrap.className = 'cyl3-chambers';

    // 1 点空膛，3/5/7/9/11 点各一句（沿半径/法线）
    var slots = [90, 150, 210, 270, 330];
    var offsets = [-1, -2, 2, 3, 1];

    for (var s = 0; s < slots.length; s++) {
      var li = idx + offsets[s];
      if (li < 0 || li >= S.lrc.length) continue;
      var line = S.lrc[li];
      if (!line || !line.text) continue;

      var a = slots[s];
      var holder = document.createElement('div');
      holder.className = 'cyl3-slot';
      holder.style.transform = 'rotate(' + a + 'deg) translateY(calc(-182 * var(--s)))';

      var chamber = document.createElement('div');
      chamber.className = 'cyl3-chamber';
      holder.appendChild(chamber);

      var label = document.createElement('div');
      label.className = 'cyl3-label';
      label.textContent = line.text;
      holder.appendChild(label);

      chamberWrap.appendChild(holder);
    }

    var empty = document.createElement('div');
    empty.className = 'cyl3-empty';
    empty.style.transform = 'rotate(30deg) translateY(calc(-182 * var(--s)))';
    chamberWrap.appendChild(empty);

    wheel.appendChild(chamberWrap);

    var hub = document.createElement('div');
    hub.className = 'cyl3-hub';
    wheel.appendChild(hub);

    scene.appendChild(wheel);

    var shot = document.createElement('div');
    shot.className = 'cyl3-shot';

    var text = document.createElement('div');
    text.className = 'cyl3-text';
    text.textContent = S.lrc[idx].text || '';
    shot.appendChild(text);

    if (S.lrc[idx].sub) {
      var sub = document.createElement('div');
      sub.className = 'cyl3-sub';
      sub.textContent = S.lrc[idx].sub;
      shot.appendChild(sub);
    }

    var t0 = S.lrc[idx].t;
    var t1 = S.lrc[idx + 1] ? S.lrc[idx + 1].t : t0 + 4;
    var dur = Math.max(2.6, Math.min(6, t1 - t0));
    shot.style.animationDuration = dur.toFixed(2) + 's';

    scene.appendChild(shot);
    layer.appendChild(scene);

    chamberWrap.style.transform = 'rotate(60deg)';
    requestAnimationFrame(function () {
      chamberWrap.style.transition = 'transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
      chamberWrap.style.transform = 'rotate(0deg)';
    });
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildCylinderLine(idx) {")
    end = t.find("\n  function buildQingshuLine", start)
    if start < 0 or end < 0:
        print("anchor miss", d)
        continue

    t = t[:start] + new_fn + t[end + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="cylLayer"' not in ht:
            ht = ht.replace('<div id="bubbleLayer"', '<div id="cylLayer" class="cyl-layer"></div>\n    <div id="bubbleLayer"', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=248", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v13" not in ct:
            ct += '''

/* 弹巢 v13：独立图层 */
.cyl-layer {
  position: fixed;
  inset: 0;
  z-index: 5;
  display: none;
  pointer-events: none;
}

body.theme-cylinder .cyl-layer {
  display: block;
}

body.theme-cylinder .lyrics {
  opacity: 0 !important;
}

.cyl3-scene {
  position: absolute !important;
  inset: 0 !important;
  width: 100% !important;
  height: 100% !important;
  display: block !important;
}

.cyl3-wheel {
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  width: min(34vw, calc(460 * var(--s))) !important;
  height: min(34vw, calc(460 * var(--s))) !important;
  margin-left: calc(-0.5 * min(34vw, calc(460 * var(--s)))) !important;
  margin-top: calc(-0.5 * min(34vw, calc(460 * var(--s)))) !important;
  flex: none !important;
}

.cyl3-shot {
  left: 50% !important;
  top: 50% !important;
  width: 64vw !important;
  margin-left: -32vw !important;
  margin-top: calc(-34 * var(--s)) !important;
  z-index: 6 !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
