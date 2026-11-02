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
    wheel.appendChild(buildCylinderSvg());

    // 当前句沿 3 点方向半径插在弹孔上；其余句分布在 5/7/9/11 点
    var slots = [
      { off: 0,  a: 90  },
      { off: -1, a: 150 },
      { off: -2, a: 210 },
      { off: 1,  a: 330 },
      { off: 2,  a: 270 }
    ];

    var dur = 4;
    if (S.lrc[idx + 1]) {
      dur = Math.max(2.8, Math.min(6, S.lrc[idx + 1].t - S.lrc[idx].t));
    }

    for (var s = 0; s < slots.length; s++) {
      var li = idx + slots[s].off;
      if (li < 0 || li >= S.lrc.length) continue;
      var line = S.lrc[li];
      if (!line || !line.text) continue;

      var holder = document.createElement('div');
      holder.className = 'cyl5-label' + (li === idx ? ' current' : '');
      holder.style.transform =
        'rotate(' + slots[s].a + 'deg) translateY(calc(-196 * var(--s))) rotate(-90deg)';

      var inner = document.createElement('div');
      inner.className = 'cyl5-label-inner';
      inner.textContent = line.text;
      if (li === idx) inner.style.animationDuration = dur.toFixed(2) + 's';
      holder.appendChild(inner);

      if (li === idx && line.sub) {
        var sb = document.createElement('div');
        sb.className = 'cyl5-label-sub';
        sb.textContent = line.sub;
        holder.appendChild(sb);
      }

      wheel.appendChild(holder);
    }

    scene.appendChild(wheel);
    layer.appendChild(scene);

    // 转轮旋转一格
    var endAngle = (idx * 60);
    wheel.style.transform = 'rotate(' + (endAngle + 60) + 'deg)';
    requestAnimationFrame(function () {
      wheel.style.transition = 'transform 0.62s cubic-bezier(0.18, 0.8, 0.22, 1)';
      wheel.style.transform = 'rotate(' + endAngle + 'deg)';
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
        if "弹巢 v28" not in ct:
            ct += '''

/* 弹巢 v28：歌词沿半径插在弹孔上 */
.cyl5-list,
.cyl5-pointer {
  display: none !important;
}

.cyl5-label {
  position: absolute;
  left: 50%;
  top: 50%;
  transform-origin: 0 50%;
  pointer-events: none;
}

.cyl5-label-inner {
  font-weight: 300;
  font-size: calc(16 * var(--s));
  line-height: 1.2;
  letter-spacing: 0.06em;
  color: rgba(228, 238, 234, 0.32);
  white-space: nowrap;
  max-width: 64vw;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cyl5-label.current .cyl5-label-inner {
  font-size: calc(42 * var(--s));
  color: #f6fbf9;
  text-shadow: 0 2px calc(18 * var(--s)) rgba(0, 0, 0, 0.55);
  animation-name: cylRadialFire;
  animation-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1);
  animation-fill-mode: forwards;
}

.cyl5-label-sub {
  margin-top: calc(8 * var(--s));
  font-size: calc(17 * var(--s));
  color: rgba(200, 222, 216, 0.55);
  white-space: nowrap;
}

@keyframes cylRadialFire {
  0%   { opacity: 0; transform: translateX(-10vw); }
  12%  { opacity: 1; transform: translateX(0); }
  60%  { opacity: 1; transform: translateX(0); }
  80%  { opacity: 1; transform: translateX(10vw); }
  100% { opacity: 0; transform: translateX(40vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=267", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
