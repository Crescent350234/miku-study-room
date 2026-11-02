import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

css_add = '''

/* 跟随模式的抽屉提示 */
.queue-note {
  list-style: none;
  padding: calc(18 * var(--s)) calc(4 * var(--s));
  color: var(--muted);
  font-size: calc(13 * var(--s));
  line-height: 1.7;
}
'''

old_show = "    var show = S.mode === 'local';"
new_show = "    var show = true;"

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    c = os.path.join(d, "css", "style.css")

    if os.path.exists(j):
        t = io.open(j, encoding="utf-8").read()
        if old_show in t:
            t = t.replace(old_show, new_show)
        anchor = "  function renderPlaylist() {"
        inject = '''  function renderPlaylist() {
    if (S.mode === 'mirror') {
      el.playlist.innerHTML = '<li class="queue-note">跟随网易云播放中，歌单为只读。<br>切歌用播放器上的 ⏮ ⏸ ⏭；<br>歌词快慢用上方的 ±0.5s 校准。</li>';
      updateListButton();
      return;
    }
'''
        if "queue-note" not in t and anchor in t:
            t = t.replace(anchor, inject, 1)
        io.open(j, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "跟随模式的抽屉提示" not in ct:
            ct += css_add
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        t = io.open(h, encoding="utf-8").read()
        t = t.replace("js/app.js?v=34", "js/app.js?v=35")
        io.open(h, "w", encoding="utf-8", newline="").write(t)
