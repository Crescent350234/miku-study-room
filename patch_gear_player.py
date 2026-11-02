import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

list_btn = '''      <button class="ctl list" id="listBtn" aria-label="歌单">
        <svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      </button>'''

gear_btn = list_btn + '''
      <button class="ctl list" id="settingsBtn" aria-label="设置">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M19.4 13a7.9 7.9 0 0 0 0-2l2-1.5-2-3.4-2.3 1a8 8 0 0 0-1.7-1L15 3h-4l-.4 2.6a8 8 0 0 0-1.7 1l-2.3-1-2 3.4L6.6 11a7.9 7.9 0 0 0 0 2l-2 1.5 2 3.4 2.3-1a8 8 0 0 0 1.7 1L11 21h4l.4-2.6a8 8 0 0 0 1.7-1l2.3 1 2-3.4z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>
      </button>'''

for d in dirs:
    h = os.path.join(d, "index.html")
    if not os.path.exists(h):
        continue
    t = io.open(h, encoding="utf-8").read()

    # remove floating gear
    import re
    t = re.sub(r'\s*<button class="gear" id="settingsBtn"[^>]*>.*?</button>\s*', '\n', t, flags=re.S)

    if 'class="ctl list" id="settingsBtn"' not in t:
        if list_btn in t:
            t = t.replace(list_btn, gear_btn, 1)
        else:
            print("anchor miss", d)

    t = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=63", t)
    io.open(h, "w", encoding="utf-8", newline="").write(t)
    print("html", d)
