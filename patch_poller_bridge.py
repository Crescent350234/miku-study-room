import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

script = r'''
  <script>
  (function () {
    var ports = [51789, 52789, 53789, 54789];
    var idx = 0;
    var port = null;
    function poll() {
      var p = port || ports[idx % ports.length];
      fetch('http://127.0.0.1:' + p + '/pomo.json?t=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { if (!r.ok) throw new Error('bad'); port = p; return r.json(); })
        .then(function (s) { document.body.classList.toggle('focus', !!s.focus); })
        .catch(function () { if (!port) idx++; });
    }
    setInterval(poll, 1000);
    poll();
  })();
  </script>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()

    if "127.0.0.1:' + p + '/pomo.json" not in t:
        t = t.replace("</body>", script + "\n</body>", 1)

    t = re.sub(r'href="css/style\.css(\?v=\d+)?"', 'href="css/style.css?v=292"', t)
    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)
