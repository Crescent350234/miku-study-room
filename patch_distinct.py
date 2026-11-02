import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_themes = """  var LYRIC_THEMES = [
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

new_themes = """  var LYRIC_THEMES = [
    { id: 'plain', name: '简洁' },
    { id: 'fume', name: '浮名' },
    { id: 'lumiere', name: '流光' },
    { id: 'scatter', name: '心象' },
    { id: 'stack', name: '云阶' },
    { id: 'tilt', name: '倾诉' },
    { id: 'hanabi', name: '花火' }
  ];"""

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if old_themes in t:
            t = t.replace(old_themes, new_themes)
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "每个模式的专属动效" not in ct:
            ct += '''

/* ---------------- 每个模式的专属动效 ---------------- */
@keyframes scDrift {
  from { translate: 0 0; }
  to   { translate: 0 -10px; }
}

@keyframes stackPulse {
  0%, 100% { scale: 1; }
  50%      { scale: 1.045; }
}

@keyframes fumeSlideA {
  from { translate: -6px 0; }
  to   { translate: 6px 0; }
}

@keyframes fumeSlideB {
  from { translate: 8px 0; }
  to   { translate: -8px 0; }
}

@keyframes tiltBob {
  0%, 100% { translate: 0 0; }
  50%      { translate: 0 -5px; }
}

@keyframes lumiSweep {
  from { transform: translateX(-22%); opacity: 0.35; }
  to   { transform: translateX(22%); opacity: 0.8; }
}

@keyframes plainBreath {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.88; }
}

/* 心象：散字缓慢浮动 */
body.theme-scatter .sc-word {
  animation: scDrift 5.2s ease-in-out infinite alternate;
}
body.theme-scatter .sc-word:nth-child(2n) { animation-duration: 6.4s; }
body.theme-scatter .sc-word:nth-child(3n) { animation-duration: 7.2s; }

/* 云阶：大字呼吸 */
body.theme-stack .stack-seg.big {
  animation: stackPulse 3.6s ease-in-out infinite;
  transform-origin: center center;
}

/* 浮名：三行反向漂移 */
body.theme-fume .fume-row.r0 { animation: fumeSlideA 7s ease-in-out infinite alternate; }
body.theme-fume .fume-row.r1 { animation: fumeSlideB 9s ease-in-out infinite alternate; }
body.theme-fume .fume-row.r2 { animation: fumeSlideA 11s ease-in-out infinite alternate; }

/* 倾诉：斜体字上下浮动 */
body.theme-tilt .tilt-seg.tilt .tc {
  animation: tiltBob 3.4s ease-in-out infinite;
}
body.theme-tilt .tilt-seg.tilt .tc:nth-child(2n) { animation-duration: 4.2s; }

/* 流光：光带左右扫动 */
body.theme-lumiere .lumi-line::before {
  animation: lumiSweep 4.5s ease-in-out infinite alternate;
}

/* 简洁：整行轻微呼吸 */
body.theme-plain .line.active {
  animation: plainBreath 6s ease-in-out infinite;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=80", t)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
