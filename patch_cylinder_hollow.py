import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_svg = r'''  function buildCylinderSvg() {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 600 600');
    svg.setAttribute('class', 'cyl5-svg');

    function el(tag, attrs, parent) {
      var n = document.createElementNS(NS, tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(n);
      return n;
    }

    var line = 'rgba(214, 238, 232, 0.42)';
    var faint = 'rgba(214, 238, 232, 0.16)';

    var defs = el('defs', {});

    // 镂空遮罩：轮体挖掉 6 个弹膛和中心轴
    var mask = el('mask', { id: 'cylHollow', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 600, height: 600 }, defs);
    el('circle', { cx: 300, cy: 300, r: 284, fill: '#fff' }, mask);
    for (var c = 0; c < 6; c++) {
      var ca = 30 + c * 60;
      var cg = el('g', { transform: 'rotate(' + ca + ' 300 300)' }, mask);
      el('circle', { cx: 300, cy: 112, r: 56, fill: '#000' }, cg);
    }
    el('circle', { cx: 300, cy: 300, r: 74, fill: '#000' }, mask);

    // 半透明轮体（真镂空）
    el('circle', {
      cx: 300, cy: 300, r: 284,
      fill: 'rgba(8, 18, 20, 0.42)',
      mask: 'url(#cylHollow)'
    });

    // 外圈细线
    el('circle', { cx: 300, cy: 300, r: 284, fill: 'none', stroke: line, 'stroke-width': 1.2 });
    el('circle', { cx: 300, cy: 300, r: 272, fill: 'none', stroke: faint, 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 254, fill: 'none', stroke: faint, 'stroke-width': 1, 'stroke-dasharray': '3 9' });

    // 外圈细齿
    for (var t = 0; t < 48; t++) {
      var ta = t * 7.5 * Math.PI / 180;
      var x1 = 300 + Math.sin(ta) * 274;
      var y1 = 300 - Math.cos(ta) * 274;
      var x2 = 300 + Math.sin(ta) * 283;
      var y2 = 300 - Math.cos(ta) * 283;
      el('line', {
        x1: x1, y1: y1, x2: x2, y2: y2,
        stroke: faint, 'stroke-width': 1
      });
    }

    // 弹膛：只留细描边（内部是真实镂空）
    for (var c2 = 0; c2 < 6; c2++) {
      var ca2 = 30 + c2 * 60;
      var g2 = el('g', { transform: 'rotate(' + ca2 + ' 300 300)' });

      el('circle', {
        cx: 300, cy: 112, r: 56,
        fill: 'none',
        stroke: c2 === 0 ? 'rgba(214, 238, 232, 0.28)' : line,
        'stroke-width': c2 === 0 ? 1.2 : 1.4,
        'stroke-dasharray': c2 === 0 ? '5 6' : 'none'
      }, g2);

      el('circle', {
        cx: 300, cy: 112, r: 44,
        fill: 'none',
        stroke: faint,
        'stroke-width': 1
      }, g2);
    }

    // 辐条细线
    for (var s = 0; s < 6; s++) {
      var sa = 30 + s * 60;
      var sg = el('g', { transform: 'rotate(' + sa + ' 300 300)' });
      el('line', {
        x1: 300, y1: 176, x2: 300, y2: 228,
        stroke: faint, 'stroke-width': 1
      }, sg);
    }

    // 中心轴细线
    el('circle', { cx: 300, cy: 300, r: 74, fill: 'none', stroke: line, 'stroke-width': 1.4 });
    el('circle', { cx: 300, cy: 300, r: 56, fill: 'none', stroke: faint, 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 16, fill: 'none', stroke: line, 'stroke-width': 1.2 });
    el('circle', { cx: 300, cy: 300, r: 4, fill: 'rgba(214, 238, 232, 0.5)' });

    return svg;
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildCylinderSvg() {")
    end = t.find("\n  function buildQingshuLine", start)
    if start < 0 or end < 0:
        print("anchor miss", d)
        continue

    t = t[:start] + new_svg + t[end + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v22" not in ct:
            ct += '''

/* 弹巢 v22：镂空 + 细线 */
.cyl5-wheel {
  left: -4vw !important;
  width: min(50vw, calc(720 * var(--s))) !important;
  height: min(50vw, calc(720 * var(--s))) !important;
  margin-top: calc(-0.5 * min(50vw, calc(720 * var(--s)))) !important;
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.35)) !important;
}

.cyl5-svg {
  opacity: 0.95;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=257", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
