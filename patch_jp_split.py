import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

helper = r'''
  function keyBoundaryOk(text, word) {
    var pos = text.indexOf(word);
    if (pos < 0) return false;
    var next = text.charAt(pos + word.length);
    if (!next) return true;
    return 'をがにはでとへもやの、。！？,.!? '.indexOf(next) >= 0;
  }

  function jpChunks(text) {
    var arr = Array.from(text);
    var chunks = [];
    var cur = '';
    var marks = 'をがにはでとへもやの';
    arr.forEach(function (ch) {
      cur += ch;
      if (marks.indexOf(ch) >= 0) { chunks.push(cur); cur = ''; }
    });
    if (cur) chunks.push(cur);
    return chunks;
  }
'''

old_ai = """    if (S.aiTheme && S.aiTheme.emphasis) {
      S.aiTheme.emphasis.forEach(function (w) {
        if (w && w.length >= 2 && w.length <= 6 && text.indexOf(w) >= 0 && w.length < text.length) {
          candidates.push(w);
        }
      });
    }
    if (!candidates.length && S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word && wc.word.length >= 2 && wc.word.length <= 6 && text.indexOf(wc.word) >= 0 && wc.word.length < text.length) {
          candidates.push(wc.word);
        }
      });
    }"""

new_ai = """    if (S.aiTheme && S.aiTheme.emphasis) {
      S.aiTheme.emphasis.forEach(function (w) {
        if (w && w.length >= 2 && w.length <= 6 && text.indexOf(w) >= 0 && w.length < text.length && keyBoundaryOk(text, w)) {
          candidates.push(w);
        }
      });
    }
    if (!candidates.length && S.aiTheme && S.aiTheme.wordColors) {
      S.aiTheme.wordColors.forEach(function (wc) {
        if (wc && wc.word && wc.word.length >= 2 && wc.word.length <= 6 && text.indexOf(wc.word) >= 0 && wc.word.length < text.length && keyBoundaryOk(text, wc.word)) {
          candidates.push(wc.word);
        }
      });
    }"""

old_fb = """    if (!candidates.length) {
      var chunks = text.split(/[，。！？、；：\\s]+/).filter(function (s) { return s.length >= 2; });
      chunks.forEach(function (chunk) {
        var arr = Array.from(chunk);
        for (var i = 0; i + 2 <= arr.length; i += 1) {
          candidates.push(arr.slice(i, i + Math.min(3, arr.length - i)).join(''));
        }
      });
      candidates = candidates.filter(function (w) { return w.length >= 2 && w.length <= 4 && w.length < text.length; });
    }"""

new_fb = """    if (!candidates.length) {
      if (/[\\u3040-\\u30ff]/.test(text)) {
        candidates = jpChunks(text).filter(function (w) { return w.length >= 2 && w.length < text.length; });
      } else {
        var chunks = text.split(/[，。！？、；：\\s]+/).filter(function (s) { return s.length >= 2; });
        chunks.forEach(function (chunk) {
          var arr = Array.from(chunk);
          for (var i = 0; i + 2 <= arr.length; i += 1) {
            candidates.push(arr.slice(i, i + Math.min(3, arr.length - i)).join(''));
          }
        });
        var badStart = '的了着过和与在是就都也又还而但却把被让给对从到向于中里上下后前时我你他她它们';
        candidates = candidates.filter(function (w) {
          return w.length >= 2 && w.length <= 4 && w.length < text.length && badStart.indexOf(w.charAt(0)) < 0;
        });
      }
    }"""

old_stack = """        if (lk2 && lk2.line === text && lk2.keyword && lk2.keyword.length >= 2 && text.indexOf(lk2.keyword) >= 0 && lk2.keyword.length < text.length) {
          key = lk2.keyword;
          break;
        }"""
new_stack = """        if (lk2 && lk2.line === text && lk2.keyword && lk2.keyword.length >= 2 && text.indexOf(lk2.keyword) >= 0 && lk2.keyword.length < text.length && keyBoundaryOk(text, lk2.keyword)) {
          key = lk2.keyword;
          break;
        }"""

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if "function keyBoundaryOk" not in t:
        t = t.replace("  function pickTiltKey(text, seed) {", helper + "\n  function pickTiltKey(text, seed) {", 1)
    if old_ai in t:
        t = t.replace(old_ai, new_ai)
    else:
        print("ai anchor miss", d)
    if old_fb in t:
        t = t.replace(old_fb, new_fb)
    else:
        print("fallback anchor miss", d)
    if old_stack in t:
        t = t.replace(old_stack, new_stack)
    else:
        print("stack anchor miss", d)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=145", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
