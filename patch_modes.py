import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

js = r'''
  function buildScatterLine(idx) {
    S.charSpans = [];
    S.tiltSegs = [];
    S.scatterWords = [];

    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    var t0 = line.t;
    var t1 = S.lrc[idx + 1] ? S.lrc[idx + 1].t : t0 + Math.max(4, text.length * 0.35);
    var dur = Math.max(1.4, t1 - t0);
    var seed = Math.floor(t0 * 1000) + text.length;

    var units = text.split(/[，。！？、；：\s]+/).filter(function (s) { return s.trim().length > 0; });
    if (units.length < 3) {
      units = [];
      var chars = Array.from(text);
      for (var ci = 0; ci < chars.length; ci += 1) units.push(chars[ci]);
    }

    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#8ef';

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'scatter-wrap';

    var per = dur / Math.max(1, units.length);

    units.forEach(function (unit, i) {
      var elWord = document.createElement('span');
      elWord.className = 'sc-word';
      elWord.textContent = unit;

      var r1 = (Math.sin(seed + i * 7) * 10000) % 1;
      var r2 = (Math.sin(seed + i * 13) * 10000) % 1;
      var r3 = (Math.sin(seed + i * 19) * 10000) % 1;
      var r4 = (Math.sin(seed + i * 23) * 10000) % 1;
      r1 = Math.abs(r1); r2 = Math.abs(r2); r3 = Math.abs(r3); r4 = Math.abs(r4);

      var rot = (r1 - 0.5) * 36;
      var dx = (r2 - 0.5) * 70;
      var dy = (r3 - 0.5) * 46;
      var scale = 0.8 + r4 * 0.8;

      elWord.style.transform = 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px) rotate(' + rot.toFixed(1) + 'deg) scale(' + scale.toFixed(2) + ')';
      elWord.style.fontSize = (0.72 + r1 * 0.75).toFixed(2) + 'em';
      if (Math.abs(r4 - 0.5) > 0.3) elWord.style.color = S.charAccent;

      elWord.dataset.t0 = (t0 + i * per).toFixed(3);
      elWord.dataset.t1 = (t0 + (i + 1) * per).toFixed(3);

      wrap.appendChild(elWord);
      S.scatterWords.push(elWord);
    });

    main.appendChild(wrap);
  }

  function paintScatter(pos) {
    if (!S.scatterWords || !S.scatterWords.length) return;
    var accent = S.charAccent || '#8ef';

    for (var i = 0; i < S.scatterWords.length; i++) {
      var w = S.scatterWords[i];
      var t0 = +w.dataset.t0;
      var p = (pos - t0) / 0.6;
      if (p < 0) p = 0;
      else if (p > 1) p = 1;

      w.style.opacity = (0.12 + 0.88 * p).toFixed(3);
      if (pos < t0) w.style.textShadow = 'none';
      else if (pos < t0 + 1.2) w.style.textShadow = '0 0 calc(16 * var(--s)) ' + accent;
      else w.style.textShadow = 'none';
    }
  }

  function buildStackLine(idx) {
    S.charSpans = [];
    S.scatterWords = [];
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

    var parts = text.split(/[，。！？、；：]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length < 2) {
      var mid = Math.ceil(text.length / 2);
      parts = [text.slice(0, mid), text.slice(mid)];
    }
    parts = parts.slice(0, 3).filter(function (s) { return s.length > 0; });

    var seed = Math.floor(t0 * 1000);
    var bigIdx = seed % parts.length;

    S.charAccent = getComputedStyle(document.body).getPropertyValue('--accent').trim() || '#8ef';

    main.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.className = 'stack-wrap';

    var per = dur / parts.length;

    parts.forEach(function (part, i) {
      var seg = document.createElement('div');
      seg.className = 'stack-seg' + (i === bigIdx ? ' big' : '');
      seg.textContent = part;
      seg.dataset.t0 = (t0 + i * per).toFixed(3);
      seg.dataset.t1 = (t0 + (i + 1) * per).toFixed(3);
      wrap.appendChild(seg);
      S.tiltSegs.push(seg);
    });

    main.appendChild(wrap);
  }
'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    # restore normal theme loading if it was forced
    forced = """    var savedTheme = 'tilt';
"""
    normal = """    var savedTheme = 'flow';
    try { savedTheme = localStorage.getItem('lyricTheme') || 'flow'; } catch (e) {}
"""
    if forced in t:
        t = t.replace(forced, normal)

    if "function buildScatterLine" not in t:
        t = t.replace("  function buildActiveChars(idx) {", js + "\n  function buildActiveChars(idx) {", 1)

    t = t.replace("    if (S.lyricTheme === 'tilt') { buildTiltLine(idx); return; }",
                  "    if (S.lyricTheme === 'tilt') { buildTiltLine(idx); return; }\n    if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }\n    if (S.lyricTheme === 'stack') { buildStackLine(idx); return; }")

    t = t.replace("    if (S.lyricTheme === 'tilt') paintTilt(S.position);\n    else paintChars(S.position);",
                  "    if (S.lyricTheme === 'tilt' || S.lyricTheme === 'stack') paintTilt(S.position);\n    else if (S.lyricTheme === 'scatter') paintScatter(S.position);\n    else paintChars(S.position);")

    old_themes = """  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
    new_themes = """  var LYRIC_THEMES = [
    { id: 'flow', name: '流光' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""
    if old_themes in t:
        t = t.replace(old_themes, new_themes)

    t = t.replace("document.body.classList.remove('theme-flow', 'theme-tilt', 'theme-ink', 'theme-neon', 'theme-soft');",
                  "document.body.classList.remove('theme-flow', 'theme-scatter', 'theme-stack', 'theme-tilt', 'theme-ink', 'theme-neon', 'theme-soft');")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".scatter-wrap" not in ct:
            ct += '''

/* ---------------- 心象（散字） ---------------- */
.scatter-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: calc(4 * var(--s)) calc(10 * var(--s));
  max-width: 82vw;
  min-height: 34vh;
  padding: calc(10 * var(--s));
}

.sc-word {
  display: inline-block;
  font-size: 1em;
  color: #ffffff;
  opacity: 0.12;
  transition: opacity 0.5s var(--ease), color 0.3s ease, text-shadow 0.3s ease;
  will-change: transform;
}

body.theme-scatter .line.active {
  font-size: calc(46 * var(--s));
  letter-spacing: 0;
}

body.theme-scatter .line:not(.active) {
  opacity: 0.08;
  filter: blur(6px);
}

/* ---------------- 云阶（叠字大字） ---------------- */
.stack-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: calc(4 * var(--s));
  line-height: 1.15;
  max-width: 86vw;
}

.stack-seg {
  opacity: 0.14;
  transform: translateY(calc(8 * var(--s)));
  transition: opacity 0.5s var(--ease), transform 0.5s var(--ease), color 0.3s ease;
  font-size: calc(30 * var(--s));
  letter-spacing: 0.06em;
  color: #ffffff;
  white-space: nowrap;
}

.stack-seg.on {
  opacity: 1;
  transform: translateY(0);
}

.stack-seg.big {
  font-size: calc(82 * var(--s));
  font-weight: 700;
  letter-spacing: 0.02em;
}

body.theme-stack .line:not(.active) {
  opacity: 0.06;
  filter: blur(7px);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("js/app.js?v=41", "js/app.js?v=42")
        io.open(h, "w", encoding="utf-8", newline="").write(t)
