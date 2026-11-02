import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "function fetchLocalPlaylist" not in t:
        t = t.replace("  function fetchPlaylist() {", '''  function fetchLocalPlaylist() {
    return fetch('music/playlist.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (data) {
        if (!Array.isArray(data) || !data.length) return [];
        return data.map(function (s) {
          return {
            name: cleanName(s.name || s.file || '未知曲目'),
            artist: s.artist || '本地',
            url: 'music/' + s.file,
            lrc: s.lrc ? ('music/' + s.lrc) : '',
            pic: ''
          };
        }).filter(function (s) { return s.url; });
      })
      .catch(function () { return []; });
  }

  function fetchPlaylist() {''')

    old = """    loadPlaylistConfig()
      .then(fetchPlaylist)
      .then(function (songs) {"""
    new = """    loadPlaylistConfig()
      .then(function () {
        return fetchLocalPlaylist().then(function (local) {
          return (local && local.length) ? local : fetchPlaylist();
        });
      })
      .then(function (songs) {"""
    if old in t:
        t = t.replace(old, new)
    else:
        print("chain miss", d)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=234", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
