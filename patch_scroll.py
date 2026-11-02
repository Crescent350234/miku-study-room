import io, os, re, sys

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\MikuWallpaper\source\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\miku_study_room",
]

old_js = """    // 滚轮滚动歌单（有些环境不会把 wheel 传给页面，手动处理）
    el.playlist.addEventListener('wheel', function (e) {
      if (!el.drawer.classList.contains('open')) return;
      el.playlist.scrollTop += e.deltaY;
      e.preventDefault();
    }, { passive: false });

    // 按住拖动滚动（滚轮不可用时的兜底）
    var dragState = null;
    el.playlist.addEventListener('mousedown', function (e) {
      dragState = { y: e.clientY, top: el.playlist.scrollTop, moved: false };
    });
    window.addEventListener('mousemove', function (e) {
      if (!dragState) return;
      var dy = e.clientY - dragState.y;
      if (Math.abs(dy) > 4) dragState.moved = true;
      if (dragState.moved) el.playlist.scrollTop = dragState.top - dy;
    });
    window.addEventListener('mouseup', function () {
      setTimeout(function () { dragState = null; }, 0);
    });
    el.playlist.addEventListener('click', function (e) {
      if (dragState && dragState.moved) {
        e.stopPropagation();
        e.preventDefault();
      }
    }, true);
"""

new_js = """    // 滚轮：在 window 捕获，避免事件被别的层吃掉
    window.addEventListener('wheel', function (e) {
      if (!el.drawer.classList.contains('open')) return;
      var r = el.playlist.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) return;
      el.playlist.scrollTop += e.deltaY;
      syncScrollbar();
      e.preventDefault();
      e.stopPropagation();
    }, { passive: false, capture: true });

    // 拖滚动条滑块
    var thumbDrag = null;
    el.scrollThumb.addEventListener('mousedown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      thumbDrag = { y: e.clientY, top: el.playlist.scrollTop };
    });
    window.addEventListener('mousemove', function (e) {
      if (!thumbDrag) return;
      var railH = el.scrollRail.clientHeight;
      var thumbH = el.scrollThumb.clientHeight;
      var track = Math.max(1, railH - thumbH);
      var ratio = (el.playlist.scrollHeight - el.playlist.clientHeight) / track;
      el.playlist.scrollTop = thumbDrag.top + (e.clientY - thumbDrag.y) * ratio;
      syncScrollbar();
    });
    window.addEventListener('mouseup', function () { thumbDrag = null; });

    el.scrollRail.addEventListener('mousedown', function (e) {
      if (e.target === el.scrollThumb) return;
      var rect = el.scrollRail.getBoundingClientRect();
      var ratio = (e.clientY - rect.top) / Math.max(1, rect.height);
      el.playlist.scrollTop = ratio * (el.playlist.scrollHeight - el.playlist.clientHeight);
      syncScrollbar();
    });

    el.playlist.addEventListener('scroll', syncScrollbar);
"""

sync_fn = """
  function syncScrollbar() {
    if (!el.scrollRail || !el.scrollThumb) return;
    if (!el.drawer.classList.contains('open')) return;

    var r = el.playlist.getBoundingClientRect();
    var d = el.drawer.getBoundingClientRect();
    if (r.height <= 0) return;

    var railH = Math.max(40, r.height - 8);
    el.scrollRail.style.top = (r.top - d.top + 4) + 'px';
    el.scrollRail.style.height = railH + 'px';

    var max = el.playlist.scrollHeight - el.playlist.clientHeight;
    var ratio = max > 0 ? el.playlist.scrollTop / max : 0;
    var thumbH = Math.max(30, railH * (el.playlist.clientHeight / Math.max(1, el.playlist.scrollHeight)));
    el.scrollThumb.style.height = thumbH + 'px';
    el.scrollThumb.style.top = (Math.min(1, Math.max(0, ratio)) * (railH - thumbH)) + 'px';
    el.scrollRail.style.opacity = max > 0 ? '1' : '0';
  }
"""

css_add = """
/* 自定义滚动条（拖滑块） */
.playlist { scrollbar-width: none; }
.playlist::-webkit-scrollbar { width: 0 !important; height: 0 !important; display: none !important; }

.scroll-rail {
  position: absolute;
  right: calc(7 * var(--s));
  width: calc(7 * var(--s));
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  z-index: 12;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.scroll-thumb {
  position: absolute;
  left: 0;
  width: 100%;
  min-height: calc(30 * var(--s));
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.30);
  cursor: pointer;
}

.scroll-thumb:hover { background: rgba(57, 197, 187, 0.75); }
"""

for d in dirs:
    html_path = os.path.join(d, "index.html")
    js_path = os.path.join(d, "js", "app.js")
    css_path = os.path.join(d, "css", "style.css")

    if os.path.exists(html_path):
        t = io.open(html_path, encoding="utf-8").read()
        if 'id="scrollRail"' not in t:
            t = t.replace(
                '    <div class="drawer-foot"',
                '    <div class="scroll-rail" id="scrollRail"><div class="scroll-thumb" id="scrollThumb"></div></div>\n    <div class="drawer-foot"',
                1,
            )
            io.open(html_path, "w", encoding="utf-8", newline="").write(t)
            print("html", d)
        else:
            print("html already", d)

    if os.path.exists(js_path):
        t = io.open(js_path, encoding="utf-8").read()
        t = t.replace("    pageDown: $('pageDown'),", "    pageDown: $('pageDown'),\n    scrollRail: $('scrollRail'),\n    scrollThumb: $('scrollThumb'),")

        if old_js in t:
            t = t.replace(old_js, new_js)
        else:
            print("JS BLOCK NOT FOUND", d)

        if "function syncScrollbar" not in t:
            t = t.replace("  function renderPlaylist() {", sync_fn + "\n  function renderPlaylist() {", 1)

        t = t.replace("      if (open) scrollActiveIntoView();", "      if (open) { scrollActiveIntoView(); setTimeout(syncScrollbar, 80); }")
        t = t.replace("    el.playlist.innerHTML = html;", "    el.playlist.innerHTML = html;\n    setTimeout(syncScrollbar, 0);")
        t = t.replace("      sizeRing();\n      sizePetals();", "      sizeRing();\n      sizePetals();\n      syncScrollbar();")
        io.open(js_path, "w", encoding="utf-8", newline="").write(t)
        print("js", d)

    if os.path.exists(css_path):
        t = io.open(css_path, encoding="utf-8").read()
        t = t.replace("  bottom: calc(72 * var(--s));", "  bottom: calc(100 * var(--s));")
        if ".scroll-rail" not in t:
            t += css_add
        io.open(css_path, "w", encoding="utf-8", newline="").write(t)
        print("css", d)
