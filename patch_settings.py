import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()

    start = t.find('    <div class="lyric-offset">')
    end = t.find('    <div class="scroll-pager">', start)
    if start < 0 or end < 0 or 'id="settingsPanel"' in t:
        print("skip", d)
        continue

    settings_body = t[start:end]
    t = t[:start] + t[end:]

    settings_html = (
        '  <aside class="settings" id="settingsPanel">\n'
        '    <div class="settings-head">\n'
        '      <span>设置</span>\n'
        '      <button class="close" id="closeSettings" aria-label="关闭">×</button>\n'
        '    </div>\n'
        + settings_body +
        '  </aside>\n\n'
    )

    # gear button + settings panel before the drawer
    drawer_at = t.find('  <aside class="drawer"')
    if drawer_at < 0:
        drawer_at = t.find('<aside class="drawer"')
    if drawer_at >= 0:
        t = t[:drawer_at] + '  <button class="gear" id="settingsBtn" title="设置">⚙</button>\n\n' + settings_html + t[drawer_at:]

    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)

    j = os.path.join(d, "js", "app.js")
    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "settingsPanel: $('settingsPanel')," not in t:
            t = t.replace("    drawer: $('drawer'),", "    drawer: $('drawer'),\n    settingsPanel: $('settingsPanel'),\n    settingsBtn: $('settingsBtn'),\n    closeSettings: $('closeSettings'),")
        if "el.settingsBtn.addEventListener" not in t:
            t = t.replace("    el.listBtn.addEventListener('click', function () {",
                          "    if (el.settingsBtn) el.settingsBtn.addEventListener('click', function (e) { e.stopPropagation(); var open = el.settingsPanel.classList.toggle('open'); if (open) { closePickers(); } sendAction(open ? 'hideicons' : 'showicons').catch(function () {}); });\n    if (el.closeSettings) el.closeSettings.addEventListener('click', function () { el.settingsPanel.classList.remove('open'); sendAction('showicons').catch(function () {}); });\n\n    el.listBtn.addEventListener('click', function () {")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".gear {" not in ct:
            ct += '''

/* 齿轮 + 设置面板 */
.gear {
  position: fixed;
  top: calc(22 * var(--s));
  right: calc(22 * var(--s));
  z-index: 16;
  width: calc(38 * var(--s));
  height: calc(38 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(8, 14, 16, 0.55);
  color: var(--text);
  font-size: calc(17 * var(--s));
  line-height: 1;
  cursor: pointer;
  backdrop-filter: blur(14px);
}

.gear:hover { background: rgba(255, 255, 255, 0.14); }

.settings {
  position: fixed;
  left: 50%;
  top: 50%;
  z-index: 18;
  width: min(560px, 70vw);
  max-height: 76vh;
  overflow-y: auto;
  padding: calc(22 * var(--s)) 0 calc(18 * var(--s));
  background: rgba(6, 12, 14, 0.9);
  backdrop-filter: blur(26px) saturate(1.2);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: calc(18 * var(--s));
  box-shadow: 0 calc(30 * var(--s)) calc(80 * var(--s)) rgba(0, 0, 0, 0.6);
  transform: translate(-50%, -46%) scale(0.96);
  opacity: 0;
  pointer-events: none;
  transition: transform 0.35s var(--ease), opacity 0.3s ease;
}

.settings.open {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
  pointer-events: auto;
}

.settings-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 calc(24 * var(--s)) calc(12 * var(--s));
  font-size: calc(13 * var(--s));
  letter-spacing: 0.18em;
  color: var(--muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  margin-bottom: calc(10 * var(--s));
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h2 = os.path.join(d, "index.html")
    if os.path.exists(h2):
        t = io.open(h2, encoding="utf-8").read()
        import re
        t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=56", t)
        io.open(h2, "w", encoding="utf-8", newline="").write(t)
