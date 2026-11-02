import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_block = """      var holder = document.createElement('div');
      holder.className = 'cyl5-label' + (li === idx ? ' current' : '');
      holder.style.transform =
        'rotate(' + slots[s].a + 'deg) translateY(calc(-0.313 * min(58vw, calc(920 * var(--s))))) rotate(-90deg)';

      var body = document.createElement('div');
      body.className = 'cyl5-label-body';

      var txt = document.createElement('span');
      txt.className = 'cyl5-label-text';
      txt.textContent = line.text;
      body.appendChild(txt);

      if (li === idx && line.sub) {
        var sb = document.createElement('span');
        sb.className = 'cyl5-label-sub';
        sb.textContent = line.sub;
        body.appendChild(sb);
      }

      if (li === idx) body.style.animationDuration = dur.toFixed(2) + 's';

      holder.appendChild(body);
      rotor.appendChild(holder);"""

old_start = "      var holder = document.createElement('div');"
old_end = "      rotor.appendChild(holder);"

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    i = t.find(old_start)
    j = t.find(old_end, i)
    if i < 0 or j < 0:
        print("anchor miss", d)
        continue
    t = t[:i] + new_block + t[j + len(old_end):]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v34" not in ct:
            ct += '''

/* 弹巢 v34：转到 3 点后当前句变色，翻译不变色 */
.cyl5-label-body {
  display: inline-block;
  white-space: nowrap;
  font-weight: 300;
  letter-spacing: 0.06em;
  animation-timing-function: cubic-bezier(0.2, 0.8, 0.2, 1);
  animation-fill-mode: forwards;
}

.cyl5-label-text {
  font-size: calc(15 * var(--s));
  color: rgba(228, 236, 232, 0.35);
}

.cyl5-label.current .cyl5-label-text {
  font-size: calc(42 * var(--s));
  color: #f7fbfa;
  animation: cylColorIn 0.35s ease 0.62s forwards;
}

.cyl5-label.current .cyl5-label-body {
  animation-name: cylRadialFire4;
}

.cyl5-label-sub {
  display: block;
  margin-top: calc(6 * var(--s));
  font-size: calc(16 * var(--s));
  color: rgba(200, 222, 216, 0.55);
}

@keyframes cylColorIn {
  from { color: #f7fbfa; }
  to   { color: #8ff0e2; }
}

@keyframes cylRadialFire4 {
  0%   { opacity: 1; transform: translateX(0); }
  60%  { opacity: 1; transform: translateX(0); }
  80%  { opacity: 1; transform: translateX(8vw); }
  100% { opacity: 0; transform: translateX(44vw); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=280", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
