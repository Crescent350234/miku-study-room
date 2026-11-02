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

    old = """    var endAngle = (idx * 60);
    wheel.style.transform = 'rotate(' + (endAngle + 60) + 'deg)';
    requestAnimationFrame(function () {
      wheel.style.transition = 'transform 0.62s cubic-bezier(0.18, 0.8, 0.22, 1)';
      wheel.style.transform = 'rotate(' + endAngle + 'deg)';
    });"""
    new = """    var endAngle = (idx * 60);
    var svgEl = wheel.querySelector('.cyl5-svg');
    if (svgEl) {
      svgEl.style.transform = 'rotate(' + (endAngle + 60) + 'deg)';
      requestAnimationFrame(function () {
        svgEl.style.transition = 'transform 0.62s cubic-bezier(0.18, 0.8, 0.22, 1)';
        svgEl.style.transform = 'rotate(' + endAngle + 'deg)';
      });
    }"""
    if old in t:
        t = t.replace(old, new)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v30" not in ct:
            ct += '''

/* 弹巢 v30：只旋转 SVG，歌词位置固定 */
.cyl5-svg {
  transform-origin: 50% 50%;
  will-change: transform;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=272", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
