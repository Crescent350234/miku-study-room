import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\MikuWallpaper\source\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\miku_study_room",
]

poll_fn = r'''
  var neteaseTimer = null;

  function pollNetease() {
    fetch(BRIDGE + 'now.json', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d || !d.ok || !d.title) return;

        var changed = d.title !== S.netease.title || d.artist !== S.netease.artist || (d.id || '') !== (S.netease.id || '');
        S.netease = { title: d.title, artist: d.artist, id: d.id || '' };
        S.hasMedia = true;

        if (S.mode === 'local' && !S.userModeChosen) {
          S.mirror.title = d.title;
          S.mirror.artist = d.artist;
          setMode('mirror');
          changed = true;
        }

        if (S.mode === 'mirror' && changed) {
          S.mirror.title = d.title;
          S.mirror.artist = d.artist;
          S.mirror.playing = true;
          el.title.textContent = d.title;
          el.artist.textContent = d.artist;
          setPlaying(true);

          if (d.pic) el.cover.src = d.pic;
          if (d.duration) { S.duration = d.duration; S.position = 0; renderProgress(); }
          if (d.lrc) loadLyrics(d.lrc, d.title);

          renderPlaylist();
        }
      })
      .catch(function () {});
  }
'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "netease: {" not in t:
        t = t.replace(
            "    mirror: { title: '', artist: '', playing: false, position: 0, duration: 0 },",
            "    mirror: { title: '', artist: '', playing: false, position: 0, duration: 0 },\n    netease: { title: '', artist: '', id: '' },",
            1,
        )

    if "function pollNetease" not in t:
        t = t.replace("  function applyQueue(data, ver) {", poll_fn + "\n  function applyQueue(data, ver) {", 1)

    if "setInterval(pollNetease" not in t:
        t = t.replace(
            "    setInterval(pollQueue, 2500);",
            "    setInterval(pollQueue, 2500);\n    setInterval(pollNetease, 2000);\n    pollNetease();",
            1,
        )

    # SMTC 不要覆盖网易云窗口标题数据
    if "if (S.netease.id) return;" not in t:
        t = t.replace(
            "    window.wallpaperRegisterMediaPropertiesListener(function (e) {",
            "    window.wallpaperRegisterMediaPropertiesListener(function (e) {\n      if (S.netease && S.netease.id) return;",
            1,
        )
        t = t.replace(
            "    window.wallpaperRegisterMediaPlaybackListener(function (e) {",
            "    window.wallpaperRegisterMediaPlaybackListener(function (e) {\n      if (S.netease && S.netease.id) return;",
            1,
        )

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("patched", p)
