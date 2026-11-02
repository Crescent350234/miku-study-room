import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

html_block = '''  <div class="clean-cover" id="cleanCover">
    <img id="cleanCoverImg" alt="">
    <button class="clean-eye" id="cleanEye" aria-label="恢复界面" title="恢复界面">
      <svg viewBox="0 0 24 24"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="12" r="2.4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>
    </button>
  </div>

'''

js_old = '''    var cleanBtn = $('cleanBtn');
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

js_new = '''    var cleanBtn = $('cleanBtn');
    var cleanCoverImg = $('cleanCoverImg');
    var cleanEye = $('cleanEye');

    var syncCleanCover = function () {
      var c = $('cover');
      if (cleanCoverImg && c && c.src) cleanCoverImg.src = c.src;
    };

    if (cleanBtn) {
      var applyClean = function (on) {
        document.body.classList.toggle('clean-wallpaper', on);
        cleanBtn.classList.toggle('on', on);
        if (on) syncCleanCover();
        try { localStorage.setItem('cleanWallpaper', on ? '1' : '0'); } catch (e) {}
      };
      var cleanSaved = false;
      try { cleanSaved = localStorage.getItem('cleanWallpaper') === '1'; } catch (e) {}
      applyClean(cleanSaved);

      cleanBtn.addEventListener('click', function () {
        applyClean(!document.body.classList.contains('clean-wallpaper'));
      });

      if (cleanEye) {
        cleanEye.addEventListener('click', function () {
          applyClean(false);
        });
      }

      setInterval(function () {
        if (document.body.classList.contains('clean-wallpaper')) syncCleanCover();
      }, 2000);
    }
'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        if 'id="cleanCover"' not in ht:
            ht = ht.replace('  <footer class="player" id="player">', html_block + '  <footer class="player" id="player">', 1)
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=178", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
        print("html", d)

    p = os.path.join(d, "js", "app.js")
    if os.path.exists(p):
        t = io.open(p, encoding="utf-8").read()
        if js_old in t:
            t = t.replace(js_old, js_new)
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            print("js", d)
        else:
            print("js anchor miss", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "只看壁纸：仅封面" not in ct:
            ct += '''

/* 只看壁纸：仅保留封面 + 右上角小眼睛 */
body.clean-wallpaper .player,
body.clean-wallpaper .drawer,
body.clean-wallpaper .settings,
body.clean-wallpaper .start-hint {
  display: none !important;
}

.clean-cover {
  display: none;
}

body.clean-wallpaper .clean-cover {
  display: block;
  position: fixed;
  right: calc(46 * var(--s));
  bottom: calc(46 * var(--s));
  width: calc(210 * var(--s));
  height: calc(210 * var(--s));
  border-radius: calc(14 * var(--s));
  overflow: hidden;
  z-index: 60;
  box-shadow: 0 calc(18 * var(--s)) calc(40 * var(--s)) rgba(0, 0, 0, 0.55);
}

.clean-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.clean-eye {
  position: absolute;
  top: calc(8 * var(--s));
  right: calc(8 * var(--s));
  width: calc(30 * var(--s));
  height: calc(30 * var(--s));
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.clean-eye:hover {
  background: rgba(0, 0, 0, 0.55);
  transform: scale(1.06);
}

.clean-eye svg {
  width: 60%;
  height: 60%;
  fill: none;
  stroke: currentColor;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)
