import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildCylinderLine(idx) {
    var layer = $('cylLayer');
    if (!layer) return;
    if (idx < 0 || idx >= S.lrc.length) { layer.innerHTML = ''; return; }

    layer.innerHTML = '';

    var scene = document.createElement('div');
    scene.className = 'cyl5-scene';

    var wheel = document.createElement('div');
    wheel.className = 'cyl5-wheel';

    var rings = document.createElement('div');
    rings.className = 'cyl5-rings';
    wheel.appendChild(rings);

    var core = document.createElement('div');
    core.className = 'cyl5-core';
    wheel.appendChild(core);

    var hub = document.createElement('div');
    hub.className = 'cyl5-hub';
    wheel.appendChild(hub);

    // 6 个弹膛，1 点空
    var chambers = document.createElement('div');
    chambers.className = 'cyl5-chambers';

    for (var i = 0; i < 6; i++) {
      var a = 30 + i * 60;
      var ch = document.createElement('div');
      ch.className = 'cyl5-chamber' + (i === 0 ? ' empty' : '');
      ch.style.transform = 'rotate(' + a + 'deg) translateY(calc(-158 * var(--s)))';
      chambers.appendChild(ch);
    }

    wheel.appendChild(chambers);
    scene.appendChild(wheel);

    var pointer = document.createElement('div');
    pointer.className = 'cyl5-pointer';
    scene.appendChild(pointer);

    var list = document.createElement('div');
    list.className = 'cyl5-list';

    for (var k = idx - 1; k <= idx + 1; k++) {
      if (k < 0 || k >= S.lrc.length) continue;
      var line = S.lrc[k];
      if (!line || !line.text) continue;

      var row = document.createElement('div');
      row.className = 'cyl5-row' + (k === idx ? ' current' : '');

      var t = document.createElement('div');
      t.className = 'cyl5-text';
      t.textContent = line.text;
      row.appendChild(t);

      if (k === idx && line.sub) {
        var sb = document.createElement('div');
        sb.className = 'cyl5-sub';
        sb.textContent = line.sub;
        row.appendChild(sb);
      }

      list.appendChild(row);
    }

    scene.appendChild(list);
    layer.appendChild(scene);
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

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v15" not in ct:
            ct += '''

/* 弹巢 v15：参考图布局，左侧线稿转轮 + 右侧歌词 */
body.theme-cylinder .lyrics { opacity: 0 !important; }

.cyl5-scene {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
}

.cyl5-wheel {
  position: absolute;
  left: -6vw;
  top: 50%;
  width: min(52vw, calc(760 * var(--s)));
  height: min(52vw, calc(760 * var(--s)));
  margin-top: calc(-0.5 * min(52vw, calc(760 * var(--s))));
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.35);
  background: radial-gradient(circle at 50% 50%, rgba(12, 26, 28, 0.45), rgba(5, 12, 14, 0.12) 70%);
}

.cyl5-rings {
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.16);
}

.cyl5-rings::before,
.cyl5-rings::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.12);
}

.cyl5-rings::before { inset: 12%; }
.cyl5-rings::after { inset: 26%; border-style: dashed; opacity: 0.6; }

.cyl5-chambers {
  position: absolute;
  inset: 0;
}

.cyl5-chamber {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(92 * var(--s));
  height: calc(92 * var(--s));
  margin: calc(-46 * var(--s)) 0 0 calc(-46 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.28);
  background: radial-gradient(circle at 40% 35%, rgba(143, 240, 226, 0.08), transparent 70%);
}

.cyl5-chamber.empty {
  border-style: dashed;
  opacity: 0.45;
}

.cyl5-core {
  position: absolute;
  inset: 34%;
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.18);
}

.cyl5-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(46 * var(--s));
  height: calc(46 * var(--s));
  margin: calc(-23 * var(--s)) 0 0 calc(-23 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(160, 220, 214, 0.35);
  background: radial-gradient(circle, rgba(143, 240, 226, 0.12), transparent 70%);
}

.cyl5-pointer {
  position: absolute;
  left: 38vw;
  top: 50%;
  width: 8vw;
  height: 1px;
  background: linear-gradient(90deg, rgba(200, 235, 228, 0.55), rgba(200, 235, 228, 0));
}

.cyl5-list {
  position: absolute;
  left: 48vw;
  top: 50%;
  transform: translateY(-50%);
  width: 46vw;
  display: flex;
  flex-direction: column;
  gap: calc(26 * var(--s));
}

.cyl5-row {
  opacity: 0.34;
  transform: rotate(-6deg);
  transform-origin: left center;
  transition: opacity 0.4s ease;
}

.cyl5-row.current {
  opacity: 1;
  transform: rotate(-3deg);
}

.cyl5-text {
  font-family: inherit;
  font-weight: 300;
  font-size: calc(24 * var(--s));
  line-height: 1.4;
  letter-spacing: 0.06em;
  color: rgba(235, 245, 242, 0.8);
  white-space: normal;
}

.cyl5-row.current .cyl5-text {
  font-size: calc(42 * var(--s));
  font-weight: 300;
  color: #f4faf8;
  text-shadow: 0 0 calc(30 * var(--s)) rgba(200, 240, 232, 0.25);
  letter-spacing: 0.08em;
}

.cyl5-sub {
  margin-top: calc(10 * var(--s));
  font-size: calc(17 * var(--s));
  font-weight: 300;
  letter-spacing: 0.04em;
  color: rgba(190, 215, 208, 0.55);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=250", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
