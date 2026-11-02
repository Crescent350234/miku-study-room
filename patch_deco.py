import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

deco_html = '''  <div class="deco" aria-hidden="true">
    <span class="d-tri t1"></span>
    <span class="d-tri t2"></span>
    <span class="d-plus p1"></span>
    <span class="d-plus p2"></span>
    <span class="d-plus p3"></span>
    <span class="d-ring r1"></span>
    <span class="d-ring r2"></span>
  </div>

'''

helper = r'''
  function lyricPalette() {
    var cs = getComputedStyle(document.body);
    var a = (cs.getPropertyValue('--accent') || '').trim() || '#7fd6ff';
    var p = (cs.getPropertyValue('--pink') || '').trim() || '#ff9ecb';
    return ['#ffffff', a, p, '#ffd479', '#c9a7ff'];
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'class="deco"' not in t:
            anchor = '  <div class="lyrics-area"'
            if anchor not in t:
                anchor = '<div class="lyrics-area"'
            if anchor in t:
                t = t.replace(anchor, deco_html + anchor.replace('  ', '  ', 1), 1)
                io.open(h, "w", encoding="utf-8", newline="").write(t)
                print("html", d)

    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function lyricPalette" not in t:
        t = t.replace("  function buildScatterLine(idx) {", helper + "\n  function buildScatterLine(idx) {", 1)

    # scatter: every word gets a palette color
    t = t.replace("      if (Math.abs(r4 - 0.5) > 0.3) elWord.style.color = S.charAccent;",
                  "      var __pal = lyricPalette();\n      elWord.style.color = __pal[i % __pal.length];")

    # stack: per-segment color, size, rotation
    old_stack = """      var seg = document.createElement('div');
      seg.className = 'stack-seg' + (i === bigIdx ? ' big' : '');
      seg.textContent = part;"""
    new_stack = """      var seg = document.createElement('div');
      seg.className = 'stack-seg' + (i === bigIdx ? ' big' : '');
      seg.textContent = part;

      var __pal2 = lyricPalette();
      seg.style.color = __pal2[i % __pal2.length];
      var __r = Math.abs((Math.sin(seed + i * 11) * 10000) % 1);
      if (i === bigIdx) {
        seg.style.fontSize = '1.65em';
        seg.style.textShadow = '0 0 calc(24 * var(--s)) ' + (S.charAccent || '#7fd6ff');
      } else {
        seg.style.fontSize = (0.62 + __r * 0.42).toFixed(2) + 'em';
        seg.style.transform = 'rotate(' + ((__r - 0.5) * 7).toFixed(1) + 'deg) translateY(0)';
      }"""
    if old_stack in t:
        t = t.replace(old_stack, new_stack)

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".deco" not in ct:
            ct += '''

/* ---------------- 背景几何层 ---------------- */
.deco {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  color: var(--accent, #7fd6ff);
  opacity: 0.09;
}

.deco span { position: absolute; display: block; }

.d-tri {
  width: 0;
  height: 0;
  border-left: calc(38 * var(--s)) solid transparent;
  border-right: calc(38 * var(--s)) solid transparent;
  border-bottom: calc(64 * var(--s)) solid currentColor;
}

.d-tri.t1 { left: 8%; top: 18%; transform: rotate(-14deg); }
.d-tri.t2 { right: 12%; bottom: 20%; transform: rotate(24deg) scale(1.3); }

.d-plus { width: calc(46 * var(--s)); height: calc(46 * var(--s)); }
.d-plus::before, .d-plus::after {
  content: '';
  position: absolute;
  background: currentColor;
}
.d-plus::before { left: 50%; top: 0; width: calc(6 * var(--s)); height: 100%; transform: translateX(-50%); }
.d-plus::after { top: 50%; left: 0; height: calc(6 * var(--s)); width: 100%; transform: translateY(-50%); }

.d-plus.p1 { left: 18%; bottom: 26%; transform: rotate(12deg); }
.d-plus.p2 { right: 20%; top: 16%; transform: rotate(-18deg) scale(0.8); }
.d-plus.p3 { right: 34%; bottom: 14%; transform: rotate(28deg) scale(0.6); }

.d-ring {
  border: 1px solid currentColor;
  border-radius: 50%;
}

.d-ring.r1 { left: 10%; top: 46%; width: calc(220 * var(--s)); height: calc(220 * var(--s)); opacity: 0.8; }
.d-ring.r2 { right: 8%; top: 34%; width: calc(320 * var(--s)); height: calc(320 * var(--s)); opacity: 0.5; }

/* 云阶大字下的细装饰线 */
.stack-seg.big::after {
  content: '';
  display: block;
  width: 64%;
  height: 1px;
  margin: calc(10 * var(--s)) auto 0;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: 0.65;
}

/* 当前行更柔和的淡入淡出 */
.line {
  transition: color 0.5s ease, opacity 0.6s ease, filter 0.6s ease,
              font-size 0.55s var(--ease), transform 0.55s var(--ease);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=59", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
