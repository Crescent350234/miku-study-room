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

    var wrap = document.createElement('div');
    wrap.className = 'qs-line';

    Array.from(text).forEach(function (ch, i) {
      var sp = document.createElement('span');
      sp.className = 'qs-char';
      sp.textContent = ch === ' ' ? '\u00a0' : ch;
      sp.style.animationDelay = (i * 0.04).toFixed(2) + 's';
      wrap.appendChild(sp);
    });

    main.appendChild(wrap);

    if (line.sub) {
      var sub = document.createElement('div');
      sub.className = 'qs-sub';
      sub.textContent = line.sub;
      main.appendChild(sub);
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
        if "青书 v5：左到右浮动" not in ct:
            ct += '''

/* 青书 v5：一句话，从左往右缓慢浮动 */
body.theme-qingshu .line .main {
  display: inline-block;
  animation: none !important;
}

body.theme-qingshu .line:not(.active) {
  opacity: 0 !important;
}

body.theme-qingshu .qs-line {
  display: inline-block;
  white-space: nowrap;
  font-family: "Noto Serif SC", "Source Han Serif SC", "Songti SC", serif;
  animation: qsDrift 16s ease-in-out infinite alternate;
}

body.theme-qingshu .qs-char {
  display: inline-block;
  white-space: pre;
  color: #cfece6;
  font-size: calc(42 * var(--s));
  line-height: 1.4;
  letter-spacing: 0.14em;
  opacity: 0;
  filter: blur(5px);
  transform: translateY(6px);
  text-shadow: 0 0 calc(16 * var(--s)) rgba(150, 225, 220, 0.25);
  animation: qsIn 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

body.theme-qingshu .qs-sub {
  margin-top: calc(10 * var(--s));
  font-size: calc(18 * var(--s));
  letter-spacing: 0.1em;
  color: rgba(150, 205, 200, 0.7);
  font-family: "Noto Serif SC", "Songti SC", serif;
}

@keyframes qsDrift {
  from { transform: translateX(-4vw); }
  to { transform: translateX(4vw); }
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
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=170", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
