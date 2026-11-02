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

    # 转轮旋转
    if "wheel.style.transform" not in t:
        anchor = """    scene.appendChild(list);
    layer.appendChild(scene);"""
        add = """    scene.appendChild(list);
    layer.appendChild(scene);

    // 转轮旋转：每句转一格
    var endAngle = -(idx * 60);
    wheel.style.transform = 'rotate(' + (endAngle - 60) + 'deg)';
    requestAnimationFrame(function () {
      wheel.style.transition = 'transform 0.62s cubic-bezier(0.18, 0.8, 0.22, 1)';
      wheel.style.transform = 'rotate(' + endAngle + 'deg)';
    });

    // 指针发射闪光
    if (list.firstChild) {
      pointer.style.animationDuration = list.firstChild.style.animationDuration || '4s';
    }"""
        t = t.replace(anchor, add, 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v27" not in ct:
            ct += '''

/* 弹巢 v27：转轮旋转 + 发射 */
.cyl5-wheel {
  transform-origin: 50% 50%;
  will-change: transform;
}

/* 当前句从转轮方向滑入 -> 停留 -> 向右发射 */
.cyl5-row.current {
  animation-name: cylRowFire2 !important;
}

@keyframes cylRowFire2 {
  0%   { opacity: 0; transform: rotate(-1.2deg) translateX(-16vw); }
  14%  { opacity: 1; transform: rotate(-1.2deg) translateX(0); }
  60%  { opacity: 1; transform: rotate(-1.2deg) translateX(0); }
  78%  { opacity: 1; transform: rotate(-1.2deg) translateX(8vw); }
  100% { opacity: 0; transform: rotate(-1.2deg) translateX(32vw); }
}

/* 指针闪光 */
.cyl5-pointer {
  animation-name: cylMuzzle;
  animation-timing-function: ease-out;
  animation-fill-mode: forwards;
  animation-duration: 4s;
  transform-origin: left center;
}

@keyframes cylMuzzle {
  0%, 58% { opacity: 0.25; box-shadow: none; }
  64%     { opacity: 1; box-shadow: 0 0 calc(14 * var(--s)) rgba(226, 232, 222, 0.8); }
  74%     { opacity: 0.15; box-shadow: none; }
  100%    { opacity: 0.2; box-shadow: none; }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=266", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
