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

    var scroll = document.createElement('div');
    scroll.className = 'qs-scroll';

    var textCol = document.createElement('div');
    textCol.className = 'qs-text';

    Array.from(text).forEach(function (ch, i) {
      var sp = document.createElement('span');
      sp.className = 'qs-char';
      sp.textContent = ch === ' ' ? '\u00a0' : ch;
      sp.style.animationDelay = (i * 0.045).toFixed(2) + 's';
      textCol.appendChild(sp);
    });

    scroll.appendChild(textCol);

    if (line.sub) {
      var subCol = document.createElement('div');
      subCol.className = 'qs-text qs-sub-text';
      Array.from(line.sub).forEach(function (ch) {
        var sp = document.createElement('span');
        sp.className = 'qs-sub-char';
        sp.textContent = ch === ' ' ? '\u00a0' : ch;
        subCol.appendChild(sp);
      });
      scroll.appendChild(subCol);
    }

    main.appendChild(scroll);
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
        if "青书 v3：卷轴" not in ct:
            ct += '''

/* 青书 v3：铺开卷轴 */
body.theme-qingshu .line .main {
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

body.theme-qingshu .line:not(.active) {
  opacity: 0 !important;
}

body.theme-qingshu .qs-scroll {
  position: relative;
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
  gap: calc(18 * var(--s));
  padding: calc(30 * var(--s)) calc(64 * var(--s));
  border-radius: calc(4 * var(--s));
  background:
    radial-gradient(120% 90% at 50% 0%, rgba(120, 170, 150, 0.10), transparent 70%),
    linear-gradient(180deg, #1f3029, #273b31 45%, #1c2c25);
  box-shadow:
    inset 0 0 calc(60 * var(--s)) rgba(0, 0, 0, 0.55),
    0 calc(16 * var(--s)) calc(40 * var(--s)) rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(170, 200, 175, 0.18);
  clip-path: inset(0 0 0 0);
  animation: qsUnroll 0.85s cubic-bezier(0.22, 0.8, 0.2, 1) both;
}

body.theme-qingshu .qs-scroll::before,
body.theme-qingshu .qs-scroll::after {
  content: '';
  position: absolute;
  top: calc(-12 * var(--s));
  bottom: calc(-12 * var(--s));
  width: calc(18 * var(--s));
  border-radius: calc(9 * var(--s));
  background: linear-gradient(90deg, #14201b, #35503f 40%, #1a2a22 70%, #0f1713);
  box-shadow: 0 calc(4 * var(--s)) calc(14 * var(--s)) rgba(0, 0, 0, 0.55);
}

body.theme-qingshu .qs-scroll::before { left: calc(-10 * var(--s)); }
body.theme-qingshu .qs-scroll::after { right: calc(-10 * var(--s)); }

body.theme-qingshu .qs-text {
  writing-mode: vertical-rl;
  text-orientation: upright;
  display: inline-block;
  text-align: center;
}

body.theme-qingshu .qs-sub-text {
  opacity: 0.6;
  margin-top: calc(8 * var(--s));
}

body.theme-qingshu .qs-char {
  color: #e8efd8;
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: calc(42 * var(--s));
  line-height: 1.08;
  letter-spacing: 0.12em;
  opacity: 0;
  filter: blur(5px);
  transform: translateY(5px);
  text-shadow: 0 0 calc(14 * var(--s)) rgba(220, 235, 200, 0.18);
  animation: qsIn 0.75s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

body.theme-qingshu .qs-sub-char {
  color: rgba(190, 215, 185, 0.75);
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: calc(20 * var(--s));
  line-height: 1.15;
  letter-spacing: 0.08em;
}

@keyframes qsUnroll {
  from { clip-path: inset(0 49% 0 49%); opacity: 0.4; }
  to { clip-path: inset(0 0 0 0); opacity: 1; }
}

@keyframes qsIn {
  to { opacity: 1; filter: blur(0); transform: translateY(0); }
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=167", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
