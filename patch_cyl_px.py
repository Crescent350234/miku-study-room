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

    wheel.appendChild(rotor);
    scene.appendChild(wheel);
    layer.appendChild(scene);

    var wheelW = wheel.getBoundingClientRect().width || 300;
    var R = Math.max(100, Math.round(wheelW * 0.313));

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
      holder.style.cssText =
        'position:absolute;left:50%;top:50%;transform-origin:0 50%;' +
        'transform:rotate(' + slots[s].a + 'deg) translateY(-' + R + 'px) rotate(-90deg);';

      var txt = document.createElement('span');
      txt.className = 'cyl5-label-text';
      txt.textContent = line.text;
      txt.style.cssText =
        'display:inline-block;white-space:nowrap;font-weight:300;letter-spacing:0.06em;' +
        'font-size:' + (li === idx ? 26 : 20) + 'px;' +
        'color:' + (li === idx ? '#8ff0e2' : 'rgba(228,236,232,0.42)') + ';';
      holder.appendChild(txt);

      if (li === idx && line.sub) {
        var sb = document.createElement('span');
        sb.className = 'cyl5-label-sub';
        sb.textContent = line.sub;
        sb.style.cssText =
          'display:block;white-space:nowrap;margin-top:6px;font-size:15px;' +
          'color:rgba(200,222,216,0.55);';
        holder.appendChild(sb);
      }

      rotor.appendChild(holder);
    }

    rotor.style.transform = 'rotate(60deg)';
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

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=282", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
