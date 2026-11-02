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

    ht = ht.replace('<button class="ctl" id="guideBtn2" aria-label="使用引导" title="使用引导">',
                    '<button class="ctl" id="guideBtn2" aria-label="使用引导" title="使用引导" onclick="window.__openGuide && window.__openGuide()">')
    ht = ht.replace('<button class="style-chip" id="openGuide">使用引导</button>',
                    '<button class="style-chip" id="openGuide" onclick="window.__openGuide && window.__openGuide()">使用引导</button>')
    ht = ht.replace('<button class="style-chip" id="restartBridge">重启桥接</button>',
                    '<button class="style-chip" id="restartBridge" onclick="window.__restartBridge && window.__restartBridge()">重启桥接</button>')

    ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=201", ht)
    io.open(h, "w", encoding="utf-8", newline="").write(ht)
    print("html", d)

    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "window.__openGuide =" not in t:
        t = t.replace("    function openMask() {", "    function openMask() {")

    t = t.replace("""    if (guideBtn2) guideBtn2.addEventListener('click', openMask);""",
                  """    if (guideBtn2) guideBtn2.addEventListener('click', openMask);
    window.__openGuide = openMask;""")

    t = t.replace("""    var restartBridgeBtn = document.getElementById('restartBridge');""",
                  """    window.__restartBridge = function () {
      var rb = document.getElementById('restartBridge');
      if (!rb) return;
      rb.disabled = true;
      rb.textContent = '重启中…';
      fetch('http://127.0.0.1:51790/restart', { cache: 'no-store' })
        .catch(function () {})
        .then(function () {
          setTimeout(function () { rb.disabled = false; rb.textContent = '重启桥接'; }, 2600);
        });
    };

    var restartBridgeBtn = document.getElementById('restartBridge');""")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)
