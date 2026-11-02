import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js = r'''
  function buildFumeLine(idx) {
    S.charSpans = [];
    S.tiltSegs = [];
    S.scatterWords = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;
    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var parts = text.split(/[，。！？、；：]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length < 2) {
      var mid = Math.ceil(text.length / 2);
      parts = [text.slice(0, mid), text.slice(mid)];
    }
    parts = parts.slice(0, 3).filter(function (s) { return s.length > 0; });

    var pal = lyricPalette();
    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'fume-wrap';

    parts.forEach(function (part, i) {
      var row = document.createElement('div');
      row.className = 'fume-row r' + i;

      Array.from(part).forEach(function (ch, ci) {
        var sp = document.createElement('span');
        sp.textContent = ch;
        sp.style.color = (ci % 6 === 2) ? pal[1] : (ci % 6 === 5 ? pal[2] : '#ffffff');
        row.appendChild(sp);
      });

      wrap.appendChild(row);
    });

    main.appendChild(wrap);
  }

  function buildLumiLine(idx) {
    S.charSpans = [];
    S.tiltSegs = [];
    S.scatterWords = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;
    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var pal = lyricPalette();
    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'lumi-line';

    Array.from(text).forEach(function (ch, ci) {
      var sp = document.createElement('span');
      sp.textContent = ch;
      sp.style.color = (ci % 7 === 3) ? pal[1] : '#ffffff';
      wrap.appendChild(sp);
    });

    main.appendChild(wrap);
  }

  var FX = { canvas: null, ctx: null, parts: [], lastBurst: 0, w: 0, h: 0 };

  function initFx() {
    FX.canvas = $('fxCanvas');
    if (!FX.canvas) return;
    FX.ctx = FX.canvas.getContext('2d');
    var resize = function () {
      FX.w = FX.canvas.width = window.innerWidth;
      FX.h = FX.canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);
  }

  function fxBurst(now) {
    var accent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#7fd6ff';
    var x = FX.w * (0.15 + Math.random() * 0.7);
    var y = FX.h * (0.15 + Math.random() * 0.45);
    var count = 46;
    for (var i = 0; i < count; i++) {
      var a = Math.PI * 2 * i / count + Math.random() * 0.2;
      var sp = 1.4 + Math.random() * 3.2;
      FX.parts.push({
        x: x, y: y,
        vx: Math.cos(a) * sp,
        vy: Math.sin(a) * sp,
        life: 1,
        decay: 0.008 + Math.random() * 0.01,
        color: (i % 5 === 0) ? '#ffffff' : accent,
        size: 1 + Math.random() * 2
      });
    }
  }

  function fxLoop(now) {
    if (!FX.ctx) return;
    if (document.body.classList.contains('theme-hanabi')) {
      FX.canvas.style.display = 'block';
      FX.ctx.clearRect(0, 0, FX.w, FX.h);
      FX.ctx.globalCompositeOperation = 'lighter';

      if (now - FX.lastBurst > 1500) {
        FX.lastBurst = now;
        fxBurst(now);
      }

      for (var i = FX.parts.length - 1; i >= 0; i--) {
        var p = FX.parts[i];
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.035;
        p.vx *= 0.992;
        p.vy *= 0.992;
        p.life -= p.decay;

        if (p.life <= 0) { FX.parts.splice(i, 1); continue; }

        FX.ctx.globalAlpha = Math.max(0, p.life);
        FX.ctx.fillStyle = p.color;
        FX.ctx.beginPath();
        FX.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        FX.ctx.fill();
      }
      FX.ctx.globalAlpha = 1;
    } else if (FX.canvas.style.display !== 'none') {
      FX.canvas.style.display = 'none';
      FX.parts.length = 0;
    }

    requestAnimationFrame(fxLoop);
  }
'''

old_themes = """  var LYRIC_THEMES = [
    { id: 'plain', name: '简洁' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""

new_themes = """  var LYRIC_THEMES = [
    { id: 'plain', name: '简洁' },
    { id: 'fume', name: '浮名' },
    { id: 'lumiere', name: '流光' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'hanabi', name: '花火' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="fxCanvas"' not in t:
            anchor = '  <div class="deco"'
            if anchor in t:
                t = t.replace(anchor, '  <canvas id="fxCanvas"></canvas>\n\n' + anchor, 1)
                io.open(h, "w", encoding="utf-8", newline="").write(t)
                print("html", d)

    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function buildFumeLine" not in t:
        t = t.replace("  function buildScatterLine(idx) {", js + "\n  function buildScatterLine(idx) {", 1)

    if old_themes in t:
        t = t.replace(old_themes, new_themes)

    if "if (S.lyricTheme === 'fume')" not in t:
        t = t.replace("    if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }",
                      "    if (S.lyricTheme === 'fume') { buildFumeLine(idx); return; }\n    if (S.lyricTheme === 'lumiere') { buildLumiLine(idx); return; }\n    if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }")

    if "initFx();" not in t:
        t = t.replace("    requestAnimationFrame(loop);", "    initFx();\n    requestAnimationFrame(fxLoop);\n    requestAnimationFrame(loop);", 1)

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "浮名（横向错落）" not in ct:
            ct += '''

/* ---------------- 花火 Canvas ---------------- */
#fxCanvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
  display: none;
}

/* ---------------- 浮名（横向错落） ---------------- */
.fume-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: calc(4 * var(--s));
  max-width: 84vw;
}

.fume-row {
  font-size: calc(34 * var(--s));
  letter-spacing: 0.08em;
  line-height: 1.22;
  color: #ffffff;
  text-shadow: 0 calc(4 * var(--s)) calc(20 * var(--s)) rgba(0, 0, 0, 0.45);
}

.fume-row.r0 { transform: rotate(-1.2deg); }
.fume-row.r1 {
  font-size: calc(48 * var(--s));
  margin-left: 8%;
  transform: rotate(-0.6deg);
}
.fume-row.r2 {
  font-size: calc(28 * var(--s));
  margin-left: 16%;
  opacity: 0.85;
  transform: rotate(-1.8deg);
}

/* ---------------- 流光（单行辉光） ---------------- */
.lumi-line {
  position: relative;
  font-size: calc(54 * var(--s));
  letter-spacing: 0.05em;
  color: #ffffff;
  text-shadow:
    0 0 calc(18 * var(--s)) var(--accent, #7fd6ff),
    0 0 calc(46 * var(--s)) rgba(255, 255, 255, 0.25);
  z-index: 1;
}

.lumi-line::before {
  content: '';
  position: absolute;
  left: -18%;
  right: -18%;
  top: 50%;
  height: calc(2 * var(--s));
  background: linear-gradient(90deg, transparent, var(--accent, #7fd6ff), transparent);
  filter: blur(calc(6 * var(--s)));
  opacity: 0.55;
  z-index: -1;
}

body.theme-hanabi .line.active {
  text-shadow: 0 0 calc(24 * var(--s)) rgba(0, 0, 0, 0.6);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=72", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
