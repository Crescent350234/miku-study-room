import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildQingshuLine(idx) {
    var nodes = el.lyrics.children;
    if (idx < 0 || idx >= nodes.length) return;

    var main = nodes[idx].querySelector('.main');
    if (!main) return;

    var line = S.lrc[idx];
    var text = line.text || '';
    main.innerHTML = '';

    var slip = document.createElement('div');
    slip.className = 'qs-slip';

    Array.from(text).forEach(function (ch, i) {
      var sp = document.createElement('span');
      sp.className = 'qs-char';
      sp.textContent = ch === ' ' ? '\u00a0' : ch;
      sp.style.animationDelay = (i * 0.045).toFixed(2) + 's';
      slip.appendChild(sp);
    });

    main.appendChild(slip);

    if (line.sub) {
      var subSlip = document.createElement('div');
      subSlip.className = 'qs-slip qs-sub-slip';
      Array.from(line.sub).forEach(function (ch) {
        var sp = document.createElement('span');
        sp.className = 'qs-sub-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        subSlip.appendChild(sp);
      });
      main.appendChild(subSlip);
    }
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildQingshuLine(idx) {")
    nxt = t.find("\n  function ", start + 10)
    if start < 0 or nxt < 0:
        print("anchor miss", d)
        continue

    t = t[:start] + new_fn + t[nxt + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "青书 v2：竹简" not in ct:
            ct += '''

/* 青书 v2：竹简 */
body.theme-qingshu .line .main {
  display: inline-flex;
  align-items: flex-start;
  gap: calc(14 * var(--s));
}

body.theme-qingshu .line:not(.active) {
  opacity: 0 !important;
}

body.theme-qingshu .qs-slip {
  position: relative;
  display: inline-block;
  writing-mode: vertical-rl;
  text-orientation: upright;
  padding: calc(22 * var(--s)) calc(16 * var(--s));
  border-radius: calc(6 * var(--s));
  border: 1px solid rgba(196, 214, 170, 0.28);
  background:
    repeating-linear-gradient(180deg, transparent 0 calc(78 * var(--s)), rgba(0, 0, 0, 0.18) calc(78 * var(--s)) calc(80 * var(--s))),
    linear-gradient(90deg, #26382c, #3a5340 35%, #40593f 55%, #2a3d2e);
  box-shadow: inset 0 0 calc(34 * var(--s)) rgba(0, 0, 0, 0.55), 0 calc(12 * var(--s)) calc(30 * var(--s)) rgba(0, 0, 0, 0.45);
}

body.theme-qingshu .qs-slip::before,
body.theme-qingshu .qs-slip::after {
  content: '';
  position: absolute;
  left: 6%;
  right: 6%;
  height: 2px;
  background: linear-gradient(90deg, rgba(190, 170, 120, 0.6), rgba(120, 100, 60, 0.3));
}

body.theme-qingshu .qs-slip::before { top: calc(8 * var(--s)); }
body.theme-qingshu .qs-slip::after { bottom: calc(8 * var(--s)); }

body.theme-qingshu .qs-char {
  display: inline-block;
  white-space: pre;
  color: #e6edd2;
  opacity: 0;
  filter: blur(5px);
  transform: translateY(6px);
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: calc(40 * var(--s));
  line-height: 1.05;
  letter-spacing: 0.12em;
  text-shadow: 0 0 calc(14 * var(--s)) rgba(220, 235, 200, 0.2);
  animation: qsIn 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

body.theme-qingshu .qs-sub-slip {
  padding: calc(16 * var(--s)) calc(10 * var(--s));
  background:
    repeating-linear-gradient(180deg, transparent 0 calc(56 * var(--s)), rgba(0, 0, 0, 0.16) calc(56 * var(--s)) calc(58 * var(--s))),
    linear-gradient(90deg, #2a3a30, #35493a);
  opacity: 0.75;
}

body.theme-qingshu .qs-sub-char {
  display: inline-block;
  white-space: pre;
  color: rgba(200, 220, 190, 0.75);
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: calc(20 * var(--s));
  line-height: 1.15;
  letter-spacing: 0.08em;
}

@keyframes qsIn {
  to {
    opacity: 1;
    filter: blur(0);
    transform: translateY(0);
  }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=166", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
