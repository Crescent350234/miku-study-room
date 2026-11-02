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

    function gearPath(cx, cy, rRoot, rOut, teeth) {
      var parts = [];
      var step = Math.PI * 2 / teeth;
      for (var i = 0; i < teeth; i++) {
        var a = i * step;
        var pts = [
          [a, rRoot],
          [a + step * 0.22, rRoot],
          [a + step * 0.30, rOut],
          [a + step * 0.70, rOut],
          [a + step * 0.78, rRoot],
          [a + step, rRoot]
        ];
        for (var p = 0; p < pts.length; p++) {
          var ang = pts[p][0];
          var rad = pts[p][1];
          var x = cx + Math.sin(ang) * rad;
          var y = cy - Math.cos(ang) * rad;
          parts.push((i === 0 && p === 0 ? 'M' : 'L') + x.toFixed(2) + ' ' + y.toFixed(2));
        }
      }
      parts.push('Z');
      return parts.join(' ');
    }

    var line = 'rgba(214, 238, 232, 0.45)';
    var faint = 'rgba(214, 238, 232, 0.16)';
    var gear = gearPath(300, 300, 268, 292, 24);

    var defs = el('defs', {});

    var mask = el('mask', { id: 'cylHollow', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 600, height: 600 }, defs);
    el('path', { d: gear, fill: '#fff' }, mask);

    // 弹膛镂空
    for (var c = 0; c < 6; c++) {
      var ca = 30 + c * 60;
      var cg = el('g', { transform: 'rotate(' + ca + ' 300 300)' }, mask);
      el('circle', { cx: 300, cy: 112, r: 56, fill: '#000' }, cg);
    }

    // 中心轴镂空
    el('circle', { cx: 300, cy: 300, r: 74, fill: '#000' }, mask);

    // 齿轮轮体（镂空）
    el('path', { d: gear, fill: 'rgba(8, 18, 20, 0.46)', mask: 'url(#cylHollow)' });

    // 齿轮轮廓
    el('path', { d: gear, fill: 'none', stroke: line, 'stroke-width': 1.2 });

    // 内圈细线
    el('circle', { cx: 300, cy: 300, r: 244, fill: 'none', stroke: faint, 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 228, fill: 'none', stroke: faint, 'stroke-width': 1, 'stroke-dasharray': '3 9' });

    // 弹膛细描边
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

      el('circle', { cx: 300, cy: 112, r: 44, fill: 'none', stroke: faint, 'stroke-width': 1 }, g2);
    }

    // 辐条细线
    for (var s = 0; s < 6; s++) {
      var sa = 30 + s * 60;
      var sg = el('g', { transform: 'rotate(' + sa + ' 300 300)' });
      el('line', { x1: 300, y1: 176, x2: 300, y2: 222, stroke: faint, 'stroke-width': 1 }, sg);
    }

    // 中心齿轮
    var hubGear = gearPath(300, 300, 76, 88, 12);
    el('path', { d: hubGear, fill: 'none', stroke: line, 'stroke-width': 1.2 });
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

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=258", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
