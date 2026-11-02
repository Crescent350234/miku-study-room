import io

p = r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room\js\app.js"
t = io.open(p, encoding="utf-8").read()

snippet = '''
  window.__restartBridge = function () {
    var rb = document.getElementById('restartBridge');
    if (rb) { rb.disabled = true; rb.textContent = '重启中…'; }
    var base = (typeof BRIDGE !== 'undefined' && BRIDGE) ? BRIDGE : 'http://127.0.0.1:51789/';
    fetch(base + 'restart.all', { cache: 'no-store' })
      .catch(function () {
        return fetch('http://127.0.0.1:51790/restart', { cache: 'no-store' }).catch(function () {});
      })
      .then(function () {
        setTimeout(function () {
          if (rb) { rb.disabled = false; rb.textContent = '重启桥接'; }
        }, 4500);
      });
  };

'''

if "restart.all" not in t:
    idx = t.rfind("})();")
    t = t[:idx] + snippet + t[idx:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("app.js patched")
