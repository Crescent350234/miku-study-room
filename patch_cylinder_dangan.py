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

    // 蓝色金属渐变
    var defs = el('defs', {});
    var grad = el('radialGradient', { id: 'cylBlue', cx: '38%', cy: '30%', r: '80%' }, defs);
    el('stop', { offset: '0%', 'stop-color': '#5b9be8' }, grad);
    el('stop', { offset: '45%', 'stop-color': '#2f6fd0' }, grad);
    el('stop', { offset: '100%', 'stop-color': '#173a78' }, grad);

    var grad2 = el('linearGradient', { id: 'cylSteel', x1: '0', y1: '0', x2: '0', y2: '1' }, defs);
    el('stop', { offset: '0%', 'stop-color': '#eef3f6' }, grad2);
    el('stop', { offset: '50%', 'stop-color': '#a9b6c2' }, grad2);
    el('stop', { offset: '100%', 'stop-color': '#e6edf2' }, grad2);

    // 转轮主体
    el('circle', { cx: 300, cy: 300, r: 268, fill: 'url(#cylBlue)' });

    // 主体高光
    el('ellipse', { cx: 250, cy: 210, rx: 150, ry: 90, fill: 'rgba(255,255,255,0.10)' });

    // 弹膛之间的凹槽（深色细线）
    for (var f = 0; f < 6; f++) {
      var fa = f * 60 + 30;
      var g = el('g', { transform: 'rotate(' + fa + ' 300 300)' });
      el('rect', {
        x: 296, y: 70, width: 8, height: 200, rx: 4,
        fill: 'rgba(6, 12, 24, 0.28)'
      }, g);
    }

    // 外圈：银环 + 分段缺口
    el('circle', { cx: 300, cy: 300, r: 286, fill: 'none', stroke: 'url(#cylSteel)', 'stroke-width': 20 });
    el('circle', { cx: 300, cy: 300, r: 275, fill: 'none', stroke: 'rgba(10, 16, 24, 0.55)', 'stroke-width': 2 });

    for (var s = 0; s < 12; s++) {
      var sa = s * 30;
      var sg = el('g', { transform: 'rotate(' + sa + ' 300 300)' });
      el('rect', { x: 292, y: 10, width: 16, height: 22, fill: '#0b1119' }, sg);
    }

    // 内圈装饰
    el('circle', { cx: 300, cy: 300, r: 236, fill: 'none', stroke: 'rgba(220, 235, 245, 0.35)', 'stroke-width': 2 });
    el('circle', { cx: 300, cy: 300, r: 224, fill: 'none', stroke: 'rgba(10, 16, 24, 0.35)', 'stroke-width': 1 });

    // 6 个弹膛
    for (var c = 0; c < 6; c++) {
      var ca = 30 + c * 60;
      var cg = el('g', { transform: 'rotate(' + ca + ' 300 300)' });

      el('circle', {
        cx: 300, cy: 112, r: 58,
        fill: c === 0 ? 'rgba(4, 8, 14, 0.55)' : '#05080c',
        stroke: 'url(#cylSteel)', 'stroke-width': 6
      }, cg);

      el('circle', {
        cx: 300, cy: 112, r: 44,
        fill: c === 0 ? 'none' : '#02040a',
        stroke: 'rgba(220, 235, 245, 0.25)', 'stroke-width': 1.5
      }, cg);

      if (c === 0) {
        var dashed = el('circle', {
          cx: 300, cy: 112, r: 58,
          fill: 'none', stroke: 'rgba(230, 242, 250, 0.65)', 'stroke-width': 2,
          'stroke-dasharray': '8 7'
        }, cg);
      }
    }

    // 中心轴
    el('circle', { cx: 300, cy: 300, r: 76, fill: '#1d4488', stroke: 'url(#cylSteel)', 'stroke-width': 8 });
    el('circle', { cx: 300, cy: 300, r: 46, fill: '#0d2148', stroke: 'rgba(230, 240, 248, 0.55)', 'stroke-width': 2 });
    el('circle', { cx: 300, cy: 300, r: 16, fill: '#c9d5de', stroke: '#0b1119', 'stroke-width': 2 });

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
        if "弹巢 v21" not in ct:
            ct += '''

/* 弹巢 v21：弹丸论破风蓝色转轮 */
.cyl5-wheel {
  left: -9vw !important;
  width: min(52vw, calc(760 * var(--s))) !important;
  height: min(52vw, calc(760 * var(--s))) !important;
  margin-top: calc(-0.5 * min(52vw, calc(760 * var(--s)))) !important;
  filter: drop-shadow(0 18px 40px rgba(0, 0, 0, 0.45));
}

.cyl5-svg {
  opacity: 1;
}
'''
            io.open(c, "w", encoding="utf-8", newline="").write(ct)
            print("css", d)

    h = os.path.join(d, "index.html")
    if os.path.exists(h):
        ht = io.open(h, encoding="utf-8").read()
        ht = re.sub(r"js/app\.js\?v=\d+", "js/app.js?v=256", ht)
        io.open(h, "w", encoding="utf-8", newline="").write(ht)
