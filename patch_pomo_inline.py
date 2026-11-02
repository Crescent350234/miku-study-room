import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

inline = r'''
  <script>
  (function () {
    var b = document.getElementById('pomo');
    var t = document.getElementById('pomoTime');
    if (!b || !t) return;
    window.__pomoInit = 1;

    var cfg = document.getElementById('pomoCfg');
    var fIn = document.getElementById('pomoFocus');
    var bIn = document.getElementById('pomoBreak');
    var m = 25, rem = 25 * 60, run = false, iv = null;
    try {
      var sm = parseInt(localStorage.getItem('pomoMin'), 10);
      if (sm > 0) m = sm;
    } catch (e) {}
    rem = m * 60;

    function fmt(s) {
      var mm = Math.floor(s / 60), ss = s % 60;
      return (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
    }
    function draw() { t.textContent = fmt(rem); }
    function tick() {
      if (!run) return;
      rem--;
      if (rem <= 0) {
        rem = 0; draw();
        run = false; clearInterval(iv);
        b.classList.remove('running');
        document.body.classList.remove('focus');
        return;
      }
      draw();
    }
    function stopAll() {
      run = false; clearInterval(iv);
      b.classList.remove('running');
      document.body.classList.remove('focus');
    }

    b.addEventListener('click', function () {
      if (run) { stopAll(); return; }
      if (rem <= 0) rem = m * 60;
      run = true;
      b.classList.add('running');
      document.body.classList.add('focus');
      clearInterval(iv);
      iv = setInterval(tick, 1000);
      draw();
    });

    b.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      if (fIn) fIn.value = m;
      if (bIn) bIn.value = (localStorage.getItem('pomoBreak') || 5);
      if (cfg) cfg.classList.add('open');
    });

    var save = document.getElementById('pomoSave');
    var cancel = document.getElementById('pomoCancel');
    if (cancel) cancel.addEventListener('click', function () { cfg.classList.remove('open'); });
    if (save) save.addEventListener('click', function () {
      var v = parseInt(fIn && fIn.value, 10);
      if (v > 0 && v <= 180) m = v;
      try { localStorage.setItem('pomoMin', String(m)); } catch (e) {}
      stopAll();
      rem = m * 60;
      draw();
      cfg.classList.remove('open');
    });

    draw();
  })();
  </script>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()
    if "__pomoInit" not in t:
        t = t.replace('  <div id="pomoCfg"', inline + '\n  <div id="pomoCfg"', 1)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
        print("html", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        jt = io.open(j, encoding="utf-8").read()
        old = "  (function initPomodoro() {\n"
        new = "  (function initPomodoro() {\n    if (window.__pomoInit) return;\n"
        if "window.__pomoInit" not in jt:
            jt = jt.replace(old, new, 1)
            io.open(j, "w", encoding="utf-8", newline="").write(jt)
            print("js", d)

    # 缓存控制
    if 'http-equiv="Cache-Control"' not in t:
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("<meta charset", '<meta http-equiv="Cache-Control" content="no-store"><meta charset', 1)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
