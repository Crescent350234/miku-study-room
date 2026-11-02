import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildCylinderLine(idx) {
    var layer = $('cylLayer');
    if (!layer) return;
    if (idx < 0 || idx >= S.lrc.length) { return; }

    layer.innerHTML = '';

    var scene = document.createElement('div');
    scene.className = 'cyl5-scene';

    var wheel = document.createElement('div');
    wheel.className = 'cyl5-wheel';

    var rotor = document.createElement('div');
    rotor.className = 'cyl5-rotor';
    rotor.appendChild(buildCylinderSvg());

    var dur = 4;
    if (S.lrc[idx + 1]) {
      dur = Math.max(2.8, Math.min(6, S.lrc[idx + 1].t - S.lrc[idx].t));
    }

    // 当前句 3 点，其它 5/7/9/11 点
    var slots = [
      { off: 0,  a: 90  },
      { off: -1, a: 150 },
      { off: -2, a: 210 },
      { off: 1,  a: 330 },
      { off: 2,  a: 270 }
    ];

    for (var s = 0; s < slots.length; s++) {
      var li = idx + slots[s].off;
      if (li < 0 || li >= S.lrc.length) continue;
      var line = S.lrc[li];
      if (!line || !line.text) continue;

      var holder = document.createElement('div');
      holder.className = 'cyl5-label' + (li === idx ? ' current' : '');
      holder.style.transform =
        'rotate(' + slots[s].a + 'deg) translateY(calc(-0.313 * min(58vw, calc(920 * var(--s))))) rotate(-90deg)';

      var inner = document.createElement('div');
      inner.className = 'cyl5-label-inner';
      inner.textContent = line.text;
      if (li === idx) inner.style.animationDuration = dur.toFixed(2) + 's';
      holder.appendChild(inner);

      if (li === idx && line.sub) {
        var sb = document.createElement('div');
        sb.className = 'cyl5-label-sub';
        sb.textContent = line.sub;
        inner.appendChild(sb);
      }

      rotor.appendChild(holder);
    }

    wheel.appendChild(rotor);
    scene.appendChild(wheel);
    layer.appendChild(scene);

    // 歌词跟着转轮从 1 点方向转上来到 3 点
    rotor.style.transform = 'rotate(-60deg)';
    requestAnimationFrame(function () {
      rotor.style.transition = 'transform 0.62s cubic-bezier(0.18, 0.8, 0.22, 1)';
      rotor.style.transform = 'rotate(0deg)';
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
        if "弹巢 v31" not in ct:
            ct += '''

/* 弹巢 v31：歌词随转轮旋转 + 整句发射 */
.cyl5-rotor {
  position: absolute;
  inset: 0;
  transform-origin: 50% 50%;
  will-change: transform;
}

.cyl5-label-sub {
  display: block;
  margin-top: calc(6 * var(--s));
  font-size: calc(16 * var(--s));
  color: rgba(200, 222, 216, 0.6);
}

.cyl5-label.current .cyl5-label-inner {
  animation-name: cylRadialFire3 !important;
  animation-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1);
  animation-fill-mode: forwards;
  display: inline-block;
}

@keyframes cylRadialFire3 {
  0%   { opacity: 0; transform: translateX(0); }
  10%  { opacity: 1; transform: translateX(0); }
  60%  { opacity: 1; transform: translateX(0); }
  78%  { opacity: 1; transform: translateX(8vw); }
  100% { opacity: 0; transform: translateX(44vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=273", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
