import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_old_start = "    <div class=\"ai-box\">"
html_old_end = "    <div class=\"scroll-pager\">"

html_new = '''    <div class="ai-box">
      <div class="ai-title">AI 主题</div>
      <div id="aiState">读取中…</div>
      <div class="ai-hint">编辑 bridge\\ai.ini 后切换歌曲生效</div>
    </div>
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        i = t.find(html_old_start)
        j = t.find(html_old_end, i)
        if i >= 0 and j > i:
            t = t[:i] + html_new + t[j:]
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    jf = os.path.join(d, "js", "app.js")
    if not os.path.exists(jf):
        continue
    t = io.open(jf, encoding="utf-8").read()

    start = t.find("  function loadAiSettings() {")
    end = t.find("  function saveAiSettings()", start)
    if start >= 0 and end > start:
        t = t[:start] + '''  function loadAiSettings() {
    fetch(BRIDGE + 'ai.config', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (c) {
        S.aiEnabled = !!(c && c.enabled);
        S.aiBase = (c && c.base) || '';
        S.aiModel = (c && c.model) || '';
        if (el.aiState) {
          el.aiState.textContent = S.aiEnabled
            ? ('AI 已启用 · ' + (S.aiModel || 'default'))
            : 'AI 未启用（使用封面取色，免费）';
        }
      })
      .catch(function () {
        if (el.aiState) el.aiState.textContent = '读取 AI 配置失败';
      });
  }

''' + t[end:]

    # maybeAiTheme: config comes from bridge, no key/base check
    t = t.replace(
        "if (!S.aiEnabled || !S.aiKey || !S.aiBase || !d || !d.id) return;",
        "if (!S.aiEnabled || !d || !d.id) return;"
    )

    old_url = """    var url = BRIDGE + 'ai.theme?b=' + encodeURIComponent(b64(S.aiBase)) +
      '&k=' + encodeURIComponent(b64(S.aiKey)) +
      '&m=' + encodeURIComponent(b64(S.aiModel)) +
      '&p=' + encodeURIComponent(b64(buildAiPrompt(d)));"""
    new_url = """    var url = BRIDGE + 'ai.theme?p=' + encodeURIComponent(b64(buildAiPrompt(d)));"""
    if old_url in t:
        t = t.replace(old_url, new_url)

    io.open(jf, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if ".ai-title" not in ct:
            ct += '''
.ai-title { color: var(--text); font-weight: 600; }
.ai-hint { color: var(--muted); font-size: calc(11 * var(--s)); line-height: 1.6; }
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
