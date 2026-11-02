import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

comp = r'''
  function lyricComplement() {
    var base = cssHsl(getComputedStyle(document.body).getPropertyValue('--accent'));
    var s = Math.max(0.55, Math.min(0.9, base.s));
    return hslStr(base.h + 165, s * 0.78, 0.66);
  }
'''

for d in dirs:
    j = os.path.join(d, "js", "app.js")
    if not os.path.exists(j):
        continue
    t = io.open(j, encoding="utf-8").read()

    if "function lyricComplement" not in t:
        t = t.replace("  function aiWordColor(text) {", comp + "\n  function aiWordColor(text) {", 1)

    # scatter: one highlight word gets complement
    old_s = """      var __pal = lyricPalette();
      elWord.style.color = lyricWordColor(unit, i, __pal);"""
    new_s = """      var __pal = lyricPalette();
      var __hi = Math.floor(Math.abs(Math.sin(seed + 3) * 10000)) % units.length;
      elWord.style.color = (i === __hi) ? lyricComplement() : lyricWordColor(unit, i, __pal);"""
    if old_s in t:
        t = t.replace(old_s, new_s)

    # stack: one non-big segment gets complement
    old_t = """      var __pal2 = lyricPalette();
      seg.style.color = lyricWordColor(part, i, __pal2);"""
    new_t = """      var __pal2 = lyricPalette();
      var __hi2 = (seed + 1) % parts.length;
      if (__hi2 === bigIdx) __hi2 = (__hi2 + 1) % parts.length;
      seg.style.color = (i === __hi2) ? lyricComplement() : lyricWordColor(part, i, __pal2);"""
    if old_t in t:
        t = t.replace(old_t, new_t)

    io.open(j, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=61", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
