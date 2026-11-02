import io, os, re

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
    scene.className = 'cyl2-scene';

    // 弹巢
    var wheel = document.createElement('div');
    wheel.className = 'cyl2-wheel';

    var chambers = document.createElement('div');
    chambers.className = 'cyl2-chambers';

    for (var i = 0; i < 6; i++) {
      var ch = document.createElement('div');
      ch.className = 'cyl2-chamber' + (i === ((idx % 6) + 6) % 6 ? ' current' : '');

      var a = i * 60;
      ch.style.transform = 'rotate(' + a + 'deg) translateY(calc(-158 * var(--s))) rotate(' + (-a) + 'deg)';
      chambers.appendChild(ch);

      var needle = document.createElement('div');
      needle.className = 'cyl2-needle';
      needle.style.transform = 'rotate(' + a + 'deg)';
      chambers.appendChild(needle);
    }

    wheel.appendChild(chambers);

    var hub = document.createElement('div');
    hub.className = 'cyl2-hub';
    wheel.appendChild(hub);

    scene.appendChild(wheel);

    // 当前歌词：从弹巢飞向右侧
    var shot = document.createElement('div');
    shot.className = 'cyl2-shot';

    var text = document.createElement('div');
    text.className = 'cyl2-text';
    text.textContent = S.lrc[idx].text || '';
    shot.appendChild(text);

    if (S.lrc[idx].sub) {
      var sub = document.createElement('div');
      sub.className = 'cyl2-sub';
      sub.textContent = S.lrc[idx].sub;
      shot.appendChild(sub);
    }

    scene.appendChild(shot);
    main.appendChild(scene);

    var startRot = 90 - (idx - 1) * 60;
    var endRot = 90 - idx * 60;
    chambers.style.transform = 'rotate(' + startRot + 'deg)';
    requestAnimationFrame(function () {
      chambers.style.transition = 'transform 0.55s cubic-bezier(0.2, 0.8, 0.2, 1)';
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
        if "弹巢 v6" not in ct:
            ct += '''

/* 弹巢 v6：针 + 发射 */
body.theme-cylinder .lyrics,
body.theme-cylinder .lyrics-viewport {
  overflow: visible !important;
}

body.theme-cylinder .line .main {
  display: block !important;
  width: 100% !important;
  max-width: 100% !important;
}

.cyl2-scene {
  position: relative;
  width: 100%;
  height: 62vh;
}

.cyl2-wheel {
  position: absolute;
  left: 16vw;
  top: 50%;
  width: min(34vw, calc(460 * var(--s)));
  height: min(34vw, calc(460 * var(--s)));
  margin-top: calc(-0.5 * min(34vw, calc(460 * var(--s))));
  border-radius: 50%;
  border: calc(2 * var(--s)) solid rgba(143, 240, 226, 0.26);
  background:
    radial-gradient(circle at 32% 26%, rgba(120, 170, 160, 0.16), transparent 45%),
    radial-gradient(circle at 50% 55%, #22312d 0%, #101917 62%, #0a1110 100%);
  box-shadow:
    inset 0 0 calc(70 * var(--s)) rgba(0, 0, 0, 0.75),
    0 0 calc(50 * var(--s)) rgba(143, 240, 226, 0.08);
}

.cyl2-wheel::after {
  content: '';
  position: absolute;
  inset: 17%;
  border-radius: 50%;
  background: repeating-conic-gradient(
    from 0deg,
    rgba(255, 255, 255, 0.05) 0deg 3deg,
    transparent 3deg 60deg
  );
  pointer-events: none;
}

.cyl2-chambers {
  position: absolute;
  inset: 0;
  will-change: transform;
}

.cyl2-chamber {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(46 * var(--s));
  height: calc(46 * var(--s));
  margin: calc(-23 * var(--s)) 0 0 calc(-23 * var(--s));
  border-radius: 50%;
  border: calc(2 * var(--s)) solid rgba(143, 240, 226, 0.24);
  background: radial-gradient(circle at 35% 30%, #33463f, #0d1513 75%);
}

.cyl2-chamber.current {
  background: radial-gradient(circle at 35% 30%, #c8fff5, #6fd8ca 80%);
  border-color: #8ff0e2;
  box-shadow: 0 0 calc(30 * var(--s)) rgba(143, 240, 226, 0.65);
}

.cyl2-needle {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(2 * var(--s));
  height: calc(118 * var(--s));
  margin-left: calc(-1 * var(--s));
  transform-origin: center top;
  background: linear-gradient(180deg, rgba(143, 240, 226, 0.65), rgba(143, 240, 226, 0));
  pointer-events: none;
}

.cyl2-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(64 * var(--s));
  height: calc(64 * var(--s));
  margin: calc(-32 * var(--s)) 0 0 calc(-32 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.35);
  background: radial-gradient(circle, rgba(143, 240, 226, 0.18), rgba(10, 16, 15, 0.95));
}

/* 歌词针：旋转到中间 -> 高光停留 -> 向右发射 */
.cyl2-shot {
  position: absolute;
  left: 52%;
  top: 50%;
  transform: translateY(-50%);
  max-width: 52vw;
  opacity: 0;
  animation: cylFire 4.2s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.cyl2-text {
  font-size: calc(40 * var(--s));
  font-weight: 600;
  line-height: 1.3;
  color: #8ff0e2;
  text-shadow: 0 0 calc(26 * var(--s)) rgba(143, 240, 226, 0.35);
  white-space: normal;
}

.cyl2-sub {
  margin-top: calc(8 * var(--s));
  font-size: calc(18 * var(--s));
  color: rgba(190, 225, 216, 0.75);
}

@keyframes cylFire {
  0% {
    opacity: 0;
    transform: translate(-40px, -50%) scale(0.92);
  }
  12% {
    opacity: 1;
    transform: translate(0, -50%) scale(1);
  }
  55% {
    opacity: 1;
    transform: translate(0, -50%) scale(1);
  }
  72% {
    opacity: 1;
    transform: translate(18vw, -50%) scale(0.98);
  }
  100% {
    opacity: 0;
    transform: translate(58vw, -50%) scale(0.9);
  }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=241", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
