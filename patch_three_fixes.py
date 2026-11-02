import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

warn_html = '<span class="bridge-warn" id="bridgeWarn" title="本地桥接未连接，请重新启动 bridge">桥接断开</span>'
guide_html = '''      <button class="chip" id="guideBtn" title="使用引导">
        <span>引导</span>
      </button>
'''
modal_html = '''  <div class="onboard-mask" id="onboardMask">
    <div class="onboard">
      <div class="onboard-title">开始使用 Miku Study Room</div>
      <div class="onboard-row"><span>本地桥接</span><b id="obBridge">检测中…</b><button id="obRetry">重试</button></div>
      <div class="onboard-row"><span>AI 主题</span><b id="obAi">检测中…</b><button id="obAiOpen">打开 AI 设置</button></div>
      <div class="onboard-row"><span>隐藏界面</span><em>点胶囊上的眼睛图标，只保留封面</em></div>
      <button class="onboard-done" id="obDone">开始使用</button>
    </div>
  </div>

'''

js_onboard = r'''
  function initOnboarding() {
    var mask = $('onboardMask');
    if (!mask) return;

    var obBridge = $('obBridge');
    var obAi = $('obAi');
    var obRetry = $('obRetry');
    var obAiOpen = $('obAiOpen');
    var obDone = $('obDone');
    var guideBtn = $('guideBtn');

    function checkBridge() {
      if (!obBridge) return;
      obBridge.textContent = '检测中…';
      fetch(BRIDGE + 'now.json', { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.ok) {
            obBridge.textContent = '已连接 · ' + (d.title || '');
            obBridge.className = 'ok';
          } else {
            obBridge.textContent = '未连接';
            obBridge.className = 'bad';
          }
        })
        .catch(function () {
          obBridge.textContent = '未连接';
          obBridge.className = 'bad';
        });
    }

    function checkAi() {
      if (!obAi) return;
      fetch(BRIDGE + 'ai.config', { cache: 'no-store' })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.enabled) {
            obAi.textContent = '已启用 · ' + (d.model || '');
            obAi.className = 'ok';
          } else {
            obAi.textContent = '未配置（会用封面配色）';
            obAi.className = 'bad';
          }
        })
        .catch(function () {
          obAi.textContent = '未配置';
          obAi.className = 'bad';
        });
    }

    function openMask() {
      mask.classList.add('open');
      checkBridge();
      checkAi();
    }

    if (obRetry) obRetry.addEventListener('click', checkBridge);
    if (obAiOpen) obAiOpen.addEventListener('click', function () {
      fetch(BRIDGE + 'ai.open', { cache: 'no-store' }).catch(function () {});
    });
    if (obDone) obDone.addEventListener('click', function () {
      mask.classList.remove('open');
      try { localStorage.setItem('onboarded', '1'); } catch (e) {}
    });
    if (guideBtn) guideBtn.addEventListener('click', openMask);

    var seen = false;
    try { seen = localStorage.getItem('onboarded') === '1'; } catch (e) {}
    if (!seen) setTimeout(openMask, 1200);
  }

'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="bridgeWarn"' not in ht:
            ht = ht.replace('<span class="source" id="source">内置</span>',
                            '<span class="source" id="source">内置</span>\n        ' + warn_html)
        if 'id="guideBtn"' not in ht:
            anchor = '      <button class="chip" id="themeBtn"'
            ht = ht.replace(anchor, guide_html + anchor, 1)
        if 'id="onboardMask"' not in ht:
            ht = ht.replace('</body>', modal_html + '</body>', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=193", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
        print("html", d)

    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    t = t.replace("""    if (S.mode === 'mirror') { sendAction('playpause'); return; }""",
                  """    if (S.mode === 'mirror') {
      sendAction('playpause').catch(function () {});
      S.mirrorUserPaused = !S.playing;
      setPlaying(!S.playing);
      return;
    }""")

    t = t.replace("""    el.pos.textContent = fmt(S.position);""",
                  """    el.pos.textContent = (S.mode === 'mirror' ? '≈ ' : '') + fmt(S.position);""")

    t = t.replace("""        S.bridgeAlive = true;
        S.bridgeFails = 0;""",
                  """        S.bridgeAlive = true;
        S.bridgeFails = 0;
        document.body.classList.remove('bridge-down');""")

    t = t.replace("""          setPlaying(true);""",
                  """          if (!S.mirrorUserPaused) setPlaying(true);""")

    t = t.replace("""        if (!d || !d.ok || !d.title) { S.bridgeFails = (S.bridgeFails || 0) + 1; if (S.bridgeFails > 3) S.bridgeAlive = false; return; }""",
                  """        if (!d || !d.ok || !d.title) { S.bridgeFails = (S.bridgeFails || 0) + 1; if (S.bridgeFails > 3) { S.bridgeAlive = false; document.body.classList.add('bridge-down'); } return; }""")

    t = t.replace("""            if (idChanged) S.position = 0;""",
                  """            if (idChanged) { S.position = 0; S.mirrorUserPaused = false; }""")

    if "initOnboarding" not in t:
        t = t.replace("  function bind() {", js_onboard + "\n  function bind() {", 1)
        t = t.replace("    bind();", "    bind();\n    initOnboarding();", 1)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "引导与桥接提示" not in ct:
            ct += '''

/* 引导与桥接提示 */
.bridge-warn {
  display: none;
  margin-left: calc(8 * var(--s));
  padding: 0 calc(8 * var(--s));
  border-radius: 999px;
  font-size: calc(11 * var(--s));
  line-height: calc(18 * var(--s));
  background: rgba(255, 120, 110, 0.18);
  border: 1px solid rgba(255, 120, 110, 0.4);
  color: #ffb3ac;
}

body.bridge-down .bridge-warn {
  display: inline-flex;
}

.onboard-mask {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.55);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}

.onboard-mask.open {
  display: flex;
}

.onboard {
  width: calc(460 * var(--s));
  max-width: 86vw;
  padding: calc(26 * var(--s)) calc(30 * var(--s));
  border-radius: calc(16 * var(--s));
  background: rgba(18, 28, 26, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 calc(20 * var(--s)) calc(50 * var(--s)) rgba(0, 0, 0, 0.6);
  color: #e9f3ef;
}

.onboard-title {
  font-size: calc(20 * var(--s));
  font-weight: 600;
  margin-bottom: calc(18 * var(--s));
}

.onboard-row {
  display: flex;
  align-items: center;
  gap: calc(10 * var(--s));
  margin-bottom: calc(14 * var(--s));
  font-size: calc(13 * var(--s));
}

.onboard-row span {
  width: calc(70 * var(--s));
  color: rgba(233, 243, 239, 0.6);
}

.onboard-row b {
  flex: 1;
  font-weight: 500;
}

.onboard-row b.ok {
  color: #9fe0c8;
}

.onboard-row b.bad {
  color: #f0b0a8;
}

.onboard-row em {
  flex: 1;
  font-style: normal;
  color: rgba(233, 243, 239, 0.75);
}

.onboard-row button {
  padding: calc(4 * var(--s)) calc(10 * var(--s));
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: #e9f3ef;
  font-size: calc(12 * var(--s));
  cursor: pointer;
}

.onboard-done {
  margin-top: calc(10 * var(--s));
  width: 100%;
  padding: calc(10 * var(--s));
  border-radius: calc(10 * var(--s));
  border: 0;
  background: #8fd8cf;
  color: #10201c;
  font-size: calc(14 * var(--s));
  font-weight: 600;
  cursor: pointer;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
