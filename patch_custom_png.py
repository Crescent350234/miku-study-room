import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function autoCustomBg() {
    function pick(src) {
      for (var i = 0; i < BACKGROUNDS.length; i++) {
        if (!BACKGROUNDS[i].custom) continue;
        BACKGROUNDS[i].imageOnly = true;
        BACKGROUNDS[i].poster = src;
        bgIndex = i;
        applyBg(i);
        renderSceneChips();
        return;
      }
    }

    var jpg = new Image();
    jpg.onload = function () { pick('custom/bg.jpg'); };
    jpg.onerror = function () {
      var png = new Image();
      png.onload = function () { pick('custom/bg.png'); };
      png.src = 'custom/bg.png';
    };
    jpg.src = 'custom/bg.jpg';
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function autoCustomBg() {")
    end = t.find("  function applyBg(i) {", start)
    if start >= 0 and end > start:
        t = t[:start] + new_fn + t[end:]
    else:
        print("auto anchor miss", d)

    # bgStill 图片失败时，自定义场景尝试 png
    old_err = """  el.bg.addEventListener('error', function () {"""
    new_err = """  el.bgStill.addEventListener('error', function () {
    var item = BACKGROUNDS[bgIndex];
    if (item && item.custom && !item.triedPng) {
      item.triedPng = true;
      item.imageOnly = true;
      item.poster = 'custom/bg.png';
      el.bgStill.src = 'custom/bg.png';
    }
  });

  el.bg.addEventListener('error', function () {"""
    if "el.bgStill.addEventListener('error'" not in t:
        t = t.replace(old_err, new_err, 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=233", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
