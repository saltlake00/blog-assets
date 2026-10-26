/* 발표 도표. index.html 본 스크립트 뒤에 읽는다(.media 칸의 _m을 쓴다).
   값 출처: 도표-기획.md §3 (2026-10-27 00:50 실측). */
(function () {
  var SVGNS = 'http://www.w3.org/2000/svg';
  var EL = { fire: '화염', ice: '얼음', bolt: '전기', light: '빛', earth: '땅' };

  /* ── 공통 툴팁 ── */
  var tip = document.createElement('div'); tip.id = 'viz-tip'; document.body.appendChild(tip);
  function showTip(e, html) { tip.innerHTML = html; tip.style.display = 'block'; moveTip(e); }
  function moveTip(e) {
    var x = e.clientX + 14, y = e.clientY + 14, w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > innerWidth - 8) x = e.clientX - w - 14;
    if (y + h > innerHeight - 8) y = e.clientY - h - 14;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tip.style.display = 'none'; }
  function bindTip(node, html) {
    node.addEventListener('mouseenter', function (e) { showTip(e, html); });
    node.addEventListener('mousemove', moveTip);
    node.addEventListener('mouseleave', hideTip);
  }
  function s(tag, attrs, parent) {
    var n = document.createElementNS(SVGNS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  /* ── 예고 범위 모양 아이콘 ── */
  function shapeSvg(shape) {
    var v = '<svg viewBox="0 0 40 40" aria-hidden="true">';
    var st = 'fill="currentColor" fill-opacity=".28" stroke="currentColor" stroke-width="2"';
    if (shape === '원') v += '<circle cx="20" cy="20" r="15" ' + st + '/>';
    else if (shape === '직선') v += '<rect x="4" y="14" width="32" height="12" rx="2" ' + st + '/>';
    else if (shape === '도넛') v += '<path fill-rule="evenodd" d="M20 4a16 16 0 1 0 .01 0zM20 12a8 8 0 1 1-.01 0z" ' + st + '/>';
    else if (shape === '방사') for (var i = 0; i < 6; i++) v += '<rect x="18" y="3" width="4" height="17" rx="1" transform="rotate(' + (i * 60) + ' 20 20)" ' + st + '/>';
    return v + '</svg>';
  }

  /* ── 보스 6종: 약점·저항·예고 범위 (보스 정의 SO) ── */
  var BOSSES = [
    { name: '보스 큐브', k: '보스큐브', ph: '05-예고1', weak: null, res: null, pats: [['충격파', '원'], ['내려찍기', '원']] },
    { name: '얼음 결정탑', k: '얼음결정탑', ph: '05-예고2', weak: 'fire', res: 'ice', pats: [['직선강타', '직선'], ['고리폭발', '도넛']] },
    { name: '전기 코어', k: '전기코어', ph: '04-보스전', weak: 'earth', res: 'bolt', pats: [['방사줄기', '방사'], ['연쇄낙뢰', '원']] },
    { name: '용암 핵', k: '용암핵', ph: '04-보스전', weak: 'ice', res: 'fire', pats: [['용암분출', '원'], ['열파고리', '도넛']] },
    { name: '자이로스코프', k: '자이로스코프', ph: '04-보스전', weak: 'bolt', res: 'light', pats: [['직선강타', '직선'], ['충격파', '원']], reuse: true },
    { name: '문양 기둥', k: '문양기둥', ph: '04-보스전', weak: 'light', res: 'earth', pats: [['내려찍기', '원'], ['고리폭발', '도넛']], reuse: true }
  ];
  function elChip(el, mult, cls) {
    if (!el) return '<span class="vz-el none">없음</span>';
    return '<span class="vz-el ' + cls + '"><i style="background:var(--' + el + ')"></i>' + EL[el] + ' <b>×' + mult + '</b></span>';
  }
  function renderBoss(root) {
    var slide = root.closest('.slide');
    var mediaEl = slide.querySelector('.media');
    var html = '<div class="vz-bh"><span>보스</span><span>약점</span><span>저항</span><span>예고 범위</span></div>';
    BOSSES.forEach(function (b, i) {
      html += '<div class="vz-brow' + (i === 0 ? ' on' : '') + '" data-i="' + i + '">' +
        '<b class="nm">' + b.name + '</b>' + elChip(b.weak, '1.5', 'weak') + elChip(b.res, '0.5', 'res') + '<span class="pats">';
      b.pats.forEach(function (p, j) {
        html += '<button class="vz-pat' + (i === 0 && j === 0 ? ' on' : '') + '" data-j="' + j + '" aria-label="' + p[0] + '">' + shapeSvg(p[1]) + '</button>';
      });
      html += (b.reuse ? '<em>재사용</em>' : '') + '</span></div>';
    });
    html += '<div class="vz-legend">' + ['원', '직선', '도넛', '방사'].map(function (sh) { return '<span>' + shapeSvg(sh) + sh + '</span>'; }).join('') + '</div>';
    root.innerHTML = html;
    function pick(i, j) {
      var b = BOSSES[i], p = b.pats[j];
      Array.prototype.forEach.call(root.querySelectorAll('.vz-brow'), function (r) { r.classList.toggle('on', +r.getAttribute('data-i') === i); });
      Array.prototype.forEach.call(root.querySelectorAll('.vz-pat'), function (x) {
        x.classList.toggle('on', +x.closest('.vz-brow').getAttribute('data-i') === i && +x.getAttribute('data-j') === j);
      });
      if (mediaEl && mediaEl._m) mediaEl._m.set('05-' + b.k + '-' + p[0], b.ph);
    }
    Array.prototype.forEach.call(root.querySelectorAll('.vz-brow'), function (r) {
      var i = +r.getAttribute('data-i');
      r.addEventListener('click', function (e) {
        var pb = e.target.closest('.vz-pat');
        pick(i, pb ? +pb.getAttribute('data-j') : 0);
      });
      Array.prototype.forEach.call(r.querySelectorAll('.vz-pat'), function (pb) {
        var p = BOSSES[i].pats[+pb.getAttribute('data-j')];
        bindTip(pb, '<b>' + p[0] + '</b> · ' + p[1] + ' 예고');
      });
    });
  }

  /* ── 일별 커밋 (origin/main, 작성일 기준) ── */
  var COMMITS = [8, 31, 43, 84, 56, 39, 64, 51, 70, 78, 75, 119, 67, 85, 130, 91, 105, 55, 23, 4, 130, 190, 87, 72, 76, 18, 136, 178, 3];
  var PRS = [0, 0, 2, 15, 15, 11, 18, 7, 11, 20, 16, 30, 13, 12, 19, 12, 10, 12, 5, 1, 20, 28, 11, 13, 12, 3, 26, 29, 3];
  var START = new Date(2026, 8, 29);
  var PHASES = [['MVP', 0, 9], ['CBT', 10, 17], ['다듬기', 18, 25], ['발표 준비', 26, 28]];
  function day(i) { var d = new Date(START); d.setDate(d.getDate() + i); return (d.getMonth() + 1) + '/' + d.getDate(); }
  function renderCommits(root) {
    var W = 1040, H = 400, L = 48, R = 12, T = 56, B = 40;
    var n = COMMITS.length, max = 200, cw = (W - L - R) / n, bw = Math.max(6, cw - 8);
    var y = function (v) { return T + (H - T - B) * (1 - v / max); };
    var svg = s('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': '일별 커밋 막대 그래프' });
    PHASES.forEach(function (p, k) {
      var x0 = L + p[1] * cw, x1 = L + (p[2] + 1) * cw;
      if (k % 2 === 0) s('rect', { x: x0, y: T - 40, width: x1 - x0, height: H - T - B + 40, fill: 'var(--card)' }, svg);
      var t = s('text', { x: x0 + 10, y: T - 14, 'font-size': 20, 'font-weight': 700, fill: 'var(--muted)' }, svg);
      t.textContent = p[0];
    });
    [0, 100, 200].forEach(function (v) {
      s('line', { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: 'var(--line-subtle)', 'stroke-width': 1 }, svg);
      var t = s('text', { x: L - 10, y: y(v) + 6, 'font-size': 16, fill: 'var(--muted)', 'text-anchor': 'end' }, svg); t.textContent = v;
    });
    var full = COMMITS.slice(0, n - 1), avg = full.reduce(function (a, b) { return a + b; }, 0) / full.length;
    COMMITS.forEach(function (v, i) {
      var x = L + i * cw + (cw - bw) / 2, h = Math.max(2, y(0) - y(v));
      var r = s('rect', { x: x, y: y(0) - h, width: bw, height: h, rx: 3, fill: 'var(--accent)', 'fill-opacity': i === n - 1 ? .4 : 1 }, svg);
      var hit = s('rect', { x: L + i * cw, y: T - 40, width: cw, height: H - T - B + 40, fill: 'transparent' }, svg);
      bindTip(hit, '<b>' + day(i) + '</b> · 커밋 ' + v + ' · 병합 PR ' + PRS[i] + (i === n - 1 ? ' (00:50까지)' : ''));
      hit.addEventListener('mouseenter', function () { r.setAttribute('fill', 'var(--accent-bright)'); });
      hit.addEventListener('mouseleave', function () { r.setAttribute('fill', 'var(--accent)'); });
      if (v === Math.max.apply(null, COMMITS)) {
        var t = s('text', { x: x + bw / 2, y: y(v) - 8, 'font-size': 20, 'font-weight': 700, fill: 'var(--ink)', 'text-anchor': 'middle' }, svg); t.textContent = v;
      }
      if (i % 7 === 0 || i === n - 1) {
        var d = s('text', { x: x + bw / 2, y: H - B + 26, 'font-size': 16, fill: 'var(--muted)', 'text-anchor': 'middle' }, svg); d.textContent = day(i);
      }
    });
    s('line', { x1: L, x2: W - R, y1: y(avg), y2: y(avg), stroke: 'var(--ink)', 'stroke-width': 2, 'stroke-dasharray': '6 6', 'pointer-events': 'none' }, svg);
    var a = s('text', { x: L + 8, y: y(avg) - 10, 'font-size': 18, 'font-weight': 700, fill: 'var(--ink)' }, svg);
    a.textContent = '하루 평균 ' + Math.round(avg);
    root.appendChild(svg);
  }

  var R = { boss: renderBoss, commits: renderCommits };
  Array.prototype.forEach.call(document.querySelectorAll('[data-viz]'), function (el) {
    var f = R[el.getAttribute('data-viz')]; if (f) f(el);
  });
})();
