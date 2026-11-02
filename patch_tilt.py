import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js = r'''
  function buildTiltLine(idx) {
    S.charSpans = [];
    S.tiltSegs = [];
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var t0 = line.t;
    var t1 = S.lrc[idx + 1] ? S.lrc[idx + 1].t : t0 + Math.max(4, text.length * 0.35);
    var dur = Math.max(1.4, t1 - t0);

    var parts = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length < 2) {
      var mid = Math.ceil(text.length / 2);
      parts = [text.slice(0, mid), text.slice(mid)];
    }
    parts = parts.slice(0, 4).filter(function (s) { return s.length > 0; });

    var seed = Math.floor(t0 * 1000) + text.length;
    var tiltIdx = seed % parts.length;

    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#8ef';

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'tilt-wrap';

    var per = dur / parts.length;

    parts.forEach(function (part, i) {
      var seg = document.createElement('div');
      seg.className = 'tilt-seg' + (i === tiltIdx ? ' tilt' : '');
      seg.dataset.t0 = (t0 + i * per).toFixed(3);
      seg.dataset.t1 = (t0 + (i + 1) * per).toFixed(3);

      if (i === tiltIdx) {
        Array.from(part).forEach(function (ch, ci) {
          var c = document.createElement('span');
          c.className = 'tc ' + (ci % 2 ? 'up' : 'down');
          c.textContent = ch;
          seg.appendChild(c);
        });
      } else {
        seg.textContent = part;
      }

      wrap.appendChild(seg);
      S.tiltSegs.push(seg);
    });

    main.appendChild(wrap);
  }

  function paintTilt(pos) {
    if (!S.tiltSegs || !S.tiltSegs.length) return;
    var accent = S.charAccent || '#8ef';

    for (var i = 0; i < S.tiltSegs.length; i++) {
      var seg = S.tiltSegs[i];
      var t0 = +seg.dataset.t0;
      var t1 = +seg.dataset.t1;
      var on = pos >= t0 - 0.15;

      seg.classList.toggle('on', on);

      if (!on) {
        seg.style.color = '';
        seg.style.textShadow = 'none';
      } else if (pos < t1) {
        seg.style.color = accent;
        seg.style.textShadow = '0 0 calc(18 * var(--s)) ' + accent;
      } else {
        seg.style.color = '#ffffff';
        seg.style.textShadow = 'none';
      }
    }
  }
'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "function buildTiltLine" not in t:
        t = t.replace("  function buildActiveChars(idx) {", js + "\n  function buildActiveChars(idx) {", 1)

    if "buildTiltLine(idx);" not in t:
        t = t.replace("  function buildActiveChars(idx) {\n    S.charSpans = [];",
                      "  function buildActiveChars(idx) {\n    S.charSpans = [];\n    if (S.lyricTheme === 'tilt') { buildTiltLine(idx); return; }", 1)

    if "paintTilt(S.position);" not in t:
        t = t.replace("    paintChars(S.position);",
                      "    if (S.lyricTheme === 'tilt') paintTilt(S.position);\n    else paintChars(S.position);", 1)

    old_themes = """  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
    new_themes = """  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
    if old_themes in t:
        t = t.replace(old_themes, new_themes)

    t = t.replace("document.body.classList.remove('theme-flow', 'theme-ink', 'theme-neon', 'theme-soft');",
                  "document.body.classList.remove('theme-flow', 'theme-tilt', 'theme-ink', 'theme-neon', 'theme-soft');")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".tilt-wrap" not in ct:
            ct += '''

/* ---------------- 倾诉（Tilt）排版 ---------------- */
.tilt-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: calc(6 * var(--s));
  line-height: 1.25;
  max-width: 86vw;
}

.tilt-seg {
  opacity: 0.16;
  transform: translateY(calc(10 * var(--s)));
  transition: opacity 0.5s var(--ease), transform 0.5s var(--ease), color 0.3s ease;
  font-size: calc(30 * var(--s));
  letter-spacing: 0.12em;
  color: var(--text);
  white-space: nowrap;
}

.tilt-seg.on {
  opacity: 1;
  transform: translateY(0);
}

.tilt-seg:not(.tilt) {
  font-size: calc(26 * var(--s));
  opacity: 0.45;
}

.tilt-seg.tilt {
  font-size: calc(64 * var(--s));
  font-style: italic;
  font-weight: 300;
  letter-spacing: 0.06em;
}

.tilt-seg.tilt .tc {
  display: inline-block;
  transition: transform 0.4s var(--ease);
}

.tilt-seg.tilt .tc.up { transform: translateY(calc(-12 * var(--s))); }
.tilt-seg.tilt .tc.down { transform: translateY(calc(12 * var(--s))); }

body.theme-tilt .line:not(.active) {
  opacity: 0.08;
  filter: blur(6px);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("js/app.js?v=39", "js/app.js?v=40")
        io.open(h, "w", encoding="utf-8", newline="").write(t)
