import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

for d in dirs:
    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r'\n    <div class="pomodoro"[\s\S]*?\n    </div>\n', "\n", ht, count=1)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
        print("html", d)

    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    for line in [
        "    pomo: $('pomodoro'),\n",
        "    pomoTime: $('pomoTime'),\n",
        "    pomoLabel: $('pomoLabel'),\n",
        "    pomoRing: $('pomoRing'),\n",
    ]:
        t = t.replace(line, "")

    t = t.replace("""        if (p.pomodoro && p.pomodoro.value === false) {
          el.pomo.style.display = 'none';
        }
""", "")

    start = t.find("  var POMO = {")
    if start >= 0:
        end = t.find("\n  /*", t.find("  function tickPomo", start))
        if end < 0:
            end = t.find("\n  function ", t.find("  function tickPomo", start) + 10)
        t = t[:start] + t[end + 1:]

    t = t.replace("    updatePomo();\n", "")
    t = t.replace("    tickPomo(dt);\n", "")
    t = t.replace("""    el.pomo.addEventListener('click', togglePomo);
    el.pomo.addEventListener('contextmenu', function (e) {
      e.preventDefault();
      resetPomo();
      toast('番茄钟已重置');
    });
""", "")
    t = t.replace("番茄钟", "")

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        ct = re.sub(r'\n\.pomodoro[\s\S]*?\n\}\n', "\n", ct, count=1)
        ct = re.sub(r'\n\.pomo-[^\n]*\{[\s\S]*?\n\}\n', "\n", ct)
        io.open(c, "w", encoding="utf-8", newline="").write(ct)
        print("css", d)

    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=192", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
