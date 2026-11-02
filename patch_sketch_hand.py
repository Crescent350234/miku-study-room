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

    function noise(seed) {
      var x = Math.sin(seed * 12.9898) * 43758.5453;
      return x - Math.floor(x);
    }

    function roughCircle(cx, cy, r, seed, seg) {
      var pts = [];
      seg = seg || 72;
      for (var i = 0; i < seg; i++) {
        var a = i / seg * Math.PI * 2;
        var rr = r + (noise(seed + i * 7.3) - 0.5) * 3.2;
        pts.push([cx + Math.sin(a) * rr, cy - Math.cos(a) * rr]);
      }
      var d = 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1);
      for (var p = 1; p < pts.length; p++) d += ' L' + pts[p][0].toFixed(1) + ' ' + pts[p][1].toFixed(1);
      return d + ' Z';
    }

    function gearPoints(cx, cy, rRoot, rOut, teeth, seed) {
      var pts = [];
      var step = Math.PI * 2 / teeth;
      for (var i = 0; i < teeth; i++) {
        var a = i * step;
        var defs = [
          [a, rRoot], [a + step * 0.24, rRoot], [a + step * 0.32, rOut],
          [a + step * 0.68, rOut], [a + step * 0.76, rRoot], [a + step, rRoot]
        ];
        for (var k = 0; k < defs.length; k++) {
          var ang = defs[k][0];
          var rad = defs[k][1] + (noise(seed + i * 11 + k * 3.7) - 0.5) * 2.4;
          pts.push([cx + Math.sin(ang) * rad, cy - Math.cos(ang) * rad]);
        }
      }
      return pts;
    }

    function ptsToPath(pts) {
      var d = 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1);
      for (var i = 1; i < pts.length; i++) d += ' L' + pts[i][0].toFixed(1) + ' ' + pts[i][1].toFixed(1);
      return d + ' Z';
    }

    var line = 'rgba(226, 224, 214, 0.88)';
    var soft = 'rgba(226, 224, 214, 0.34)';
    var gearPts = gearPoints(300, 300, 268, 292, 24, 3.1);
    var gear = ptsToPath(gearPts);

    var defs = el('defs', {});

    var mask = el('mask', { id: 'cylHollow', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 600, height: 600 }, defs);
    el('path', { d: gear, fill: '#fff' }, mask);
    for (var c = 0; c < 6; c++) {
      var ca = 30 + c * 60;
      var cg = el('g', { transform: 'rotate(' + ca + ' 300 300)' }, mask);
      el('circle', { cx: 300, cy: 112, r: 55, fill: '#000' }, cg);
    }
    el('circle', { cx: 300, cy: 300, r: 73, fill: '#000' }, mask);

    // 轮体：深色，接近不透明
    el('path', { d: gear, fill: 'rgba(17, 18, 17, 0.82)', mask: 'url(#cylHollow)' });

    // 手绘外轮廓：两遍
    el('path', { d: gear, fill: 'none', stroke: line, 'stroke-width': 1.5, 'stroke-linejoin': 'round' });
    el('path', {
      d: gear, fill: 'none', stroke: soft, 'stroke-width': 1,
      transform: 'translate(1.4 1.1)'
    });

    // 排线阴影（两方向）
    var clip = el('clipPath', { id: 'cylBodyClip' }, defs);
    el('path', { d: gear, fill: '#fff' }, clip);

    var hatch = el('g', { 'clip-path': 'url(#cylBodyClip)', mask: 'url(#cylHollow)' });
    for (var h = 0; h < 40; h++) {
      el('line', {
        x1: -80 + h * 13, y1: -20,
        x2: -80 + h * 13 + 430, y2: 640,
        stroke: 'rgba(222, 220, 210, 0.10)', 'stroke-width': 1
      }, hatch);
    }
    for (var h2 = 0; h2 < 26; h2++) {
      el('line', {
        x1: -20 + h2 * 20, y1: 620,
        x2: -20 + h2 * 20 + 260, y2: -20,
        stroke: 'rgba(222, 220, 210, 0.06)', 'stroke-width': 1
      }, hatch);
    }

    // 内圈手绘线
    el('path', { d: roughCircle(300, 300, 244, 9.2), fill: 'none', stroke: soft, 'stroke-width': 1 });
    el('path', { d: roughCircle(300, 300, 228, 13.7), fill: 'none', stroke: soft, 'stroke-width': 1, 'stroke-dasharray': '4 7' });

    // 弹膛：手绘双圈
    for (var c2 = 0; c2 < 6; c2++) {
      var ca2 = 30 + c2 * 60;
      var g2 = el('g', { transform: 'rotate(' + ca2 + ' 300 300)' });
      var dash = c2 === 0 ? '6 6' : 'none';
      el('path', {
        d: roughCircle(300, 112, 55, 21 + c2 * 3.3),
        fill: 'none', stroke: line, 'stroke-width': 1.6, 'stroke-dasharray': dash
      }, g2);
      el('path', {
        d: roughCircle(300, 112, 55, 21 + c2 * 3.3),
        fill: 'none', stroke: soft, 'stroke-width': 1,
        transform: 'translate(1.6 1.2)'
      }, g2);
      el('path', {
        d: roughCircle(300, 112, 43, 31 + c2 * 3.3),
        fill: 'none', stroke: soft, 'stroke-width': 1
      }, g2);
    }

    // 辐条
    for (var s = 0; s < 6; s++) {
      var sa = 30 + s * 60;
      var sg = el('g', { transform: 'rotate(' + sa + ' 300 300)' });
      el('line', { x1: 300, y1: 176, x2: 300, y2: 222, stroke: soft, 'stroke-width': 1 }, sg);
    }

    // 中心小齿轮
    var hub = ptsToPath(gearPoints(300, 300, 76, 88, 12, 41.7));
    el('path', { d: hub, fill: 'none', stroke: line, 'stroke-width': 1.3 });
    el('path', { d: hub, fill: 'none', stroke: soft, 'stroke-width': 1, transform: 'translate(1.2 1)' });
    el('path', { d: roughCircle(300, 300, 55, 55.5), fill: 'none', stroke: soft, 'stroke-width': 1 });
    el('path', { d: roughCircle(300, 300, 16, 61.1), fill: 'none', stroke: line, 'stroke-width': 1.2 });
    el('circle', { cx: 300, cy: 300, r: 4, fill: 'rgba(230, 228, 218, 0.75)' });

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
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=262", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
