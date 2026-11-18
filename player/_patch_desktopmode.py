import io, re

h = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\index.html"
s = io.open(h, encoding="utf-8").read()
if "desktop-mode.css" not in s:
    s = s.replace('<link rel="stylesheet" href="css/v5.css?v=4">',
                  '<link rel="stylesheet" href="css/v5.css?v=4">\n<link rel="stylesheet" href="css/desktop-mode.css?v=1">')
s = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=283", s)
io.open(h, "w", encoding="utf-8", newline="").write(s)
print("html patched")

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()
anchor = "  var BRIDGE = 'http://127.0.0.1:51789/';\n"
block = """  var BRIDGE = 'http://127.0.0.1:51789/';
  var DESKTOP = params.has('desktop') && !!(window.chrome && window.chrome.webview);
  if (DESKTOP) document.documentElement.classList.add('desktop-mode');

  function postDesktopRegions() {
    if (!DESKTOP) return;
    try {
      var rects = [];
      ['player', 'lyricsViewport'].forEach(function (id) {
        var node = $(id);
        if (!node) return;
        var r = node.getBoundingClientRect();
        if (r.width > 8 && r.height > 8) {
          rects.push({ x: r.left, y: r.top, w: r.width, h: r.height });
        }
      });
      window.chrome.webview.postMessage(JSON.stringify({
        kind: 'regions', width: window.innerWidth, height: window.innerHeight, rects: rects
      }));
    } catch (e) {}
  }

  if (DESKTOP) {
    setInterval(postDesktopRegions, 800);
    window.addEventListener('resize', postDesktopRegions);
    setTimeout(postDesktopRegions, 1200);
  }
"""
if "postDesktopRegions" not in t:
    t = t.replace(anchor, block, 1)
    print("desktop block added")
else:
    print("desktop block exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)
