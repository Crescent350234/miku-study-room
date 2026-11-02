import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    ht = io.open(h, encoding="utf-8").read()

    ht = ht.replace('<div class="clean-cover" id="cleanCover">',
                    '<div class="clean-cover" id="cleanCover" onclick="window.__exitClean && window.__exitClean()">')
    ht = ht.replace('<button class="clean-eye" id="cleanEye" aria-label="恢复界面" title="恢复界面">',
                    '<button class="clean-eye" id="cleanEye" aria-label="恢复界面" title="恢复界面" onclick="event.stopPropagation(); window.__exitClean && window.__exitClean()">')

    ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=226", ht)
    io.open(h, "w", encoding="utf-8", newline="").write(ht)
    print("html", d)

    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "window.__exitClean" not in t:
        t = t.replace("""      if (cleanEye) {
        cleanEye.addEventListener('click', function () {
          applyClean(false);
        });
      }""", """      window.__exitClean = function () { applyClean(false); };

      if (cleanEye) {
        cleanEye.addEventListener('click', function (e) {
          e.stopPropagation();
          applyClean(false);
        });
      }
      if (cleanCover) {
        cleanCover.addEventListener('click', function () { applyClean(false); });
      }""")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "恢复按钮加大" not in ct:
            ct += '''

/* 干净模式恢复按钮加大，防止点不中 */
body.clean-wallpaper .clean-eye {
  width: calc(28 * var(--s)) !important;
  height: calc(28 * var(--s)) !important;
  top: calc(4 * var(--s)) !important;
  right: calc(4 * var(--s)) !important;
  z-index: 2;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
