import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

block = r'''
  /* 独立初始化：引导与桥接重启，不依赖 start() */
  (function setupGuideAndRestart() {
    var mask = document.getElementById('onboardMask');
    var obBridge = document.getElementById('obBridge');
    var obAi = document.getElementById('obAi');
    var obRetry = document.getElementById('obRetry');
    var obAiOpen = document.getElementById('obAiOpen');
    var obDone = document.getElementById('obDone');

    function checkBridge() {
      if (!obBridge) return;
      obBridge.textContent = '检测中…';
      fetch(BRIDGE + 'now.json', { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.ok) { obBridge.textContent = '已连接 · ' + (d.title || ''); obBridge.className = 'ok'; }
          else { obBridge.textContent = '未连接'; obBridge.className = 'bad'; }
        })
        .catch(function () { obBridge.textContent = '未连接'; obBridge.className = 'bad'; });
    }

    function checkAi() {
      if (!obAi) return;
      fetch(BRIDGE + 'ai.config', { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.enabled) { obAi.textContent = '已启用 · ' + (d.model || ''); obAi.className = 'ok'; }
          else { obAi.textContent = '未配置（会用封面配色）'; obAi.className = 'bad'; }
        })
        .catch(function () { obAi.textContent = '未配置'; obAi.className = 'bad'; });
    }

    window.__openGuide = function () {
      if (!mask) return;
      mask.classList.add('open');
      checkBridge();
      checkAi();
    };

    window.__restartBridge = function () {
      var rb = document.getElementById('restartBridge');
      if (rb) { rb.disabled = true; rb.textContent = '重启中…'; }
      fetch('http://127.0.0.1:51790/restart', { cache: 'no-store' })
        .catch(function () {})
        .then(function () {
          setTimeout(function () {
            if (rb) { rb.disabled = false; rb.textContent = '重启桥接'; }
          }, 2600);
        });
    };

    if (obRetry) obRetry.addEventListener('click', checkBridge);
    if (obAiOpen) obAiOpen.addEventListener('click', function () {
      fetch(BRIDGE + 'ai.open', { cache: 'no-store' }).catch(function () {});
    });
    if (obDone) obDone.addEventListener('click', function () {
      mask.classList.remove('open');
      try { localStorage.setItem('onboarded', '1'); } catch (e) {}
    });

    var seen = false;
    try { seen = localStorage.getItem('onboarded') === '1'; } catch (e) {}
    if (!seen) setTimeout(window.__openGuide, 1500);
  })();

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if "setupGuideAndRestart" not in t:
        idx = t.rfind("})();")
        if idx < 0:
            print("tail miss", d)
            continue
        t = t[:idx] + block + t[idx:]
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=202", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
