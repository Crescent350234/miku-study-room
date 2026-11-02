import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_anchor = '    <div class="scroll-pager">'
html_new = '''    <div class="ai-box">
      <label class="ai-toggle"><input type="checkbox" id="aiEnabled"> 启用 AI 主题（按歌生成配色）</label>
      <input id="aiBase" placeholder="接口地址，如 https://api.deepseek.com/v1" autocomplete="off">
      <input id="aiKey" type="password" placeholder="API Key（只存在本机）" autocomplete="off">
      <input id="aiModel" placeholder="模型，如 deepseek-chat" autocomplete="off">
      <div class="ai-row">
        <button id="aiSave">保存</button>
        <span id="aiState">未启用</span>
      </div>
    </div>
    <div class="scroll-pager">'''

js = r'''
  function b64(s) {
    try { return btoa(unescape(encodeURIComponent(String(s)))); } catch (e) { return ''; }
  }

  function loadAiSettings() {
    S.aiEnabled = localStorage.getItem('aiEnabled') === '1';
    S.aiBase = localStorage.getItem('aiBase') || '';
    S.aiKey = localStorage.getItem('aiKey') || '';
    S.aiModel = localStorage.getItem('aiModel') || '';
    if (el.aiEnabled) el.aiEnabled.checked = S.aiEnabled;
    if (el.aiBase) el.aiBase.value = S.aiBase;
    if (el.aiKey) el.aiKey.value = S.aiKey;
    if (el.aiModel) el.aiModel.value = S.aiModel;
    if (el.aiState) el.aiState.textContent = S.aiEnabled ? (S.aiKey ? '已启用' : '缺少 Key') : '未启用';
  }

  function saveAiSettings() {
    S.aiEnabled = el.aiEnabled ? el.aiEnabled.checked : false;
    S.aiBase = el.aiBase ? el.aiBase.value.trim().replace(/\/+$/, '') : '';
    S.aiKey = el.aiKey ? el.aiKey.value.trim() : '';
    S.aiModel = el.aiModel ? el.aiModel.value.trim() : '';
    localStorage.setItem('aiEnabled', S.aiEnabled ? '1' : '0');
    localStorage.setItem('aiBase', S.aiBase);
    localStorage.setItem('aiKey', S.aiKey);
    localStorage.setItem('aiModel', S.aiModel);
    if (el.aiState) el.aiState.textContent = S.aiEnabled ? (S.aiKey && S.aiBase ? '已启用' : '缺少 Key/地址') : '未启用';
    toast(S.aiEnabled ? 'AI 主题已开启' : 'AI 主题已关闭');
  }

  function buildAiPrompt(d) {
    var lyric = S.lrc.slice(0, 40).map(function (l) { return l.text; }).join('\n').slice(0, 800);
    return '你是音乐壁纸的配色设计师。根据歌曲情绪生成一套深色主题，只输出 JSON，不要解释。\n' +
      'JSON 字段：{"name":"4字主题名","accent":"#RRGGBB","background":"#RRGGBB","primary":"#RRGGBB","secondary":"#RRGGBB","wordColors":[{"word":"歌词里的词","color":"#RRGGBB"}]}\n' +
      '要求：accent 与 background 对比明显；wordColors 8-12 个，词必须出现在歌词里；整体贴合情绪。\n' +
      '歌曲：' + (d.title || '') + ' - ' + (d.artist || '') + '\n歌词：\n' + lyric;
  }

  function applyAiTheme(t) {
    if (!t || !t.accent) return;
    S.aiTheme = t;
    document.body.style.setProperty('--accent', t.accent);
    if (t.secondary) document.body.style.setProperty('--pink', t.secondary);
    if (t.background) document.body.style.setProperty('--theme-bg', t.background);
    if (t.primary) document.body.style.setProperty('--theme-primary', t.primary);
    renderLyrics(S.lrc);
    updateLyrics(S.position);
    if (el.aiState) el.aiState.textContent = '已应用：' + (t.name || 'AI 主题');
  }

  function maybeAiTheme(d) {
    if (!S.aiEnabled || !S.aiKey || !S.aiBase || !d || !d.id) return;

    var cacheKey = 'aiTheme:' + d.id;
    try {
      var cached = localStorage.getItem(cacheKey);
      if (cached) { applyAiTheme(JSON.parse(cached)); return; }
    } catch (e) {}

    if (S.aiBusy) return;
    S.aiBusy = true;
    if (el.aiState) el.aiState.textContent = '生成中…';

    var url = BRIDGE + 'ai.theme?b=' + encodeURIComponent(b64(S.aiBase)) +
      '&k=' + encodeURIComponent(b64(S.aiKey)) +
      '&m=' + encodeURIComponent(b64(S.aiModel)) +
      '&p=' + encodeURIComponent(b64(buildAiPrompt(d)));

    fetch(url, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res && res.error) throw new Error(String(res.error).slice(0, 120));
        var txt = res && res.choices && res.choices[0] && res.choices[0].message && res.choices[0].message.content;
        if (!txt) throw new Error('empty ai response');
        var obj = JSON.parse(String(txt).replace(/```json/gi, '').replace(/```/g, '').trim());
        try { localStorage.setItem(cacheKey, JSON.stringify(obj)); } catch (e) {}
        applyAiTheme(obj);
        toast('AI 主题 · ' + (obj.name || '已应用'));
      })
      .catch(function (err) {
        if (el.aiState) el.aiState.textContent = '失败：' + err.message;
      })
      .then(function () { S.aiBusy = false; });
  }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    j = os.path.join(d, "js", "app.js")
    c = os.path.join(d, "css", "style.css")

    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        if 'id="aiEnabled"' not in t and html_anchor in t:
            t = t.replace(html_anchor, html_new, 1)
            io.open(h, "w", encoding="utf-8", newline="").write(t)
            print("html", d)

    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if "function maybeAiTheme" not in t:
            t = t.replace("  function updateLyrics(time) {", js + "\n  function updateLyrics(time) {", 1)
        if "aiEnabled: $('aiEnabled')," not in t:
            t = t.replace("    offVal: $('offVal'),", "    offVal: $('offVal'),\n    aiEnabled: $('aiEnabled'),\n    aiBase: $('aiBase'),\n    aiKey: $('aiKey'),\n    aiModel: $('aiModel'),\n    aiSave: $('aiSave'),\n    aiState: $('aiState'),")
        if "loadAiSettings();" not in t:
            t = t.replace("    setLyricOffset(savedOff);", "    setLyricOffset(savedOff);\n    loadAiSettings();\n    if (el.aiSave) el.aiSave.addEventListener('click', saveAiSettings);\n    if (el.aiEnabled) el.aiEnabled.addEventListener('change', saveAiSettings);")
        if "maybeAiTheme(d);" not in t:
            t = t.replace("          if (d.lrc) loadLyrics(d.lrc, d.title);", "          if (d.lrc) loadLyrics(d.lrc, d.title);\n          maybeAiTheme(d);")
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "AI 主题设置" not in ct:
            ct += '''

/* AI 主题设置 */
.ai-box {
  display: flex;
  flex-direction: column;
  gap: calc(6 * var(--s));
  padding: 0 calc(14 * var(--s)) calc(10 * var(--s));
  font-size: calc(12 * var(--s));
}

.ai-box input[type="text"], .ai-box input[type="password"], .ai-box input:not([type]) {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: calc(8 * var(--s));
  color: var(--text);
  padding: calc(5 * var(--s)) calc(8 * var(--s));
  font-size: calc(12 * var(--s));
}

.ai-toggle { display: flex; align-items: center; gap: calc(6 * var(--s)); color: var(--muted); }
.ai-row { display: flex; align-items: center; gap: calc(10 * var(--s)); }
.ai-row button {
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  border-radius: 999px;
  padding: calc(4 * var(--s)) calc(12 * var(--s));
  cursor: pointer;
}
#aiState { color: var(--muted); }
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
