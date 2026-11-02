import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

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
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'bubble', name: '群唱' },
    { id: 'ink', name: '墨韵' },
    { id: 'neon', name: '霓虹' },
    { id: 'soft', name: '轻语' }
  ];"""

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if old_themes in t:
            t = t.replace(old_themes, new_themes)
        # no char spans in bubble mode
        t = t.replace("    if (S.lyricTheme === 'stack') { buildStackLine(idx); for (var sj = 0; sj < S.tiltSegs.length; sj++) S.tiltSegs[sj].classList.add('on'); return; }",
                      "    if (S.lyricTheme === 'stack') { buildStackLine(idx); for (var sj = 0; sj < S.tiltSegs.length; sj++) S.tiltSegs[sj].classList.add('on'); return; }\n    if (S.lyricTheme === 'bubble') return;")
        # recent class for previous 2 lines
        t = t.replace("      nodes[j].classList.toggle('far', Math.abs(j - idx) > 1);",
                      "      nodes[j].classList.toggle('far', Math.abs(j - idx) > 1);\n      nodes[j].classList.toggle('recent', j === idx - 1 || j === idx - 2);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "群唱（聊天气泡）" not in ct:
            ct += '''

/* ---------------- 群唱（聊天气泡） ---------------- */
body.theme-bubble .line {
  display: none;
}

body.theme-bubble .line.active,
body.theme-bubble .line.recent {
  display: block;
  width: fit-content;
  max-width: 62%;
  padding: calc(10 * var(--s)) calc(18 * var(--s));
  border-radius: calc(18 * var(--s));
  background: rgba(255, 255, 255, 0.09);
  color: rgba(255, 255, 255, 0.8);
  font-size: calc(26 * var(--s));
  line-height: 1.5;
  margin: calc(6 * var(--s)) auto;
  filter: none;
  opacity: 0.55;
  text-align: left;
  position: relative;
  box-shadow: 0 calc(8 * var(--s)) calc(24 * var(--s)) rgba(0, 0, 0, 0.25);
}

body.theme-bubble .line.active {
  background: var(--accent, #3cc5bb);
  color: #06110f;
  opacity: 1;
  font-size: calc(30 * var(--s));
  font-weight: 600;
}

body.theme-bubble .line:nth-child(odd) {
  margin-left: 6%;
}

body.theme-bubble .line:nth-child(even) {
  margin-left: auto;
  margin-right: 6%;
}

body.theme-bubble .line.recent::before,
body.theme-bubble .line.active::before {
  content: '';
  position: absolute;
  top: calc(-14 * var(--s));
  left: calc(14 * var(--s));
  width: calc(22 * var(--s));
  height: calc(22 * var(--s));
  border-radius: 50%;
  background: var(--pink, #ff9ecb);
  box-shadow: 0 0 0 calc(2 * var(--s)) rgba(8, 12, 14, 0.6);
}

body.theme-bubble .line:nth-child(even)::before {
  left: auto;
  right: calc(14 * var(--s));
  background: var(--accent, #3cc5bb);
}

body.theme-bubble .line .sub {
  font-size: 0.55em;
  color: rgba(0, 0, 0, 0.5);
  margin-top: calc(2 * var(--s));
}

body.theme-bubble .line.recent .sub {
  color: rgba(255, 255, 255, 0.5);
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=64", t)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
