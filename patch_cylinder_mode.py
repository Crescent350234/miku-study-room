import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

fn = r'''
  function buildCylinderLine(idx) {
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    main.innerHTML = '';

    var stage = document.createElement('div');
    stage.className = 'cyl-stage';

    var cyl = document.createElement('div');
    cyl.className = 'cyl';

    for (var i = idx - 2; i <= idx + 3; i++) {
      if (i < 0 || i >= S.lrc.length) continue;
      var line = S.lrc[i];
      if (!line || !line.text) continue;

      var ch = document.createElement('div');
      ch.className = 'cyl-ch' + (i === idx ? ' current' : '');
      var angle = (i - idx) * 60;
      ch.style.transform = 'rotateX(' + angle + 'deg) translateZ(calc(150 * var(--s)))';

      var t = document.createElement('div');
      t.className = 'cyl-text';
      t.textContent = line.text;
      ch.appendChild(t);

      if (i === idx && line.sub) {
        var sb = document.createElement('div');
        sb.className = 'cyl-sub';
        sb.textContent = line.sub;
        ch.appendChild(sb);
      }

      cyl.appendChild(ch);
    }

    stage.appendChild(cyl);
    main.appendChild(stage);

    cyl.style.transform = 'rotateX(60deg)';
    requestAnimationFrame(function () {
      cyl.style.transition = 'transform 0.55s cubic-bezier(0.2, 0.8, 0.2, 1)';
      cyl.style.transform = 'rotateX(0deg)';
    });
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "id: 'cylinder'" not in t:
        t = t.replace("    { id: 'qingshu', name: '青书' }", "    { id: 'qingshu', name: '青书' },\n    { id: 'cylinder', name: '弹巢' }")

    if "function buildCylinderLine" not in t:
        t = t.replace("  function buildQingshuLine(idx) {", fn + "\n  function buildQingshuLine(idx) {", 1)

    if "buildCylinderLine(idx)" not in t:
        t = t.replace("if (S.lyricTheme === 'qingshu') { return; }",
                      "if (S.lyricTheme === 'qingshu') { return; }\n    if (S.lyricTheme === 'cylinder') { buildCylinderLine(idx); return; }")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v1" not in ct:
            ct += '''

/* 弹巢：左轮歌词 */
body.theme-cylinder .lyrics,
body.theme-cylinder .lyrics-viewport {
  overflow: visible !important;
}

.cyl-stage {
  width: 100%;
  height: 46vh;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
}

.cyl {
  position: relative;
  width: min(78vw, calc(1000 * var(--s)));
  height: 100%;
  transform-style: preserve-3d;
}

.cyl-ch {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  margin-top: calc(-42 * var(--s));
  text-align: center;
  backface-visibility: hidden;
  transform-origin: center center;
}

.cyl-text {
  font-size: calc(40 * var(--s));
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: 0.02em;
  color: rgba(255, 255, 255, 0.28);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;
}

.cyl-sub {
  margin-top: calc(6 * var(--s));
  font-size: calc(18 * var(--s));
  color: rgba(190, 215, 208, 0.5);
  white-space: nowrap;
}

.cyl-ch.current .cyl-text {
  color: #8ff0e2;
  text-shadow: 0 0 calc(24 * var(--s)) rgba(143, 240, 226, 0.35);
}

.cyl-ch.current .cyl-sub {
  color: rgba(180, 230, 220, 0.8);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=235", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
