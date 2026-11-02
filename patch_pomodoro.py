import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

pomo_html = """

  <div id="pomo" class="pomo" title="左键开始 / 暂停 · 右键设置">
    <span class="pomo-dot"></span>
    <span id="pomoTime" class="pomo-time">25:00</span>
    <span class="pomo-tag">专注</span>
  </div>

  <div id="pomoCfg" class="pomo-cfg">
    <label>专注（分钟）<input id="pomoFocus" type="number" min="1" max="180" value="25"></label>
    <label>休息（分钟）<input id="pomoBreak" type="number" min="1" max="60" value="5"></label>
    <div class="pomo-cfg-actions">
      <button id="pomoCancel">取消</button>
      <button id="pomoSave">保存</button>
    </div>
  </div>
"""

pomo_js = r'''
  (function initPomodoro() {
    var box = document.getElementById('pomo');
    var timeEl = document.getElementById('pomoTime');
    if (!box || !timeEl) return;

    var cfg = document.getElementById('pomoCfg');
    var inpFocus = document.getElementById('pomoFocus');
    var inpBreak = document.getElementById('pomoBreak');
    var btnSave = document.getElementById('pomoSave');
    var btnCancel = document.getElementById('pomoCancel');

    var state = { min: 25, breakMin: 5, remain: 25 * 60, running: false, timer: null };
    try {
      var m = parseInt(localStorage.getItem('pomoMin'), 10);
      if (m > 0 && m <= 180) state.min = m;
      var b = parseInt(localStorage.getItem('pomoBreak'), 10);
      if (b > 0 && b <= 60) state.breakMin = b;
    } catch (e) {}
    state.remain = state.min * 60;

    function fmt(sec) {
      var mm = Math.floor(sec / 60);
      var ss = sec % 60;
      return (mm < 10 ? '0' : '') + mm + ':' + (ss < 10 ? '0' : '') + ss;
    }

    function render() {
      timeEl.textContent = fmt(state.remain);
    }

    function tick() {
      if (!state.running) return;
      state.remain--;
      if (state.remain <= 0) {
        state.remain = 0;
        render();
        stop(true);
        if (typeof toast === 'function') toast('专注结束，休息一下');
        return;
      }
      render();
    }

    function start() {
      if (state.remain <= 0) state.remain = state.min * 60;
      state.running = true;
      document.body.classList.add('focus');
      box.classList.add('running');
      clearInterval(state.timer);
      state.timer = setInterval(tick, 1000);
      render();
    }

    function stop(exitFocus) {
      state.running = false;
      clearInterval(state.timer);
      box.classList.remove('running');
      if (exitFocus !== false) document.body.classList.remove('focus');
    }

    box.addEventListener('click', function () {
      if (state.running) stop(true);
      else start();
    });

    box.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      inpFocus.value = state.min;
      inpBreak.value = state.breakMin;
      cfg.classList.add('open');
    });

    if (btnCancel) btnCancel.addEventListener('click', function () {
      cfg.classList.remove('open');
    });

    if (btnSave) btnSave.addEventListener('click', function () {
      var f = parseInt(inpFocus.value, 10);
      var b = parseInt(inpBreak.value, 10);
      if (!(f > 0 && f <= 180)) f = 25;
      if (!(b > 0 && b <= 60)) b = 5;
      state.min = f;
      state.breakMin = b;
      try {
        localStorage.setItem('pomoMin', String(f));
        localStorage.setItem('pomoBreak', String(b));
      } catch (e) {}
      stop(true);
      state.remain = f * 60;
      render();
      cfg.classList.remove('open');
    });

    render();
  })();

'''

pomo_css = '''

/* ---------------- 番茄钟 / 专注模式 ---------------- */
.pomo {
  position: fixed;
  left: 50%;
  bottom: calc(214 * var(--s));
  transform: translateX(-50%);
  z-index: 8;
  display: flex;
  align-items: center;
  gap: calc(12 * var(--s));
  padding: calc(10 * var(--s)) calc(20 * var(--s));
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: var(--glass);
  backdrop-filter: blur(20px) saturate(1.2);
  box-shadow: 0 calc(12 * var(--s)) calc(40 * var(--s)) rgba(0, 0, 0, 0.35);
  color: #eef7f4;
  font-size: calc(18 * var(--s));
  letter-spacing: 0.06em;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.pomo:hover { opacity: 1; }

.pomo-dot {
  width: calc(8 * var(--s));
  height: calc(8 * var(--s));
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
}

.pomo.running .pomo-dot {
  background: #8ff0e2;
  box-shadow: 0 0 calc(12 * var(--s)) rgba(143, 240, 226, 0.8);
}

.pomo-time {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: calc(20 * var(--s));
}

.pomo-tag {
  color: rgba(200, 222, 216, 0.55);
  font-size: calc(13 * var(--s));
}

.pomo.running .pomo-tag { color: #8ff0e2; }

.pomo-cfg {
  position: fixed;
  left: 50%;
  bottom: calc(280 * var(--s));
  transform: translateX(-50%);
  z-index: 9;
  display: none;
  flex-direction: column;
  gap: calc(12 * var(--s));
  padding: calc(18 * var(--s)) calc(22 * var(--s));
  border-radius: calc(18 * var(--s));
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(12, 24, 22, 0.92);
  backdrop-filter: blur(18px);
  color: #eaf4f1;
  font-size: calc(14 * var(--s));
}

.pomo-cfg.open { display: flex; }

.pomo-cfg label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: calc(12 * var(--s));
}

.pomo-cfg input {
  width: calc(72 * var(--s));
  padding: calc(4 * var(--s)) calc(8 * var(--s));
  border-radius: calc(6 * var(--s));
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font-size: calc(14 * var(--s));
}

.pomo-cfg-actions {
  display: flex;
  justify-content: flex-end;
  gap: calc(8 * var(--s));
}

.pomo-cfg-actions button {
  padding: calc(6 * var(--s)) calc(14 * var(--s));
  border-radius: calc(8 * var(--s));
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.06);
  color: #eaf4f1;
  cursor: pointer;
}

#pomoSave { background: #8ff0e2; color: #0b1a17; border: none; }

body.focus #settingsPanel,
body.focus #drawer,
body.focus .chips,
body.focus .settings,
body.focus #cleanCover {
  display: none !important;
}

body.focus .pomo {
  opacity: 1;
}
'''

for d in dirs:
    p = os.path.join(d, "index.html")
    if not os.path.exists(p):
        continue
    ht = io.open(p, encoding="utf-8").read()
    if 'id="pomo"' not in ht:
        ht = ht.replace("</footer>", "</footer>\n" + pomo_html, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(ht)
        print("html", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "番茄钟 / 专注模式" not in ct:
            ct += pomo_css
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        jt = io.open(j, encoding="utf-8").read()
        if "initPomodoro" not in jt:
            idx = jt.rfind("})();")
            if idx > 0:
                jt = jt[:idx] + pomo_js + jt[idx:]
                io.open(j, "w", encoding="utf-8", newline="").write(jt)
                print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        hh = io.open(h, encoding="utf-8").read()
        hh = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=290", hh)
        io.open(h, "w", encoding="utf-8", newline="").write(hh)
