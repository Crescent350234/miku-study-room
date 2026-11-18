import io, re

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

anchor = "  if (DESKTOP) {\n    setInterval(postDesktopRegions, 800);"
block = """  var desktopPlayerActive = false;
  var desktopProbeBusy = false;
  var desktopPlayerPort = 0;

  function probeDesktopPlayer(port) {
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, 500);
    return fetch('http://127.0.0.1:' + port + '/player-status', { cache: 'no-store', signal: controller.signal })
      .then(function (r) { return r.ok ? r.text() : ''; })
      .then(function (s) {
        if (s !== 'miku-player-1:active' && s !== 'miku-player-1:inactive') throw new Error('bad');
        return { port: port, active: s === 'miku-player-1:active' };
      })
      .finally(function () { clearTimeout(timer); });
  }

  function checkDesktopPlayer() {
    if (DESKTOP || desktopProbeBusy) return;
    desktopProbeBusy = true;
    var ports = [51802, 52802, 53802, 54802, 45802];
    var first = desktopPlayerPort ? probeDesktopPlayer(desktopPlayerPort) : Promise.reject(new Error('none'));
    first.catch(function () {
      return Promise.any(ports.map(function (p) { return probeDesktopPlayer(p); }));
    }).then(function (r) {
      desktopPlayerPort = r.port;
      if (desktopPlayerActive !== r.active) {
        desktopPlayerActive = r.active;
        document.body.classList.toggle('desktop-player-active', r.active);
      }
    }).catch(function () {
      desktopPlayerPort = 0;
      if (desktopPlayerActive) {
        desktopPlayerActive = false;
        document.body.classList.remove('desktop-player-active');
      }
    }).finally(function () { desktopProbeBusy = false; });
  }

  if (!DESKTOP) {
    checkDesktopPlayer();
    setInterval(checkDesktopPlayer, 2500);
  }

  if (DESKTOP) {
    setInterval(postDesktopRegions, 800);"""
if "desktopPlayerActive" not in t:
    t = t.replace(anchor, block, 1)
    print("presence added")
else:
    print("presence exists")

io.open(p, "w", encoding="utf-8", newline="").write(t)

h = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\index.html"
s = io.open(h, encoding="utf-8").read()
s = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=284", s)
io.open(h, "w", encoding="utf-8", newline="").write(s)

css = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\css\desktop-mode.css"
c = io.open(css, encoding="utf-8").read()
if "desktop-player-active" not in c:
    c += """

/* 独立播放器运行时，壁纸隐藏自己的胶囊和歌词，避免两套 UI */
body.desktop-player-active #player,
body.desktop-player-active .lyrics-area {
  display: none !important;
}
"""
    io.open(css, "w", encoding="utf-8", newline="").write(c)
    print("css added")
