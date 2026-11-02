import io, os

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

helper = r'''
  function splitLyricSegments(text, maxParts) {
    var boundary = '的了着过和与在是就都也又还而但却把被让给对从到向于中里上下后前时のをがにはでともへやからまで';
    var raw = String(text || '').split(/[，。！？、；：,.!?;:]+/).filter(function (s) { return s.trim().length > 0; });

    function splitAtBest(s) {
      if (s.length <= 10) return [s];
      var mid = Math.floor(s.length / 2);
      var best = -1;
      var bestDist = 1e9;
      for (var i = 2; i < s.length - 2; i++) {
        if (boundary.indexOf(s.charAt(i)) >= 0) {
          var d = Math.abs(i - mid);
          if (d < bestDist) { bestDist = d; best = i; }
        }
      }
      if (best < 0) best = mid - 1;
      return [s.slice(0, best + 1), s.slice(best + 1)];
    }

    var out = [];
    raw.forEach(function (part) {
      var pieces = [part];
      while (pieces.length < maxParts) {
        var longest = 0;
        for (var i = 1; i < pieces.length; i++) if (pieces[i].length > pieces[longest].length) longest = i;
        if (pieces[longest].length <= 12) break;
        var halves = splitAtBest(pieces[longest]);
        if (halves[0].length === 0 || halves[1].length === 0) break;
        pieces.splice.apply(pieces, [longest, 1].concat(halves));
      }
      out = out.concat(pieces);
    });

    out = out.filter(function (s) { return s.trim().length > 0; });
    if (out.length === 0) out = [String(text || '')];
    return out.slice(0, maxParts);
  }
'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if "function splitLyricSegments" not in t:
        t = t.replace("  function buildTiltLine(idx) {", helper + "\n  function buildTiltLine(idx) {", 1)

    old = """    var parts = text.split(/[，。！？、；：]+/).filter(function (s) { return s.trim().length > 0; });
    if (parts.length < 2) {
      var mid = Math.ceil(text.length / 2);
      parts = [text.slice(0, mid), text.slice(mid)];
    }
    parts = parts.slice(0, 4).filter(function (s) { return s.length > 0; });"""
    new = """    var parts = splitLyricSegments(text, 3);"""
    if old in t:
        t = t.replace(old, new)
    else:
        print("tilt anchor miss", d)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        import re
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=129", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
