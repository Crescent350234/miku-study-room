import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    # 1) 自定义背景条目
    if "custom: true" not in t:
        t = t.replace("""    { src: 'assets/bg/1.webm', poster: 'assets/bg/1.jpg' }
  ];""", """    { src: 'assets/bg/1.webm', poster: 'assets/bg/1.jpg' },
    { src: 'custom/bg.webm', poster: 'custom/bg.jpg', custom: true }
  ];""")

    # 2) 芯片名称
    t = t.replace("b.textContent = '场景 ' + (idx + 1);", "b.textContent = BACKGROUNDS[idx].custom ? '自定义' : ('场景 ' + (idx + 1));")
    t = t.replace("toast('背景 · 场景 ' + (idx + 1));", "toast('背景 · ' + (BACKGROUNDS[idx].custom ? '自定义' : ('场景 ' + (idx + 1))));")

    # 3) applyBg 支持自定义：视频失败回退图片
    old_apply = """    el.bg.classList.remove('ready');
    clearTimeout(bgTimer);

    // 先显示静态帧，视频就绪后再淡入
    if (el.bgStill.src.indexOf(item.poster) === -1) {
      el.bgStill.src = item.poster;
    }

    bgTimer = setTimeout(function () {
      el.bg.poster = item.poster;
      el.bg.src = item.src;
      var p = el.bg.play();
      if (p && p.catch) p.catch(function () {});
    }, 260);"""

    new_apply = """    el.bg.classList.remove('ready');
    clearTimeout(bgTimer);

    if (item.imageOnly) {
      el.bg.pause();
      el.bg.removeAttribute('src');
      el.bg.load();
      el.bg.style.display = 'none';
      el.bgStill.style.display = 'block';
      el.bgStill.src = item.poster;
      return;
    }

    el.bg.style.display = '';
    el.bgStill.style.display = '';

    // 先显示静态帧，视频就绪后再淡入
    if (el.bgStill.src.indexOf(item.poster) === -1) {
      el.bgStill.src = item.poster;
    }

    bgTimer = setTimeout(function () {
      el.bg.poster = item.poster;
      el.bg.src = item.src;
      var p = el.bg.play();
      if (p && p.catch) p.catch(function () {});
    }, 260);"""

    if old_apply in t:
        t = t.replace(old_apply, new_apply)

    # 4) 视频加载失败：自定义模式先尝试图片
    old_err = """  el.bg.addEventListener('error', function () {
    el.bg.classList.remove('ready');
    bgFails++;
    if (bgFails < BACKGROUNDS.length) applyBg(bgIndex + 1);
  });"""

    new_err = """  el.bg.addEventListener('error', function () {
    el.bg.classList.remove('ready');
    var item = BACKGROUNDS[bgIndex];
    if (item && item.custom && !item.triedImage) {
      item.triedImage = true;
      item.imageOnly = true;
      applyBg(bgIndex);
      return;
    }
    bgFails++;
    if (bgFails < BACKGROUNDS.length) applyBg(bgIndex + 1);
  });"""

    if old_err in t:
        t = t.replace(old_err, new_err)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    # 5) custom 目录说明
    cd = os.path.join(d, "custom")
    os.makedirs(cd, exist_ok=True)
    readme = os.path.join(cd, "放这里.txt")
    if not os.path.exists(readme):
        io.open(readme, "w", encoding="utf-8", newline="").write(
            "把自己的背景放在这个文件夹：\n\n"
            "视频：bg.webm（必须是 VP9 编码的 WebM）\n"
            "封面/静态图：bg.jpg（或 bg.png）\n\n"
            "然后在壁纸设置 → 背景 → 选「自定义」。\n"
            "只放 bg.jpg 也可以，会用静态图当背景。\n"
        )
        print("custom readme", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=230", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
