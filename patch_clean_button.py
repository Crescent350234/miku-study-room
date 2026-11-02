import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

btn = '''      <button class="ctl" id="cleanBtn" aria-label="只看壁纸" title="只看壁纸（隐藏歌词与界面）">
        <svg viewBox="0 0 24 24"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><circle cx="12" cy="12" r="2.4" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M4 20L20 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>
      </button>
'''

js = '''    var cleanBtn = $('cleanBtn');
    if (cleanBtn) {
      var applyClean = function (on) {
        document.body.classList.toggle('clean-wallpaper', on);
        cleanBtn.classList.toggle('on', on);
        try { localStorage.setItem('cleanWallpaper', on ? '1' : '0'); } catch (e) {}
      };
      var cleanSaved = false;
      try { cleanSaved = localStorage.getItem('cleanWallpaper') === '1'; } catch (e) {}
      applyClean(cleanSaved);
      cleanBtn.addEventListener('click', function () {
        applyClean(!document.body.classList.contains('clean-wallpaper'));
      });
    }

'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="cleanBtn"' not in ht:
            ht = ht.replace('      <button class="ctl list" id="listBtn"', btn + '      <button class="ctl list" id="listBtn"', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=177", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
        print("html", d)

    p = os.path.join(d, "js", "app.js")
    if os.path.exists(p):
        t = io.open(p, encoding="utf-8").read()
        if "cleanBtn" not in t:
            t = t.replace("  function start() {", "  function start() {\n" + js, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "只看壁纸模式" not in ct:
            ct += '''

/* 只看壁纸模式：隐藏歌词与界面装饰 */
body.clean-wallpaper .lyrics-area,
body.clean-wallpaper .qs-layer,
body.clean-wallpaper .bubble-layer,
body.clean-wallpaper #stackLayer,
body.clean-wallpaper .hud-left,
body.clean-wallpaper .hud-right,
body.clean-wallpaper .deco,
body.clean-wallpaper #startHint,
body.clean-wallpaper .pomo {
  display: none !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
