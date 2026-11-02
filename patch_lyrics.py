import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\MikuWallpaper\source\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\miku_study_room",
]

old_parse = """  function parseLrc(text) {
    var out = [];
    var re = /\\[(\\d{1,3}):(\\d{1,2})(?:[.:](\\d{1,3}))?\\]/g;

    String(text || '').split(/\\r?\\n/).forEach(function (line) {
      var stamps = [];
      var m;
      while ((m = re.exec(line)) !== null) {
        var frac = m[3] || '0';
        var ms = frac.length === 3 ? +frac : (+frac) * 10;
        stamps.push(+m[1] * 60 + +m[2] + ms / 1000);
      }
      if (!stamps.length) return;
      var content = line.replace(/\\[[^\\]]*\\]/g, '').trim();
      if (!content) return;
      stamps.forEach(function (t) {
        out.push({ t: t, text: content });
      });
    });

    out.sort(function (a, b) { return a.t - b.t; });
    return out;
  }
"""

new_parse = """  function parseLrc(text) {
    var map = {};
    var re = /\\[(\\d{1,3}):(\\d{1,2})(?:[.:](\\d{1,3}))?\\]/g;

    String(text || '').split(/\\r?\\n/).forEach(function (line) {
      var stamps = [];
      var m;
      while ((m = re.exec(line)) !== null) {
        var frac = m[3] || '0';
        var ms = frac.length === 3 ? +frac : (+frac) * 10;
        stamps.push(+m[1] * 60 + +m[2] + ms / 1000);
      }
      if (!stamps.length) return;
      var content = line.replace(/\\[[^\\]]*\\]/g, '').trim();
      if (!content) return;

      stamps.forEach(function (t) {
        var key = t.toFixed(2);
        if (!map[key]) {
          map[key] = { t: t, text: content, sub: '' };
        } else if (!map[key].sub) {
          map[key].sub = content;
        } else {
          map[key].sub += ' / ' + content;
        }
      });
    });

    var out = Object.keys(map).map(function (k) { return map[k]; });
    out.sort(function (a, b) { return a.t - b.t; });
    return out;
  }
"""

old_render = """      var div = document.createElement('div');
      div.className = 'line';
      div.dataset.i = i;
      div.textContent = line.text;
      frag.appendChild(div);"""

new_render = """      var div = document.createElement('div');
      div.className = 'line';
      div.dataset.i = i;
      div.innerHTML = esc(line.text) + (line.sub ? '<span class="sub">' + esc(line.sub) + '</span>' : '');
      frag.appendChild(div);"""

old_update = """    var nodes = el.lyrics.children;
    for (var j = 0; j < nodes.length; j++) {
      nodes[j].classList.toggle('active', j === idx);
      nodes[j].classList.toggle('past', j < idx);
    }
    centerActive();"""

new_update = """    var nodes = el.lyrics.children;
    for (var j = 0; j < nodes.length; j++) {
      nodes[j].classList.toggle('active', j === idx);
      nodes[j].classList.toggle('past', j < idx);
      nodes[j].classList.toggle('near', Math.abs(j - idx) === 1);
      nodes[j].classList.toggle('far', Math.abs(j - idx) > 1);
    }
    centerActive();"""

css = """

/* ---------------- Folia 风格歌词层 ---------------- */
.line {
  font-size: calc(30 * var(--s));
  opacity: 0.16;
  filter: blur(4px);
  transform: scale(0.9);
  transform-origin: center center;
  transition: opacity 0.5s var(--ease), filter 0.5s var(--ease),
              font-size 0.55s var(--ease), transform 0.55s var(--ease),
              color 0.4s ease;
}

.line.near {
  font-size: calc(38 * var(--s));
  opacity: 0.34;
  filter: blur(1.6px);
  transform: scale(0.96);
}

.line.active {
  font-size: calc(58 * var(--s));
  opacity: 1;
  filter: none;
  transform: scale(1);
  letter-spacing: 0.01em;
}

.line .sub {
  display: block;
  margin-top: calc(10 * var(--s));
  font-size: 0.42em;
  font-weight: 400;
  letter-spacing: 0.04em;
  color: rgba(232, 252, 249, 0.55);
  filter: none;
}

.line.active .sub {
  color: rgba(232, 252, 249, 0.78);
}

.lyrics-viewport { height: 64vh; }
"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old_parse in t:
        t = t.replace(old_parse, new_parse)
    else:
        print("parse miss", p)
    if old_render in t:
        t = t.replace(old_render, new_render)
    else:
        print("render miss", p)
    if old_update in t:
        t = t.replace(old_update, new_update)
    else:
        print("update miss", p)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", p)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "Folia 风格歌词层" not in ct:
            ct += css
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", c)
