import io, os, re

dirs = [
    r"D:\MikuWallpaper\wallpaper",
    r"D:\Steam\steamapps\common\wallpaper_engine\projects\myprojects\Miku Study Room",
    r"D:\MikuWallpaper-dist\Miku Study Room\wallpaper",
]

new_fn = r'''  function buildCylinderLine(idx) {
    var layer = $('cylLayer');
    if (!layer) return;
    if (idx < 0 || idx >= S.lrc.length) { layer.innerHTML = ''; return; }

    layer.innerHTML = '';

    var scene = document.createElement('div');
    scene.className = 'cyl5-scene';

    var wheel = document.createElement('div');
    wheel.className = 'cyl5-wheel';
    wheel.appendChild(buildCylinderSvg());
    scene.appendChild(wheel);

    var pointer = document.createElement('div');
    pointer.className = 'cyl5-pointer';
    scene.appendChild(pointer);

    var list = document.createElement('div');
    list.className = 'cyl5-list';

    for (var k = idx - 1; k <= idx + 1; k++) {
      if (k < 0 || k >= S.lrc.length) continue;
      var line = S.lrc[k];
      if (!line || !line.text) continue;

      var row = document.createElement('div');
      row.className = 'cyl5-row' + (k === idx ? ' current' : '');

      var t = document.createElement('div');
      t.className = 'cyl5-text';
      t.textContent = line.text;
      row.appendChild(t);

      if (k === idx && line.sub) {
        var sb = document.createElement('div');
        sb.className = 'cyl5-sub';
        sb.textContent = line.sub;
        row.appendChild(sb);
      }

      list.appendChild(row);
    }

    scene.appendChild(list);
    layer.appendChild(scene);
  }

  function buildCylinderSvg() {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 600 600');
    svg.setAttribute('class', 'cyl5-svg');

    function el(tag, attrs) {
      var n = document.createElementNS(NS, tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      svg.appendChild(n);
      return n;
    }

    function line(x1, y1, x2, y2, op, w) {
      return el('line', {
        x1: x1, y1: y1, x2: x2, y2: y2,
        stroke: 'rgba(196, 234, 227, ' + op + ')',
        'stroke-width': w || 1
      });
    }

    // 外圈
    el('circle', { cx: 300, cy: 300, r: 286, fill: 'none', stroke: 'rgba(196, 234, 227, 0.30)', 'stroke-width': 1.2 });
    el('circle', { cx: 300, cy: 300, r: 274, fill: 'none', stroke: 'rgba(196, 234, 227, 0.14)', 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 252, fill: 'none', stroke: 'rgba(196, 234, 227, 0.10)', 'stroke-width': 1 });

    // 棘轮齿
    for (var r = 0; r < 48; r++) {
      var ra = r * 7.5;
      var rad = ra * Math.PI / 180;
      var x1 = 300 + Math.sin(rad) * 266;
      var y1 = 300 - Math.cos(rad) * 266;
      var x2 = 300 + Math.sin(rad) * 282;
      var y2 = 300 - Math.cos(rad) * 282;
      line(x1, y1, x2, y2, 0.20, 1);
    }

    // 凹槽
    for (var f = 0; f < 6; f++) {
      var fa = 30 + f * 60 + 30;
      var g = el('g', { transform: 'rotate(' + fa + ' 300 300)' });
      var rect = document.createElementNS(NS, 'rect');
      rect.setAttribute('x', 270);
      rect.setAttribute('y', 128);
      rect.setAttribute('width', 60);
      rect.setAttribute('height', 120);
      rect.setAttribute('rx', 30);
      rect.setAttribute('fill', 'rgba(196, 234, 227, 0.025)');
      rect.setAttribute('stroke', 'rgba(196, 234, 227, 0.18)');
      rect.setAttribute('stroke-width', '1');
      g.appendChild(rect);
    }

    // 6 个弹膛
    for (var c = 0; c < 6; c++) {
      var ca = 30 + c * 60;
      var cg = el('g', { transform: 'rotate(' + ca + ' 300 300)' });

      var outer = document.createElementNS(NS, 'circle');
      outer.setAttribute('cx', 300);
      outer.setAttribute('cy', 112);
      outer.setAttribute('r', 56);
      outer.setAttribute('fill', c === 0 ? 'none' : 'rgba(8, 16, 15, 0.55)');
      outer.setAttribute('stroke', c === 0 ? 'rgba(196, 234, 227, 0.22)' : 'rgba(196, 234, 227, 0.42)');
      outer.setAttribute('stroke-width', '1.2');
      if (c === 0) outer.setAttribute('stroke-dasharray', '6 6');
      cg.appendChild(outer);

      var inner = document.createElementNS(NS, 'circle');
      inner.setAttribute('cx', 300);
      inner.setAttribute('cy', 112);
      inner.setAttribute('r', 42);
      inner.setAttribute('fill', 'none');
      inner.setAttribute('stroke', 'rgba(196, 234, 227, 0.22)');
      inner.setAttribute('stroke-width', '1');
      cg.appendChild(inner);

      var pin = document.createElementNS(NS, 'circle');
      pin.setAttribute('cx', 300);
      pin.setAttribute('cy', 112);
      pin.setAttribute('r', 9);
      pin.setAttribute('fill', c === 0 ? 'none' : 'rgba(196, 234, 227, 0.10)');
      pin.setAttribute('stroke', 'rgba(196, 234, 227, 0.35)');
      pin.setAttribute('stroke-width', '1');
      cg.appendChild(pin);
    }

    // 辐条
    for (var s = 0; s < 6; s++) {
      var sa = 30 + s * 60;
      var sg = el('g', { transform: 'rotate(' + sa + ' 300 300)' });
      var l = document.createElementNS(NS, 'line');
      l.setAttribute('x1', 300);
      l.setAttribute('y1', 180);
      l.setAttribute('x2', 300);
      l.setAttribute('y2', 236);
      l.setAttribute('stroke', 'rgba(196, 234, 227, 0.20)');
      l.setAttribute('stroke-width', '1');
      sg.appendChild(l);
    }

    // 中心轴
    el('circle', { cx: 300, cy: 300, r: 78, fill: 'rgba(8, 16, 15, 0.35)', stroke: 'rgba(196, 234, 227, 0.26)', 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 52, fill: 'none', stroke: 'rgba(196, 234, 227, 0.18)', 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 18, fill: 'none', stroke: 'rgba(196, 234, 227, 0.38)', 'stroke-width': 1 });
    el('circle', { cx: 300, cy: 300, r: 4, fill: 'rgba(196, 234, 227, 0.5)' });

    // 中心螺丝位
    for (var b = 0; b < 6; b++) {
      var ba = b * 60;
      var bg = el('g', { transform: 'rotate(' + ba + ' 300 300)' });
      var bolt = document.createElementNS(NS, 'circle');
      bolt.setAttribute('cx', 300);
      bolt.setAttribute('cy', 258);
      bolt.setAttribute('r', 5);
      bolt.setAttribute('fill', 'none');
      bolt.setAttribute('stroke', 'rgba(196, 234, 227, 0.30)');
      bolt.setAttribute('stroke-width', '1');
      bg.appendChild(bolt);
    }

    return svg;
  }

'''

for d in dirs:
    p = os.path.join(d, "js", "app.js")
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()

    start = t.find("  function buildCylinderLine(idx) {")
    end = t.find("\n  function buildQingshuLine", start)
    if start < 0 or end < 0:
        print("anchor miss", d)
        continue

    t = t[:start] + new_fn + t[end + 1:]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("js", d)

    c = os.path.join(d, "css", "style.css")
    if os.path.exists(c):
        ct = io.open(c, encoding="utf-8").read()
        if "弹巢 v18" not in ct:
            ct += '''

/* 弹巢 v18：SVG 机械转轮 */
.cyl5-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
}

.cyl5-rings,
.cyl5-chambers,
.cyl5-core,
.cyl5-hub {
  display: none;
}

.cyl5-wheel {
  border: none !important;
  background: radial-gradient(circle at 50% 50%, rgba(10, 24, 26, 0.35), rgba(5, 12, 14, 0.05) 70%) !important;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=253", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
