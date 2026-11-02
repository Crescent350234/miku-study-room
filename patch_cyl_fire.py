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

    if "cyl5-label-body" not in t:
        old = """      var txt = document.createElement('span');
      txt.className = 'cyl5-label-text';"""
        new = """      var body = document.createElement('div');
      body.className = 'cyl5-label-body';

      var txt = document.createElement('span');
      txt.className = 'cyl5-label-text';"""
        t = t.replace(old, new, 1)

        t = t.replace("      holder.appendChild(txt);", "      body.appendChild(txt);", 1)
        t = t.replace("        holder.appendChild(sb);", "        body.appendChild(sb);", 1)

        old2 = """      rotor.appendChild(holder);"""
        new2 = """      holder.appendChild(body);
      rotor.appendChild(holder);"""
        t = t.replace(old2, new2, 1)

    # 当前句体加动画
    t = t.replace(
        "      rotor.appendChild(holder);",
        "      if (li === idx) {\n        var d0 = 4;\n        if (S.lrc[idx + 1]) d0 = Math.max(2.8, Math.min(6, S.lrc[idx + 1].t - S.lrc[idx].t));\n        body.style.animationDuration = d0.toFixed(2) + 's';\n      }\n      rotor.appendChild(holder);",
        1,
    )

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v40" not in ct:
            ct += '''

/* 弹巢 v40：整句向右发射 */
.cyl5-label-body {
  display: inline-block;
  white-space: nowrap;
  animation-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1);
  animation-fill-mode: forwards;
}

.cyl5-label.current .cyl5-label-body {
  animation-name: cylRadialFire5;
}

@keyframes cylRadialFire5 {
  0%   { opacity: 1; transform: translateX(0); }
  60%  { opacity: 1; transform: translateX(0); }
  80%  { opacity: 1; transform: translateX(10vw); }
  100% { opacity: 0; transform: translateX(46vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=287", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
