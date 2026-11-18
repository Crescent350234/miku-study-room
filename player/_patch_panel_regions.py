import io, re

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

old = """      var rects = [];
      ['player', 'lyricsViewport'].forEach(function (id) {
        var node = $(id);
        if (!node) return;
        var r = node.getBoundingClientRect();
        if (r.width > 8 && r.height > 8) {
          rects.push({ x: r.left, y: r.top, w: r.width, h: r.height });
        }
      });"""
new = """      var rects = [];
      ['player', 'lyricsViewport'].forEach(function (id) {
        var node = $(id);
        if (!node) return;
        var r = node.getBoundingClientRect();
        if (r.width > 8 && r.height > 8) {
          rects.push({ x: r.left, y: r.top, w: r.width, h: r.height });
        }
      });
      ['settingsPanel', 'drawer'].forEach(function (id) {
        var node = $(id);
        if (!node || !node.classList.contains('open')) return;
        var r = node.getBoundingClientRect();
        if (r.width > 8 && r.height > 8) {
          rects.push({ x: r.left, y: r.top, w: r.width, h: r.height });
        }
      });"""

if "settingsPanel', 'drawer" not in t:
    t = t.replace(old, new, 1)
    print("panel regions added")
else:
    print("already added")

io.open(p, "w", encoding="utf-8", newline="").write(t)

h = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\index.html"
s = io.open(h, encoding="utf-8").read()
s = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=285", s)
io.open(h, "w", encoding="utf-8", newline="").write(s)
print("bumped")
