import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_js = '''    var syncCleanCover = function () {
      var c = $('cover');
      if (cleanCoverImg && c && c.src) cleanCoverImg.src = c.src;
    };'''

new_js = '''    var cleanCover = $('cleanCover');
    var syncCleanCover = function () {
      var c = $('cover');
      if (!c || !cleanCover) return;
      if (cleanCoverImg && c.src) cleanCoverImg.src = c.src;
      var r = c.getBoundingClientRect();
      cleanCover.style.left = r.left + 'px';
      cleanCover.style.top = r.top + 'px';
      cleanCover.style.width = r.width + 'px';
      cleanCover.style.height = r.height + 'px';
    };'''

old_css_start = "body.clean-wallpaper .clean-cover {\n  display: block;\n  position: fixed;\n  right: calc(46 * var(--s));\n  bottom: calc(46 * var(--s));\n  width: calc(210 * var(--s));\n  height: calc(210 * var(--s));\n  border-radius: calc(14 * var(--s));\n  overflow: hidden;\n  z-index: 60;\n  box-shadow: 0 calc(18 * var(--s)) calc(40 * var(--s)) rgba(0, 0, 0, 0.55);\n}"

new_css_start = "body.clean-wallpaper .clean-cover {\n  display: block;\n  position: fixed;\n  border-radius: calc(8 * var(--s));\n  overflow: hidden;\n  z-index: 60;\n  box-shadow: 0 calc(8 * var(--s)) calc(20 * var(--s)) rgba(0, 0, 0, 0.45);\n}"

old_eye = "  width: calc(30 * var(--s));\n  height: calc(30 * var(--s));"

new_eye = "  width: calc(20 * var(--s));\n  height: calc(20 * var(--s));"

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if os.path.exists(p):
        t = io.open(p, encoding="utf-8").read()
        if old_js in t:
            t = t.replace(old_js, new_js)
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            print("js", d)
        else:
            print("js miss", d)
        h = os.path.join(d, "index.html")
        if os.path.exists(h):
            ht = io.open(h, encoding="utf-8").read()
            ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=179", ht)
            io.open(h, "w", encoding="utf-8", newline="").write(ht)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if old_css_start in ct:
            ct = ct.replace(old_css_start, new_css_start)
        if old_eye in ct:
            ct = ct.replace(old_eye, new_eye, 1)
        io.open(c, "w", encoding="utf-8", newline="").write(ct)
        print("css", d)
