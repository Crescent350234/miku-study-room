import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    # only layout modes build spans; plain keeps whole line
    old = """  function buildActiveChars(idx) {
    S.charSpans = [];
    if (S.lyricTheme === 'tilt') { buildTiltLine(idx); return; }
    if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }
    if (S.lyricTheme === 'stack') { buildStackLine(idx); return; }"""
    new = """  function buildActiveChars(idx) {
    S.charSpans = [];
    if (S.lyricTheme === 'tilt') { buildTiltLine(idx); return; }
    if (S.lyricTheme === 'scatter') { buildScatterLine(idx); return; }
    if (S.lyricTheme === 'stack') { buildStackLine(idx); return; }
    return;"""
    if old in t:
        t = t.replace(old, new)

    # stop per-frame painting
    t = t.replace("    if (S.lyricTheme === 'tilt' || S.lyricTheme === 'stack') paintTilt(S.position);\n    else if (S.lyricTheme === 'scatter') paintScatter(S.position);\n    else paintChars(S.position);\n", "")

    # scatter: fully visible once built
    t = t.replace("    main.appendChild(wrap);\n  }\n\n  function paintScatter", "    main.appendChild(wrap);\n    for (var wi = 0; wi < S.scatterWords.length; wi++) S.scatterWords[wi].style.opacity = '1';\n  }\n\n  function paintScatter")

    # stack/tilt: mark all segments on when built
    t = t.replace("    main.appendChild(wrap);\n  }\n\n  function buildScatterLine", "    main.appendChild(wrap);\n    for (var si = 0; si < S.tiltSegs.length; si++) S.tiltSegs[si].classList.add('on');\n  }\n\n  function buildScatterLine")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".line.active .sc-word" not in ct:
            ct += '''

/* 当前行整体高亮：不逐字渐亮 */
.line.active .sc-word { opacity: 1 !important; }
.line.active .tilt-seg.on,
.line.active .stack-seg.on { opacity: 1 !important; }
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=49", t)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
