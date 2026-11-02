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
    scene.className = 'cyl3-scene';

    var wheel = document.createElement('div');
    wheel.className = 'cyl3-wheel';

    var chamberWrap = document.createElement('div');
    chamberWrap.className = 'cyl3-chambers';

    // 1 点（30°）空膛，3/5/7/9/11 点各一句
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
      holder.style.transform = 'rotate(' + a + 'deg) translateY(calc(-172 * var(--s)))';

      var label = document.createElement('div');
      label.className = 'cyl3-label' + (li === idx ? ' current' : '');
      label.textContent = line.text;
      label.style.transform = 'rotate(' + (90 - a) + 'deg)';
      holder.appendChild(label);

      var chamber = document.createElement('div');
      chamber.className = 'cyl3-chamber';
      holder.appendChild(chamber);

      chamberWrap.appendChild(holder);
    }

    // 空膛（1 点）
    var empty = document.createElement('div');
    empty.className = 'cyl3-empty';
    empty.style.transform = 'rotate(30deg) translateY(calc(-172 * var(--s))) translate(-50%, -50%)';
    chamberWrap.appendChild(empty);

    wheel.appendChild(chamberWrap);

    var hub = document.createElement('div');
    hub.className = 'cyl3-hub';
    wheel.appendChild(hub);

    scene.appendChild(wheel);

    // 当前歌词：从 1 点滑到正中，停留，再向右发射
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
    main.appendChild(scene);

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

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v7" not in ct:
            ct += '''

/* 弹巢 v7：居中转轮，1 点空膛，歌词滑到中心后发射 */
body.theme-cylinder .lyrics,
body.theme-cylinder .lyrics-viewport {
  overflow: visible !important;
}

body.theme-cylinder .line .main {
  display: block !important;
  width: 100% !important;
  max-width: 100% !important;
}

.cyl3-scene {
  position: relative;
  width: 100%;
  height: 66vh;
}

.cyl3-wheel {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(38vw, calc(520 * var(--s)));
  height: min(38vw, calc(520 * var(--s)));
  margin-left: calc(-0.5 * min(38vw, calc(520 * var(--s))));
  margin-top: calc(-0.5 * min(38vw, calc(520 * var(--s))));
  border-radius: 50%;
  border: calc(2 * var(--s)) solid rgba(143, 240, 226, 0.26);
  background:
    radial-gradient(circle at 32% 26%, rgba(120, 170, 160, 0.16), transparent 45%),
    radial-gradient(circle at 50% 55%, #22312d 0%, #101917 62%, #0a1110 100%);
  box-shadow:
    inset 0 0 calc(80 * var(--s)) rgba(0, 0, 0, 0.75),
    0 0 calc(60 * var(--s)) rgba(143, 240, 226, 0.08);
}

.cyl3-wheel::after {
  content: '';
  position: absolute;
  inset: 16%;
  border-radius: 50%;
  background: repeating-conic-gradient(
    from 0deg,
    rgba(255, 255, 255, 0.05) 0deg 3deg,
    transparent 3deg 60deg
  );
}

.cyl3-chambers {
  position: absolute;
  inset: 0;
  will-change: transform;
}

.cyl3-slot {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
  transform-origin: center center;
}

.cyl3-chamber {
  position: absolute;
  left: 0;
  top: 0;
  width: calc(46 * var(--s));
  height: calc(46 * var(--s));
  margin: calc(-23 * var(--s)) 0 0 calc(-23 * var(--s));
  border-radius: 50%;
  border: calc(2 * var(--s)) solid rgba(143, 240, 226, 0.26);
  background: radial-gradient(circle at 35% 30%, #33463f, #0d1513 75%);
}

.cyl3-empty {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(50 * var(--s));
  height: calc(50 * var(--s));
  border-radius: 50%;
  border: 1px dashed rgba(143, 240, 226, 0.22);
  transform-origin: left top;
}

.cyl3-label {
  position: absolute;
  left: 0;
  top: 0;
  width: calc(220 * var(--s));
  margin-left: calc(-110 * var(--s));
  margin-top: calc(-56 * var(--s));
  text-align: center;
  font-size: calc(18 * var(--s));
  color: rgba(220, 236, 231, 0.45);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cyl3-label.current {
  color: #8ff0e2;
}

.cyl3-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  width: calc(70 * var(--s));
  height: calc(70 * var(--s));
  margin: calc(-35 * var(--s)) 0 0 calc(-35 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(143, 240, 226, 0.35);
  background: radial-gradient(circle, rgba(143, 240, 226, 0.18), rgba(10, 16, 15, 0.95));
}

.cyl3-shot {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 62vw;
  margin-left: -31vw;
  margin-top: calc(-30 * var(--s));
  text-align: center;
  opacity: 0;
  animation-name: cylLoadFire;
  animation-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1);
  animation-fill-mode: forwards;
}

.cyl3-text {
  font-size: calc(46 * var(--s));
  font-weight: 600;
  line-height: 1.25;
  color: #8ff0e2;
  text-shadow: 0 0 calc(30 * var(--s)) rgba(143, 240, 226, 0.4);
}

.cyl3-sub {
  margin-top: calc(8 * var(--s));
  font-size: calc(18 * var(--s));
  color: rgba(190, 225, 216, 0.7);
}

@keyframes cylLoadFire {
  0% {
    opacity: 0;
    transform: translate(22vw, -14vh) scale(0.7);
  }
  14% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  52% {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  66% {
    opacity: 1;
    transform: translate(10vw, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(64vw, 0) scale(0.92);
  }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=242", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
