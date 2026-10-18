// Visual layer for the case study and evidence pages: scroll reveals, the animated
// studio, data-driven mini charts with tooltips, the tenure explorer and the
// overbooking simulator. All numbers come from the lab's aggregated outputs or
// from the cited papers; illustrative assumptions are labelled as such on the page.
(function(){
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lang = () => document.documentElement.lang === 'es' ? 'es' : 'en';
  const T = (en, es) => lang() === 'es' ? es : en;
  const fmt = (x, d = 1) => {
    const s = x.toFixed(d);
    return lang() === 'es' ? s.replace('.', ',') : s;
  };
  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for(const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if(parent) parent.appendChild(n);
    return n;
  };
  const text = (parent, x, y, str, cls, anchor = 'start') => {
    const t = el('text', {x, y, class: cls, 'text-anchor': anchor}, parent);
    t.textContent = str; return t;
  };
  const renderers = [];       // charts with language-dependent labels
  const onLang = fn => { renderers.push(fn); fn(); };
  document.addEventListener('ccl:lang', () => renderers.forEach(fn => fn()));

  /* ---------- Scroll progress ---------- */
  const bar = document.querySelector('.progress');
  if(bar){
    const upd = () => { const h = document.documentElement; const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight); bar.style.transform = `scaleX(${p})`; };
    addEventListener('scroll', upd, {passive:true}); upd();
  }

  /* ---------- Reveal + count-up ---------- */
  function countUp(node){
    const to = parseFloat(node.dataset.count), dec = +(node.dataset.dec || 0), pre = node.dataset.pre || '', suf = node.dataset.suf || '';
    const out = v => { node.textContent = pre + (dec ? fmt(v, dec) : Math.round(v).toLocaleString(lang() === 'es' ? 'es-ES' : 'en-US')) + suf; };
    if(reduce){ out(to); return; }
    const t0 = performance.now(), dur = 1400;
    const step = t => { const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3); out(to * e); if(k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  const io = new IntersectionObserver(entries => {
    for(const e of entries){
      if(!e.isIntersecting) continue;
      const n = e.target;
      n.classList.add('in');
      if(n.dataset.count) countUp(n);
      n.querySelectorAll('[data-to]').forEach(d => { d.style.left = d.dataset.to; });
      io.unobserve(n);
    }
  }, {threshold: 0.25, rootMargin: '0px 0px -40px 0px'});
  function watch(root = document){
    root.querySelectorAll('.reveal,.anim-bars,.split-bar,.dumbbell,.viz,.steps.stagger,[data-count]').forEach(n => {
      n.querySelectorAll('[data-to]').forEach(d => { d.dataset.final = d.style.left; d.style.left = d.dataset.from; });
      io.observe(n);
    });
  }
  document.addEventListener('ccl:lang', () => document.querySelectorAll('[data-count].in').forEach(n => {
    const dec = +(n.dataset.dec || 0), v = parseFloat(n.dataset.count);
    n.textContent = (n.dataset.pre || '') + (dec ? fmt(v, dec) : Math.round(v).toLocaleString(lang() === 'es' ? 'es-ES' : 'en-US')) + (n.dataset.suf || '');
  }));

  /* ---------- Tooltip helper ---------- */
  function tooltip(host){
    const tip = document.createElement('div'); tip.className = 'tip'; host.appendChild(tip);
    return {
      show(html, x, y){ tip.innerHTML = html; tip.style.left = x + 'px'; tip.style.top = y + 'px'; tip.classList.add('on'); },
      hide(){ tip.classList.remove('on'); }
    };
  }
  function bindTip(target, host, tip, html){
    const place = () => {
      const r = target.getBoundingClientRect(), h = host.getBoundingClientRect();
      tip.show(html(), r.left + r.width / 2 - h.left, r.top - h.top);
    };
    target.addEventListener('mouseenter', place); target.addEventListener('focus', place);
    target.addEventListener('mouseleave', tip.hide); target.addEventListener('blur', tip.hide);
    target.addEventListener('touchstart', place, {passive:true});
  }

  /* ---------- Studio: 40 booked places, 12 attended (30% ≈ 30.3%) ---------- */
  const studio = document.getElementById('studio-svg');
  if(studio){
    const cols = 8, rows = 5, w = 36, h = 44, gx = 12, gy = 12, x0 = 24, y0 = 60;
    const attended = new Set([1, 4, 6, 10, 13, 19, 22, 25, 28, 31, 35, 38]);
    el('rect', {x: 4, y: 4, width: 412, height: 336, rx: 14, class: 'studio-floor'}, studio);
    el('rect', {x: 150, y: 14, width: 120, height: 28, rx: 6, class: 'stage'}, studio);
    text(studio, 210, 32, 'COACH', 'stage-text', 'middle');
    el('circle', {cx: 176, cy: 28, r: 5, class: 'coach'}, studio);
    const seats = [];
    for(let i = 0; i < cols * rows; i++){
      const c = i % cols, r = Math.floor(i / cols), x = x0 + c * (w + gx), y = y0 + r * (h + gy);
      const mat = el('rect', {x, y, width: w, height: h, rx: 7, class: 'mat'}, studio);
      let person = null;
      if(attended.has(i)){
        person = el('g', {class: 'person'}, studio);
        el('circle', {cx: x + w / 2, cy: y + 14, r: 6}, person);
        el('rect', {x: x + w / 2 - 9, y: y + 22, width: 18, height: 16, rx: 6}, person);
      }
      seats.push({mat, person, att: attended.has(i)});
    }
    const cB = document.getElementById('c-booked'), cA = document.getElementById('c-att'), cE = document.getElementById('c-empty');
    const dots = document.querySelectorAll('.phase i');
    const setPhase = k => dots.forEach((d, i) => d.classList.toggle('on', i <= k));
    const setCounts = (b, a, e) => { cB.textContent = b; cA.textContent = a; cE.textContent = e; };
    const finalState = () => { seats.forEach(s => { s.mat.setAttribute('class', 'mat ' + (s.att ? 'booked' : 'empty')); if(s.person) s.person.classList.add('in'); }); setCounts(40, 12, 28); setPhase(2); };
    if(reduce){ finalState(); }
    else{
      let timers = [], running = false;
      const later = (fn, ms) => timers.push(setTimeout(fn, ms));
      const cycle = () => {
        timers.forEach(clearTimeout); timers = [];
        seats.forEach(s => { s.mat.setAttribute('class', 'mat'); if(s.person) s.person.classList.remove('in'); });
        setCounts(0, 0, 0); setPhase(-1);
        let t = 400;
        later(() => setPhase(0), t);
        seats.forEach((s, i) => later(() => { s.mat.setAttribute('class', 'mat booked'); setCounts(i + 1, 0, 0); }, t + i * 45));
        t += 40 * 45 + 1100;
        later(() => setPhase(1), t);
        let a = 0, e = 0;
        const order = seats.map((s, i) => i).sort((p, q) => ((p * 37) % 40) - ((q * 37) % 40));
        order.forEach((i, k) => later(() => {
          const s = seats[i];
          if(s.att){ s.person.classList.add('in'); a++; } else { s.mat.setAttribute('class', 'mat empty'); e++; }
          setCounts(40, a, e);
        }, t + k * 70));
        t += 40 * 70 + 600;
        later(() => setPhase(2), t);
        later(() => { if(running) cycle(); }, t + 3800);
      };
      new IntersectionObserver(([e]) => {
        if(e.isIntersecting && !running){ running = true; cycle(); }
        else if(!e.isIntersecting && running){ running = false; timers.forEach(clearTimeout); finalState(); }
      }, {threshold: 0.3}).observe(studio);
    }
  }

  /* ---------- Tenure explorer ---------- */
  const explorer = document.getElementById('explorer');
  if(explorer){
    const bands = [
      {en: '1–6 months', es: '1–6 meses', r: 3.4, n: 266},
      {en: '7–12 months', es: '7–12 meses', r: 15.2, n: 513},
      {en: '13–24 months', es: '13–24 meses', r: 40.3, n: 496},
      {en: '25–48 months', es: '25–48 meses', r: 69.4, n: 183},
      {en: '49+ months', es: '49+ meses', r: 95.2, n: 42},
    ];
    const crowd = explorer.querySelector('.crowd'), big = explorer.querySelector('.big'), cap = explorer.querySelector('.crowd-cap');
    const range = explorer.querySelector('input'), ticks = explorer.querySelectorAll('.ticks button');
    const people = [];
    for(let i = 0; i < 20; i++){
      const s = el('svg', {viewBox: '0 0 20 30', 'aria-hidden': 'true'}, crowd);
      const g = el('g', {class: 'p'}, s);
      el('circle', {cx: 10, cy: 6, r: 5}, g); el('rect', {x: 2, y: 13, width: 16, height: 17, rx: 6}, g);
      people.push(g);
    }
    let shown = 0, raf = 0;
    const set = (k, user) => {
      const b = bands[k], on = Math.max(1, Math.round(b.r / 5));
      range.value = k;
      ticks.forEach((t, i) => t.classList.toggle('on', i === k));
      people.forEach((p, i) => setTimeout(() => p.classList.toggle('on', i < on), reduce ? 0 : i * 25));
      cap.textContent = T(`Of 20 bookings by members with ${b.en} of tenure, about ${on} end in attendance (observed ${fmt(b.r)}%, n = ${b.n}).`,
                          `De 20 reservas de socios con ${b.es} de antigüedad, unas ${on} terminan en asistencia (observado ${fmt(b.r)}%, n = ${b.n}).`);
      cancelAnimationFrame(raf);
      const from = shown, to = b.r, t0 = performance.now();
      const step = t => { const q = reduce ? 1 : Math.min(1, (t - t0) / 600); shown = from + (to - from) * (1 - Math.pow(1 - q, 3)); big.textContent = fmt(shown) + '%'; if(q < 1) raf = requestAnimationFrame(step); };
      raf = requestAnimationFrame(step);
      if(user) autoplay = false;
    };
    let autoplay = !reduce, current = 0;
    range.addEventListener('input', () => set(+range.value, true));
    ticks.forEach((t, i) => t.addEventListener('click', () => set(i, true)));
    onLang(() => set(+range.value));
    new IntersectionObserver(([e], obs) => {
      if(!e.isIntersecting) return;
      obs.disconnect();
      if(!autoplay) return;
      const tick = () => { if(!autoplay || current >= 4) return; current++; set(current); setTimeout(tick, 1300); };
      setTimeout(tick, 900);
    }, {threshold: 0.5}).observe(explorer);
  }

  /* ---------- Mini charts (case study) ---------- */
  function leadTime(host){
    const data = [[1,10,5],[2,200,56],[3,32,7],[4,157,49],[5,31,10],[6,73,18],[7,39,7],[8,195,64],[9,24,9],[10,299,92],[11,26,8],[12,181,53],[13,26,6],[14,175,56],[15,24,12]];
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 210', role: 'img', 'aria-label': T('Attendance rate by booking lead time, days 1 to 15; points sized by number of bookings. No trend.', 'Tasa de asistencia según días de anticipación, días 1 a 15; puntos según número de reservas. Sin tendencia.')});
      host.prepend(s);
      const X = d => 34 + (d - 1) / 14 * 266, Y = r => 172 - r / 0.6 * 150;
      [0, 0.2, 0.4, 0.6].forEach(v => { el('line', {x1: 34, x2: 304, y1: Y(v), y2: Y(v), class: 'ax'}, s); text(s, 28, Y(v) + 4, Math.round(v * 100) + '%', 'ax-text', 'end'); });
      [1, 5, 10, 15].forEach(d => text(s, X(d), 190, d, 'ax-text', 'middle'));
      text(s, 167, 206, T('Days booked ahead', 'Días de anticipación'), 'ax-text', 'middle');
      el('line', {x1: 34, x2: 308, y1: Y(0.303), y2: Y(0.303), class: 'ref fade'}, s);
      text(s, 312, Y(0.303) - 2, T('overall', 'global'), 'lbl-m fade'); text(s, 312, Y(0.303) + 12, fmt(30.3) + '%', 'lbl fade');
      data.forEach(([d, n, a], i) => {
        const g = el('g', {class: 'pop', style: `transition-delay:${i * 50}ms`, tabindex: 0, role: 'img', 'aria-label': `${d}: ${fmt(a / n * 100)}% (${a}/${n})`}, s);
        el('circle', {cx: X(d), cy: Y(a / n), r: Math.max(4, Math.sqrt(n) * 0.7), class: 'mark ring', opacity: n < 30 ? 0.45 : 1}, g);
        const hit = el('circle', {cx: X(d), cy: Y(a / n), r: 14, class: 'hit'}, g);
        bindTip(g, host, tip, () => T(`<b>${d} days ahead</b><br>${fmt(a / n * 100)}% attended · ${a}/${n}`, `<b>${d} días antes</b><br>${fmt(a / n * 100)}% asistió · ${a}/${n}`));
      });
    });
  }
  function ampm(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 150', role: 'img', 'aria-label': T('AM minus PM attendance gap: 5.4 points raw, 4.0 points with a common tenure mix, 95% interval −0.6 to 8.5 crossing zero.', 'Brecha AM menos PM: 5,4 puntos bruta, 4,0 con mezcla común de antigüedad, intervalo 95% de −0,6 a 8,5 que cruza el cero.')});
      host.prepend(s);
      const X = v => 40 + (v + 2) / 12 * 300;
      [-2, 0, 2, 4, 6, 8, 10].forEach(v => { el('line', {x1: X(v), x2: X(v), y1: 20, y2: 112, class: 'ax'}, s); text(s, X(v), 128, (v > 0 ? '+' : '') + v, 'ax-text', 'middle'); });
      text(s, 190, 146, T('AM − PM gap, percentage points', 'Brecha AM − PM, puntos porcentuales'), 'ax-text', 'middle');
      el('line', {x1: X(0), x2: X(0), y1: 14, y2: 112, class: 'zero'}, s);
      text(s, X(0) + 4, 12, T('no difference', 'sin diferencia'), 'lbl-m');
      text(s, 36, 46, T('Raw', 'Bruta'), 'lbl', 'end');
      el('circle', {cx: X(5.4), cy: 42, r: 6, class: 'mark-soft ring pop'}, s);
      text(s, X(5.4) + 10, 46, fmt(5.4), 'lbl-m fade');
      text(s, 36, 86, T('Adjusted', 'Ajustada'), 'lbl', 'end');
      el('line', {x1: X(-0.6), x2: X(8.5), y1: 82, y2: 82, class: 'ci growx'}, s);
      el('circle', {cx: X(4.0), cy: 82, r: 6, class: 'mark ring pop', style: 'transition-delay:.5s'}, s);
      text(s, X(4.0), 102, fmt(4.0) + '  [' + fmt(-0.6) + ', ' + fmt(8.5) + ']', 'lbl-m fade', 'middle');
    });
  }
  function weekday(host){
    const data = [['Mon','Lun',28.5,228],['Tue','Mar',30.3,195],['Wed','Mié',20.7,116],['Thu','Jue',32.4,241],['Fri','Vie',30.8,305],['Sat','Sáb',31.2,202],['Sun','Dom',33.3,213]];
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 190', role: 'img', 'aria-label': T('Attendance by weekday, from 20.7% on Wednesday to 33.3% on Sunday.', 'Asistencia por día, de 20,7% el miércoles a 33,3% el domingo.')});
      host.prepend(s);
      const base = 160, H = r => r / 40 * 130;
      [0, 20, 40].forEach(v => { el('line', {x1: 26, x2: 350, y1: base - H(v), y2: base - H(v), class: 'ax'}, s); text(s, 22, base - H(v) + 4, v + '%', 'ax-text', 'end'); });
      data.forEach(([en, es, r, n], i) => {
        const x = 44 + i * 44, h = H(r), w = 22, top = base - h;
        const g = el('g', {tabindex: 0, role: 'img', 'aria-label': `${T(en, es)}: ${fmt(r)}%, n = ${n}`}, s);
        el('path', {d: `M${x},${base}V${top + 4}Q${x},${top} ${x + 4},${top}H${x + w - 4}Q${x + w},${top} ${x + w},${top + 4}V${base}Z`, class: (en === 'Wed' ? 'mark-alt' : 'mark') + ' grow', style: `transition-delay:${i * 70}ms`}, g);
        el('rect', {x: x - 10, y: 20, width: w + 20, height: base - 20, class: 'hit'}, g);
        text(s, x + w / 2, base + 16, T(en, es), 'ax-text', 'middle');
        if(en === 'Wed' || en === 'Sun') text(s, x + w / 2, top - 7, fmt(r) + '%', 'lbl fade', 'middle');
        bindTip(g, host, tip, () => `<b>${T(en, es)}</b><br>${fmt(r)}% · n = ${n}`);
      });
    });
  }
  function venn(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 200', role: 'img', 'aria-label': T('Of 1,000 synthetic profiles: 503 group classes, 518 personal training, 258 both, 237 neither.', 'De 1.000 perfiles sintéticos: 503 clases grupales, 518 entrenamiento personal, 258 ambos, 237 ninguno.')});
      host.prepend(s);
      const g = el('g', {class: 'venn'}, s);
      el('circle', {cx: 150, cy: 108, r: 67, class: 'c1', fill: 'color-mix(in srgb, var(--green) 22%, transparent)', stroke: 'var(--green)', 'stroke-width': 2}, g);
      el('circle', {cx: 210, cy: 108, r: 68, class: 'c2', fill: 'color-mix(in srgb, var(--orange) 18%, transparent)', stroke: 'var(--orange)', 'stroke-width': 2}, g);
      text(s, 72, 24, T('Group classes', 'Clases grupales'), 'lbl', 'middle'); text(s, 72, 40, '503', 'lbl-m', 'middle');
      text(s, 292, 24, T('Personal training', 'Entrenamiento personal'), 'lbl', 'middle'); text(s, 292, 40, '518', 'lbl-m', 'middle');
      text(s, 116, 112, '245', 'lbl fade', 'middle');
      text(s, 180, 106, '258', 'lbl fade', 'middle'); text(s, 180, 122, T('both', 'ambos'), 'lbl-m fade', 'middle');
      text(s, 246, 112, '260', 'lbl fade', 'middle');
      text(s, 340, 192, T('neither · 237', 'ninguno · 237'), 'lbl-m fade', 'end');
    });
  }
  const charts = {leadTime, ampm, weekday, venn};
  document.querySelectorAll('[data-chart]').forEach(h => charts[h.dataset.chart]?.(h));

  /* ---------- Evidence figures ---------- */
  function gapBars(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 520 130', role: 'img', 'aria-label': T('Average clinical no-show rate about 23% versus GoalZone non-attendance 69.7%.', 'Tasa clínica media de no-show cerca de 23% frente a 69,7% de inasistencia en GoalZone.')});
      host.prepend(s);
      const X = v => 190 + v / 100 * 300;
      [0, 25, 50, 75, 100].forEach(v => { el('line', {x1: X(v), x2: X(v), y1: 10, y2: 106, class: 'ax'}, s); text(s, X(v), 124, v + '%', 'ax-text', 'middle'); });
      const rows = [[T('Clinical no-shows, 105 studies [1]', 'No-shows clínicos, 105 estudios [1]'), 23, 'mark-soft'], [T('GoalZone non-attendance', 'Inasistencia GoalZone'), 69.7, 'mark']];
      rows.forEach(([lab, v, cls], i) => {
        const y = 26 + i * 44;
        text(s, 180, y + 16, lab, 'lbl', 'end');
        el('path', {d: `M${X(0)},${y}H${X(v) - 4}Q${X(v)},${y} ${X(v)},${y + 4}V${y + 20}Q${X(v)},${y + 24} ${X(v) - 4},${y + 24}H${X(0)}Z`, class: cls + ' growx', style: `transition-delay:${i * 200}ms`}, s);
        text(s, X(v) + 8, y + 17, '≈' + fmt(v, v % 1 ? 1 : 0) + '%', 'lbl fade');
      });
    });
  }
  function habitTimeline(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 560 280', role: 'img', 'aria-label': T('Timeline of the first year of membership with habit and attrition milestones from the literature, and the lab attendance rates by tenure.', 'Línea de tiempo del primer año de membresía con hitos de hábito y abandono de la literatura, y las tasas de asistencia del laboratorio por antigüedad.')});
      host.prepend(s);
      const X = m => 30 + m / 12 * 500, axisY = 170;
      el('line', {x1: X(0), x2: X(12), y1: axisY, y2: axisY, class: 'ax', 'stroke-width': 2}, s);
      [0, 3, 6, 9, 12].forEach(m => { el('line', {x1: X(m), x2: X(m), y1: axisY - 4, y2: axisY + 4, class: 'ax'}, s); text(s, X(m), axisY + 18, m === 12 ? '12+' : m, 'ax-text', 'middle'); });
      text(s, X(0), axisY + 36, T('Months since joining', 'Meses desde la inscripción'), 'ax-text');
      // Gym habits: months to become predictable [6]
      text(s, X(2), 20, T('Gym habits take months to become predictable [6]', 'Los hábitos de gimnasio tardan meses en volverse predecibles [6]'), 'lbl-m fade');
      el('line', {x1: X(2), x2: X(7), y1: 30, y2: 30, class: 'ci growx'}, s);
      // Lally: 18–254 days, median 66
      el('rect', {x: X(18 / 30.4), y: 98, width: X(254 / 30.4) - X(18 / 30.4), height: 8, rx: 4, fill: 'color-mix(in srgb, var(--green) 25%, transparent)', class: 'growx'}, s);
      const ms = [
        {m: 1.4, y: 60, lab: T('6 weeks · 4 sessions a week to form a habit [4]', '6 semanas · 4 sesiones por semana para formar hábito [4]')},
        {m: 66 / 30.4, y: 92, lab: T('Day 66 · median habit automaticity, range 18–254 days [5]', 'Día 66 · mediana de automaticidad, rango 18–254 días [5]')},
        {m: 3, y: 132, lab: T('Month 3 · about 63% of new members have left [2]', 'Mes 3 · cerca del 63% de los nuevos socios se fue [2]'), alt: true},
        {m: 12, y: axisY + 36, lab: T('Month 12 · fewer than 4% still active [2]', 'Mes 12 · menos del 4% sigue activo [2]'), alt: true, below: true},
      ];
      ms.forEach((d, i) => {
        const g = el('g', {class: 'pop', style: `transition-delay:${300 + i * 200}ms`}, s);
        if(!d.below) el('line', {x1: X(d.m), x2: X(d.m), y1: d.y + 5, y2: axisY, class: 'ref'}, g);
        el('circle', {cx: X(d.m), cy: axisY, r: 6, class: (d.alt ? 'mark-alt' : 'mark') + ' ring'}, g);
        text(s, d.below ? X(d.m) : X(d.m) + 8, d.y, d.lab, 'lbl-m fade', d.below ? 'end' : 'start');
      });
      // This lab
      text(s, 30, 232, T('This lab · attendance by tenure', 'Este laboratorio · asistencia por antigüedad'), 'lbl');
      [[1, 6, 3.4, T('1–6 mo', '1–6 m')], [7, 12, 15.2, T('7–12 mo', '7–12 m')]].forEach(([a0, a1, r, lab], i) => {
        el('rect', {x: X(a0 - 1) + 2, y: 244, width: X(a1) - X(a0 - 1) - 4, height: 14, rx: 4, fill: 'var(--green)', opacity: 0.15 + r / 100 * 3, class: 'growx', style: `transition-delay:${i * 200}ms`}, s);
        text(s, (X(a0 - 1) + X(a1)) / 2, 272, `${lab} · ${fmt(r)}%`, 'lbl-m', 'middle');
      });
      text(s, X(12), 232, T('13–24 mo · 40.3% →', '13–24 m · 40,3% →'), 'lbl-m', 'end');
    });
  }
  function simulator(host){
    const cap = host.querySelector('#sim-cap'), p = host.querySelector('#sim-p'), lim = host.querySelector('#sim-lim');
    const out = id => host.querySelector(id);
    const chart = host.querySelector('.viz');
    const tip = tooltip(chart);
    function pmf(n, q){
      const lg = [0]; for(let i = 1; i <= n; i++) lg[i] = lg[i - 1] + Math.log(i);
      return Array.from({length: n + 1}, (_, k) => q === 0 ? +(k === 0) : q === 1 ? +(k === n) : Math.exp(lg[n] - lg[k] - lg[n - k] + k * Math.log(q) + (n - k) * Math.log(1 - q)));
    }
    function draw(){
      const C = +cap.value, q = +p.value / 100;
      lim.min = C; if(+lim.value < C) lim.value = C; lim.max = C * 2;
      const L = +lim.value, P = pmf(L, q);
      let exp = 0, over = 0, empty = 0, turned = 0;
      P.forEach((pk, k) => { exp += k * pk; if(k > C){ over += pk; turned += (k - C) * pk; } else empty += (C - k) * pk; });
      out('#o-cap').textContent = C; out('#o-p').textContent = Math.round(q * 100) + '%'; out('#o-lim').textContent = L;
      out('#s-exp').textContent = fmt(exp); out('#s-empty').textContent = fmt(empty); out('#s-over').textContent = fmt(over * 100) + '%';
      chart.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 520 190', role: 'img', 'aria-label': T('Distribution of attendees for the chosen booking limit, with the capacity line.', 'Distribución de asistentes para el límite de reservas elegido, con la línea de capacidad.')});
      chart.prepend(s);
      const maxK = L, maxP = Math.max(...P), bw = Math.min(20, 460 / (maxK + 1) - 2);
      const X = k => 40 + k / Math.max(1, maxK) * 460, base = 150, H = v => v / maxP * 120;
      el('line', {x1: 36, x2: 504, y1: base, y2: base, class: 'ax'}, s);
      P.forEach((pk, k) => {
        if(pk < 1e-4) return;
        const h = H(pk), x = X(k) - bw / 2, top = base - h;
        const g = el('g', {tabindex: -1}, s);
        el('path', {d: h > 4 ? `M${x},${base}V${top + 3}Q${x},${top} ${x + 3},${top}H${x + bw - 3}Q${x + bw},${top} ${x + bw},${top + 3}V${base}Z` : `M${x},${base}V${top}H${x + bw}V${base}Z`, class: k > C ? 'mark-alt' : 'mark'}, g);
        el('rect', {x: x - 1, y: 10, width: bw + 2, height: base - 10, class: 'hit'}, g);
        bindTip(g, chart, tip, () => T(`<b>${k} attend</b><br>probability ${fmt(pk * 100)}%`, `<b>${k} asisten</b><br>probabilidad ${fmt(pk * 100)}%`));
      });
      el('line', {x1: X(C) + bw / 2 + 1, x2: X(C) + bw / 2 + 1, y1: 8, y2: base + 4, stroke: 'var(--ink)', 'stroke-width': 1.5}, s);
      text(s, X(C) + bw / 2 + 5, 18, T(`capacity ${C}`, `capacidad ${C}`), 'lbl');
      [0, Math.round(maxK / 2), maxK].forEach(k => text(s, X(k), base + 18, k, 'ax-text', 'middle'));
      text(s, 270, base + 36, T('People who show up', 'Personas que llegan'), 'ax-text', 'middle');
    }
    [cap, p, lim].forEach(i => i.addEventListener('input', draw));
    onLang(draw);
  }
  const figs = {gapBars, habitTimeline};
  document.querySelectorAll('[data-fig]').forEach(h => figs[h.dataset.fig]?.(h));
  const sim = document.getElementById('simulator'); if(sim) simulator(sim);

  /* ---------- Dashboard mockup tilt ---------- */
  const browser = document.querySelector('.browser');
  if(browser && !reduce && matchMedia('(hover:hover)').matches){
    browser.addEventListener('mousemove', e => {
      const r = browser.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      browser.style.transform = `rotateX(${-y * 6}deg) rotateY(${x * 8}deg) scale(1)`;
    });
    browser.addEventListener('mouseleave', () => { browser.style.transform = ''; });
  }

  watch();
})();
