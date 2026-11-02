import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

poller = r'''
  <script>
  (function () {
    function poll() {
      fetch('pomo.json?t=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (s) {
          if (!s) return;
          document.body.classList.toggle('focus', !!s.focus);
        })
        .catch(function () {});
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
    if "pomo.json?t=" not in t:
        t = t.replace("</body>", poller + "\n</body>", 1)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
        print("html", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "番茄钟 w2" not in ct:
            ct += '''

/* 番茄钟 w2：网页内只做专注态，倒计时交给独立小窗 */
#pomo,
#pomoCfg,
#pomoSettingsBtn {
  display: none !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        jt = io.open(j, encoding="utf-8").read()
        jt = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=292", jt)
        io.open(j, "w", encoding="utf-8", newline="").write(jt)

# bump html version
for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=292", t)
        io.open(h, "w", encoding="utf-8", newline="").write(t)
