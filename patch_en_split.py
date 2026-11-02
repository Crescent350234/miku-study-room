import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

old_boundary = r'''  function keyBoundaryOk(text, word) {
    var pos = text.indexOf(word);
    if (pos < 0) return false;
    var next = text.charAt(pos + word.length);
    if (!next) return true;
    return 'をがにはでとへもやの、。！？,.!? '.indexOf(next) >= 0;
  }'''

new_boundary = r'''  function keyBoundaryOk(text, word) {
    var pos = text.indexOf(word);
    if (pos < 0) return false;
    var next = text.charAt(pos + word.length);
    var prev = pos > 0 ? text.charAt(pos - 1) : '';

    if (/[A-Za-z]/.test(word)) {
      var wordChar = /[A-Za-z'’-]/;
      if (prev && wordChar.test(prev)) return false;
      if (next && wordChar.test(next)) return false;
      return true;
    }

    if (!next) return true;
    return 'をがにはでとへもやの、。！？,.!? '.indexOf(next) >= 0;
  }'''

old_fb = """    if (!candidates.length) {
      if (/[\\u3040-\\u30ff]/.test(text)) {
        candidates = jpChunks(text).filter(function (w) { return w.length >= 2 && w.length < text.length; });
      } else {"""

new_fb = """    if (!candidates.length) {
      if (/[A-Za-z]/.test(text) && !/[\\u4e00-\\u9fff\\u3040-\\u30ff]/.test(text)) {
        var stop = ' the a an and or of to in on at for with from by is are was were be been am do does did it its this that these those i you he she we they me him her us them my your his their our as so if but not no yes'.split(' ');
        var words = text.match(/[A-Za-z][A-Za-z'’-]*/g) || [];
        candidates = words.filter(function (w) {
          var lw = w.toLowerCase();
          return w.length >= 3 && w.length < text.length && stop.indexOf(lw) < 0;
        });
      } else if (/[\\u3040-\\u30ff]/.test(text)) {
        candidates = jpChunks(text).filter(function (w) { return w.length >= 2 && w.length < text.length; });
      } else {"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    if old_boundary in t:
        t = t.replace(old_boundary, new_boundary)
    else:
        print("boundary miss", d)

    if old_fb in t:
        t = t.replace(old_fb, new_fb)
    else:
        print("fallback miss", d)

    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=146", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
