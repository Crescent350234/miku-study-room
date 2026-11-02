import io, os, re

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

    t = t.replace("var line = 'rgba(214, 238, 232, 0.45)';", "var line = 'rgba(230, 230, 224, 0.78)';")
    t = t.replace("var faint = 'rgba(214, 238, 232, 0.16)';", "var faint = 'rgba(230, 230, 224, 0.30)';")
    t = t.replace("fill: 'rgba(8, 18, 20, 0.78)'", "fill: 'rgba(16, 18, 18, 0.62)'")
    t = t.replace("'rgba(214, 238, 232, 0.28)'", "'rgba(230, 230, 224, 0.45)'")
    t = t.replace("'rgba(214, 238, 232, 0.5)'", "'rgba(230, 230, 224, 0.7)'")
    t = t.replace("'rgba(220, 235, 245, 0.25)'", "'rgba(230, 230, 224, 0.3)'")

    if "cylHatch" not in t:
        anchor = "    // 内圈细线"
        hatch = '''    // 素描排线
    var clip = el('clipPath', { id: 'cylBodyClip' }, defs);
    el('path', { d: gear, fill: '#fff' }, clip);

    var hatch = el('g', { 'clip-path': 'url(#cylBodyClip)', mask: 'url(#cylHollow)' });
    for (var h = 0; h < 34; h++) {
      el('line', {
        x1: -80 + h * 15, y1: 0,
        x2: -80 + h * 15 + 520, y2: 600,
        stroke: 'rgba(228, 228, 220, 0.09)',
        'stroke-width': 1
      }, hatch);
    }

'''
        t = t.replace(anchor, hatch + anchor, 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=261", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
