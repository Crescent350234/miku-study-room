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

    t = t.replace(
        "if (idx < 0 || idx >= S.lrc.length) { layer.innerHTML = ''; return; }",
        "if (idx < 0 || idx >= S.lrc.length) { return; }",
    )

    if "__cylTest" not in t:
        anchor = "  function buildCylinderSvg() {"
        dbg = """  window.__cylTest = function (i) {
    try {
      buildCylinderLine(typeof i === 'number' ? i : Math.max(0, S.lrcIndex));
      return { idx: S.lrcIndex, len: S.lrc.length, kids: $('cylLayer') ? $('cylLayer').children.length : -1 };
    } catch (e) {
      return 'ERR ' + e.message + ' ' + (e.stack || '').slice(0, 200);
    }
  };

  function buildCylinderSvg() {"""
        t = t.replace(anchor, dbg, 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=269", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
