import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Studio Room\wallpaper",
]

# 修正可能的路径错误
dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildCylinderLine(idx) {
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    main.innerHTML = '';

    var scene = document.createElement('div');
    scene.className = 'cyl-scene';

    // 左轮转盘
    var wheel = document.createElement('div');
    wheel.className = 'cyl-wheel';

    var ring1 = document.createElement('div');
    ring1.className = 'cyl-ring r1';
    wheel.appendChild(ring1);

    var ring2 = document.createElement('div');
    ring2.className = 'cyl-ring r2';
    wheel.appendChild(ring2);

    var chambers = document.createElement('div');
    chambers.className = 'cyl-chambers';

    for (var i = 0; i < 6; i++) {
      var ch = document.createElement('div');
      ch.className = 'cyl-chamber' + (i === ((idx % 6) + 6) % 6 ? ' current' : '');
      var dot = document.createElement('span');
      dot.className = 'cyl-dot';
      ch.appendChild(dot);

      var a = i * 60;
      ch.style.transform = 'rotate(' + a + 'deg) translateY(calc(-150 * var(--s))) rotate(' + (-a) + 'deg)';
      chambers.appendChild(ch);
    }

    wheel.appendChild(chambers);

    var core = document.createElement('div');
    core.className = 'cyl-core';
    wheel.appendChild(core);

    var pointer = document.createElement('div');
    pointer.className = 'cyl-pointer';
    wheel.appendChild(pointer);

    scene.appendChild(wheel);

    // 右侧歌词
    var lines = document.createElement('div');
    lines.className = 'cyl-lines';

    for (var k = idx - 1; k <= idx + 1; k++) {
      if (k < 0 || k >= S.lrc.length) continue;
      var line = S.lrc[k];
      if (!line || !line.text) continue;

      var row = document.createElement('div');
      row.className = 'cyl-line' + (k === idx ? ' current' : '');

      var txt = document.createElement('div');
      txt.className = 'cyl-line-text';
      txt.textContent = line.text;
      row.appendChild(txt);

      if (k === idx && line.sub) {
        var sub = document.createElement('div');
        sub.className = 'cyl-line-sub';
        sub.textContent = line.sub;
        row.appendChild(sub);
      }

      lines.appendChild(row);
    }

    scene.appendChild(lines);
    main.appendChild(scene);

    // 从上一格转到当前格
    var startRot = 90 - (idx - 1) * 60;
    var endRot = 90 - idx * 60;
    chambers.style.transform = 'rotate(' + startRot + 'deg)';
    requestAnimationFrame(function () {
      chambers.style.transition = 'transform 0.62s cubic-bezier(0.2, 0.8, 0.2, 1)';
      chambers.style.transform = 'rotate(' + endRot + 'deg)';
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

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v3" not in ct:
            ct += '''

/* 弹巢 v3：左侧转轮 + 指针 + 右侧歌词 */
body.theme-cylinder .lyrics,
body.theme-cylinder .lyrics-viewport {
  overflow: visible !important;
}

.cyl-scene {
  display: flex;
  align-items: center;
  gap: calc(52 * var(--s));
  width: 92vw;
  height: 56vh;
  margin: 0 auto;
}

.cyl-wheel {
  position: relative;
  flex: 0 0 auto;
  width: min(40vw, calc(520 * var(--s)));
  height: min(40vw, calc(520 * var(--s)));
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.22);
  box-shadow: inset 0 0 calc(70 * var(--s)) rgba(0, 0, 0, 0.55),
              0 0 calc(50 * var(--s)) rgba(143, 240, 226, 0.08);
  background: radial-gradient(circle at 50% 50%, rgba(20, 34, 31, 0.55), rgba(10, 16, 15, 0.75));
}

.cyl-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.14);
  pointer-events: none;
}

.cyl-ring.r1 { inset: 7%; }
.cyl-ring.r2 { inset: 16%; border-style: dashed; opacity: 0.5; }

.cyl-chambers {
  position: absolute;
  inset: 0;
  will-change: transform;
}

.cyl-chamber {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(54 * var(--s));
  height: calc(54 * var(--s));
  margin: calc(-27 * var(--s)) 0 0 calc(-27 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.28);
  background: rgba(14, 24, 22, 0.75);
  box-shadow: inset 0 0 calc(16 * var(--s)) rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cyl-chamber.current {
  background: #8ff0e2;
  border-color: #8ff0e2;
  box-shadow: 0 0 calc(28 * var(--s)) rgba(143, 240, 226, 0.6);
}

.cyl-dot {
  width: calc(10 * var(--s));
  height: calc(10 * var(--s));
  border-radius: 50%;
  background: rgba(143, 240, 226, 0.55);
}

.cyl-chamber.current .cyl-dot {
  background: #0d1a17;
}

.cyl-core {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(70 * var(--s));
  height: calc(70 * var(--s));
  margin: calc(-35 * var(--s)) 0 0 calc(-35 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.3);
  background: radial-gradient(circle, rgba(143, 240, 226, 0.16), rgba(10, 16, 15, 0.9));
}

.cyl-pointer {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 34%;
  height: 1px;
  transform-origin: left center;
  background: linear-gradient(90deg, rgba(143, 240, 226, 0.85), rgba(143, 240, 226, 0));
}

.cyl-lines {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: calc(26 * var(--s));
  min-width: 0;
}

.cyl-line {
  opacity: 0.32;
  transform: rotate(-1.6deg);
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.cyl-line.current {
  opacity: 1;
  transform: none;
}

.cyl-line-text {
  font-size: calc(26 * var(--s));
  line-height: 1.35;
  color: rgba(235, 245, 242, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cyl-line.current .cyl-line-text {
  font-size: calc(44 * var(--s));
  font-weight: 600;
  color: #8ff0e2;
  text-shadow: 0 0 calc(26 * var(--s)) rgba(143, 240, 226, 0.35);
}

.cyl-line-sub {
  margin-top: calc(8 * var(--s));
  font-size: calc(18 * var(--s));
  color: rgba(190, 220, 212, 0.65);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=238", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
