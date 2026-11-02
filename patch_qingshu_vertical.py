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

    old = """    main.appendChild(wrap);

    if (line.sub) {"""
    new = """    var len = Math.max(1, Array.from(text).length);
    var fit = Math.min(1, 15 / len);
    wrap.style.setProperty('font-size', 'calc(' + (42 * fit).toFixed(1) + ' * var(--s))', 'important');

    main.appendChild(wrap);

    if (line.sub) {"""
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书 v6：竖排" not in ct:
            ct += '''

/* 青书 v6：竖排 + 左右浮动 */
body.theme-qingshu .line .main {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: calc(14 * var(--s));
}

body.theme-qingshu .qs-line {
  display: inline-block;
  writing-mode: vertical-rl;
  text-orientation: upright;
  white-space: nowrap;
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: calc(42 * var(--s));
  animation: qsDrift 18s ease-in-out infinite alternate;
}

body.theme-qingshu .qs-char {
  display: inline-block;
  white-space: pre;
  color: #cfece6;
  font-size: 1em;
  line-height: 1.08;
  letter-spacing: 0.12em;
  opacity: 0;
  filter: blur(5px);
  transform: translateY(6px);
  text-shadow: 0 0 calc(16 * var(--s)) rgba(150, 225, 220, 0.25);
  animation: qsIn 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

body.theme-qingshu .qs-sub {
  writing-mode: vertical-rl;
  text-orientation: upright;
  margin-top: 0;
  margin-left: calc(6 * var(--s));
  font-size: calc(20 * var(--s));
  letter-spacing: 0.08em;
  color: rgba(150, 205, 200, 0.7);
  font-family: "Noto Serif SC", "Songti SC", serif;
}

@keyframes qsDrift {
  from { transform: translateX(-4vw); }
  to { transform: translateX(4vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=171", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
