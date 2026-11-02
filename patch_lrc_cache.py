import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old = r'''  function loadLyrics(url, title) {
    var token = ++S.lyricToken;
    S.lrc = [];

    if (!url) {
      renderLyrics([]);
      el.empty.textContent = '暂无歌词 · 尽情享受音乐吧';
      return;
    }

    el.empty.textContent = '歌词加载中…';
    document.body.classList.add('no-lyrics');

    fetch(url)
      .then(function (r) { return r.ok ? r.text() : ''; })
      .then(function (text) {
        if (token !== S.lyricToken) return;
        S.lrc = parseLrc(text);
        renderLyrics(S.lrc);
      })'''

new = r'''  function lrcCacheKey() {
    if (S.mode !== 'mirror' || !S.netease || !S.netease.id) return '';
    return 'lrc:' + S.netease.id;
  }

  function saveLrcCache(key, text) {
    if (!key || !text) return;
    try {
      localStorage.setItem(key, text);
      var keys = JSON.parse(localStorage.getItem('lrcKeys') || '[]');
      if (keys.indexOf(key) < 0) keys.push(key);
      while (keys.length > 200) {
        var old = keys.shift();
        localStorage.removeItem(old);
      }
      localStorage.setItem('lrcKeys', JSON.stringify(keys));
    } catch (e) {}
  }

  function loadLyrics(url, title) {
    var token = ++S.lyricToken;
    S.lrc = [];

    if (!url) {
      renderLyrics([]);
      el.empty.textContent = '暂无歌词 · 尽情享受音乐吧';
      return;
    }

    var cacheKey = lrcCacheKey();
    if (cacheKey) {
      var cached = '';
      try { cached = localStorage.getItem(cacheKey) || ''; } catch (e) {}
      if (cached) {
        S.lrc = parseLrc(cached);
        if (S.lrc.length) {
          document.body.classList.remove('no-lyrics');
          renderLyrics(S.lrc);
          return;
        }
      }
    }

    el.empty.textContent = '歌词加载中…';
    document.body.classList.add('no-lyrics');

    fetch(url)
      .then(function (r) { return r.ok ? r.text() : ''; })
      .then(function (text) {
        if (token !== S.lyricToken) return;
        saveLrcCache(cacheKey, text);
        S.lrc = parseLrc(text);
        renderLyrics(S.lrc);
      })'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)
    else:
        print("miss", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=134", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
