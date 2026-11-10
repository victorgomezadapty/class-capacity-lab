// Visual layer for the case study and evidence pages: scroll reveals, the animated
// studio, data-driven mini charts with tooltips, the season-to-season explorer and
// the overbooking simulator. Every lab number is read from assets/data.js, built by
// src/build_site.py from Madrid 300076 (CC BY 4.0). Simulator inputs are assumptions
// and are labelled as such on the page.
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

  /* ---------- Studio: 40 places offered, booked share of the latest season ---------- */
  const studio = document.getElementById('studio-svg');
  if(studio){
    const cols = 8, rows = 5, w = 36, h = 44, gx = 12, gy = 12, x0 = 24, y0 = 60;
    const D0 = window.CCL, nB = D0 ? Math.round(D0.latest.occupancy * 40) : 25;
    const attended = new Set(Array.from({length: 40}, (_, i) => i).sort((p, q) => ((p * 17) % 40) - ((q * 17) % 40)).slice(0, nB));
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
    const finalState = () => { seats.forEach(s => { s.mat.setAttribute('class', 'mat ' + (s.att ? 'booked' : 'empty')); if(s.person) s.person.classList.add('in'); }); setCounts(40, nB, 40 - nB); setPhase(2); };
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

  const D = window.CCL;
  if(!D){ watch(); return; }
  const FAM = f => lang() === 'es' ? (D.family_es[f] || f) : f;
  const WD = {Mon:['Mon','Lun'],Tue:['Tue','Mar'],Wed:['Wed','Mié'],Thu:['Thu','Jue'],Fri:['Fri','Vie'],Sat:['Sat','Sáb'],Sun:['Sun','Dom']};
  const SL = {Morning:['Morning','Mañana'],Midday:['Midday','Mediodía'],Afternoon:['Afternoon','Tarde'],Evening:['Evening','Tarde-noche']};
  const MO = ['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const MOes = ['', 'Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
  const K = n => Math.round(n).toLocaleString(lang() === 'es' ? 'es-ES' : 'en-US');
  // cube rows: [season, family, weekday, slot, sessions, places, booked, full, empty]
  const agg = (rows, keyFn) => {
    const m = new Map();
    rows.forEach(r => { const k = keyFn(r); const a = m.get(k) || {s:0,p:0,b:0,f:0,e:0}; a.s += r[4]; a.p += r[5]; a.b += r[6]; a.f += r[7]; a.e += r[8]; m.set(k, a); });
    return m;
  };

  /* ---------- Season-to-season explorer ---------- */
  const explorer = document.getElementById('explorer');
  if(explorer){
    const bands = D.calibration.map(c => ({b: c.band, r: c.full_rate_now * 100, n: c.sessions}));
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
      cap.textContent = T(`Of 20 sessions in 2025-26 whose slot was full ${b.b} of the time in 2024-25, about ${on} were full again (observed ${fmt(b.r)}%, ${K(b.n)} sessions).`,
                          `De 20 sesiones de 2025-26 cuyo horario se llenó el ${b.b} de las veces en 2024-25, unas ${on} volvieron a llenarse (observado ${fmt(b.r)}%, ${K(b.n)} sesiones).`);
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
      const tick = () => { if(!autoplay || current >= bands.length - 1) return; current++; set(current); setTimeout(tick, 1300); };
      setTimeout(tick, 900);
    }, {threshold: 0.5}).observe(explorer);
  }

  /* ---------- Mini charts (case study) ---------- */
  function heat(host){
    const m = agg(D.cube, r => r[2] + '|' + r[3]);
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 200', role: 'img', 'aria-label': T('Share of sessions fully booked by weekday and time slot.', 'Porcentaje de sesiones llenas por día y franja.')});
      host.prepend(s);
      const cw = 40, ch = 34, x0 = 76, y0 = 22;
      D.weekdays.forEach((w, i) => text(s, x0 + i * cw + cw / 2, 14, T(...WD[w]), 'ax-text', 'middle'));
      D.slots.forEach((sl, j) => {
        text(s, x0 - 6, y0 + j * ch + ch / 2 + 4, T(...SL[sl]), 'ax-text', 'end');
        D.weekdays.forEach((w, i) => {
          const a = m.get(w + '|' + sl); if(!a) return;
          const r = a.f / a.s;
          const g = el('g', {class: 'pop', style: `transition-delay:${(i + j) * 40}ms`, tabindex: 0, role: 'img', 'aria-label': `${T(...WD[w])} ${T(...SL[sl])}: ${fmt(r * 100)}%`}, s);
          el('rect', {x: x0 + i * cw + 1, y: y0 + j * ch + 1, width: cw - 2, height: ch - 2, rx: 5, fill: 'var(--green)', 'fill-opacity': (0.06 + r / 0.45 * 0.94).toFixed(3)}, g);
          text(g, x0 + i * cw + cw / 2, y0 + j * ch + ch / 2 + 4, Math.round(r * 100) + '%', r > 0.27 ? 'lbl-inv' : 'lbl-m', 'middle');
          bindTip(g, host, tip, () => `<b>${T(...WD[w])} · ${T(...SL[sl])}</b><br>${fmt(r * 100)}% ${T('full', 'llenas')} · ${K(a.s)} ${T('sessions', 'sesiones')}`);
        });
      });
    });
  }
  function family(host){
    const m = agg(D.cube, r => r[1]);
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const rows = D.families.map(f => [f, m.get(f)]).sort((a, b) => b[1].f / b[1].s - a[1].f / a[1].s);
      const s = el('svg', {viewBox: `0 0 360 ${rows.length * 20 + 10}`, role: 'img', 'aria-label': T('Share of sessions fully booked by activity family.', 'Porcentaje de sesiones llenas por familia de actividad.')});
      host.prepend(s);
      const X = v => 168 + v / 0.5 * 160;
      rows.forEach(([f, a], i) => {
        const y = 4 + i * 20, r = a.f / a.s;
        const g = el('g', {tabindex: 0, role: 'img', 'aria-label': `${FAM(f)}: ${fmt(r * 100)}%`}, s);
        text(g, 162, y + 12, FAM(f), 'ax-text', 'end');
        el('rect', {x: X(0), y: y + 2, width: Math.max(1, X(r) - X(0)), height: 13, rx: 3, class: (r > 0.35 ? 'mark' : 'mark-soft') + ' growx', style: `transition-delay:${i * 50}ms`}, g);
        text(g, X(r) + 4, y + 13, fmt(r * 100) + '%', 'lbl-m fade');
        el('rect', {x: 0, y, width: 360, height: 18, class: 'hit'}, g);
        bindTip(g, host, tip, () => `<b>${FAM(f)}</b><br>${fmt(r * 100)}% ${T('full', 'llenas')} · ${fmt(a.b / a.p * 100)}% ${T('of places booked', 'de plazas ocupadas')} · ${K(a.s)} ${T('sessions', 'sesiones')}`);
      });
    });
  }
  function auc(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 150', role: 'img', 'aria-label': T('AUC by season pair for two rankings: same slot last season, and family, weekday and slot last season. 0.5 is chance.', 'AUC por par de temporadas para dos ordenamientos: mismo horario la temporada pasada, y familia, día y franja la temporada pasada. 0,5 es azar.')});
      host.prepend(s);
      const X = v => 110 + (v - 0.5) / 0.5 * 230;
      [0.5, 0.6, 0.7, 0.8, 0.9, 1].forEach(v => { el('line', {x1: X(v), x2: X(v), y1: 8, y2: 118, class: 'ax'}, s); text(s, X(v), 132, fmt(v, 1), 'ax-text', 'middle'); });
      text(s, X(0.5) + 3, 146, T('0.5 = chance', '0,5 = azar'), 'ax-text');
      D.predictability.forEach((p, i) => {
        const y = 22 + i * 34;
        text(s, 104, y + 8, p.train + ' → ' + p.test.slice(2), 'ax-text', 'end');
        el('circle', {cx: X(p.auc_family_weekday_slot), cy: y + 4, r: 5, class: 'mark-soft ring pop'}, s);
        el('circle', {cx: X(p.auc_same_slot), cy: y + 4, r: 6, class: 'mark ring pop', style: 'transition-delay:.3s'}, s);
        text(s, X(p.auc_same_slot) + 9, y + 8, fmt(p.auc_same_slot, 2), 'lbl-m fade');
      });
    });
  }
  function season(host){
    const m = agg(D.cube, r => r[0]);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 206', role: 'img', 'aria-label': T('Share of sessions fully booked and share of places booked, by season.', 'Porcentaje de sesiones llenas y de plazas ocupadas, por temporada.')});
      host.prepend(s);
      const base = 160, H = r => r / 0.7 * 140;
      [0, 0.2, 0.4, 0.6].forEach(v => { el('line', {x1: 30, x2: 350, y1: base - H(v), y2: base - H(v), class: 'ax'}, s); text(s, 26, base - H(v) + 4, Math.round(v * 100) + '%', 'ax-text', 'end'); });
      D.seasons.forEach((se, i) => {
        const a = m.get(se), x = 52 + i * 76, w = 26;
        [[a.b / a.p, 'mark-soft', 0], [a.f / a.s, 'mark', w + 4]].forEach(([r, cls, dx], k) => {
          const top = base - H(r);
          el('path', {d: `M${x + dx},${base}V${top + 4}Q${x + dx},${top} ${x + dx + 4},${top}H${x + dx + w - 4}Q${x + dx + w},${top} ${x + dx + w},${top + 4}V${base}Z`, class: cls + ' grow', style: `transition-delay:${(i * 2 + k) * 60}ms`}, s);
          text(s, x + dx + w / 2, top - 5, Math.round(r * 100) + '%', 'lbl-m fade', 'middle');
        });
        text(s, x + w + 2, base + 16, se, 'ax-text', 'middle');
      });
      text(s, 30, 200, T('■ light: places booked   ■ dark: sessions full', '■ claro: plazas ocupadas   ■ oscuro: sesiones llenas'), 'ax-text');
    });
  }
  function month(host){
    const m = new Map();
    D.month.forEach(r => { const a = m.get(r[2]) || {s:0,f:0}; a.s += r[3]; a.f += r[6]; m.set(r[2], a); });
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 360 190', role: 'img', 'aria-label': T('Share of sessions fully booked by month, September to August.', 'Porcentaje de sesiones llenas por mes, de septiembre a agosto.')});
      host.prepend(s);
      const base = 160, H = r => r / 0.35 * 140;
      [0, 0.1, 0.2, 0.3].forEach(v => { el('line', {x1: 30, x2: 350, y1: base - H(v), y2: base - H(v), class: 'ax'}, s); text(s, 26, base - H(v) + 4, Math.round(v * 100) + '%', 'ax-text', 'end'); });
      D.months.forEach((mo, i) => {
        const a = m.get(mo), r = a.f / a.s, x = 38 + i * 26, w = 18, top = base - H(r);
        const g = el('g', {tabindex: 0, role: 'img', 'aria-label': `${T(MO[mo], MOes[mo])}: ${fmt(r * 100)}%`}, s);
        el('path', {d: `M${x},${base}V${top + 3}Q${x},${top} ${x + 3},${top}H${x + w - 3}Q${x + w},${top} ${x + w},${top + 3}V${base}Z`, class: (r < 0.18 ? 'mark-alt' : 'mark') + ' grow', style: `transition-delay:${i * 50}ms`}, g);
        el('rect', {x: x - 4, y: 10, width: w + 8, height: base - 10, class: 'hit'}, g);
        text(s, x + w / 2, base + 16, T(MO[mo], MOes[mo]), 'ax-text', 'middle');
        bindTip(g, host, tip, () => `<b>${T(MO[mo], MOes[mo])}</b><br>${fmt(r * 100)}% ${T('full', 'llenas')} · ${K(a.s)} ${T('sessions', 'sesiones')}`);
      });
    });
  }
  function centres(host){
    const tip = tooltip(host);
    onLang(() => {
      host.querySelector('svg')?.remove();
      const c = D.centres_latest.slice().sort((a, b) => a[3] - b[3]);
      const s = el('svg', {viewBox: '0 0 360 170', role: 'img', 'aria-label': T('Share of full sessions in 2025-26 for each centre with at least 500 sessions, sorted.', 'Porcentaje de sesiones llenas en 2025-26 por centro con al menos 500 sesiones, ordenado.')});
      host.prepend(s);
      const base = 140, H = r => r / 0.6 * 125, bw = 300 / c.length;
      [0, 0.2, 0.4, 0.6].forEach(v => { el('line', {x1: 30, x2: 340, y1: base - H(v), y2: base - H(v), class: 'ax'}, s); text(s, 26, base - H(v) + 4, Math.round(v * 100) + '%', 'ax-text', 'end'); });
      c.forEach((row, i) => {
        const r = row[3], x = 36 + i * bw, top = base - H(r);
        const g = el('g', {tabindex: -1}, s);
        el('rect', {x, y: top, width: Math.max(1, bw - 1), height: H(r), class: 'mark grow', style: `transition-delay:${i * 10}ms`}, g);
        el('rect', {x, y: 10, width: bw, height: base - 10, class: 'hit'}, g);
        bindTip(g, host, tip, () => `<b>${row[0]}</b><br>${fmt(r * 100)}% ${T('full', 'llenas')} · ${K(row[1])} ${T('sessions', 'sesiones')}`);
      });
      text(s, 36, base + 18, T(`${c.length} centres, lowest to highest`, `${c.length} centros, de menor a mayor`), 'ax-text');
    });
  }
  const charts = {heat, family, auc, season, month, centres};
  document.querySelectorAll('[data-chart]').forEach(h => charts[h.dataset.chart]?.(h));

  /* ---------- Evidence figures ---------- */
  function calib(host){
    onLang(() => {
      host.querySelector('svg')?.remove();
      const s = el('svg', {viewBox: '0 0 520 222', role: 'img', 'aria-label': T('Share of 2025-26 sessions that were full, by how often the same slot was full in 2024-25.', 'Porcentaje de sesiones llenas en 2025-26 según cuánto se llenó el mismo horario en 2024-25.')});
      host.prepend(s);
      const base = 160, H = r => r * 140;
      [0, 0.25, 0.5, 0.75, 1].forEach(v => { el('line', {x1: 50, x2: 500, y1: base - H(v), y2: base - H(v), class: 'ax'}, s); text(s, 44, base - H(v) + 4, Math.round(v * 100) + '%', 'ax-text', 'end'); });
      D.calibration.forEach((c, i) => {
        const x = 70 + i * 88, w = 48, r = c.full_rate_now, top = base - H(r);
        el('path', {d: `M${x},${base}V${top + 4}Q${x},${top} ${x + 4},${top}H${x + w - 4}Q${x + w},${top} ${x + w},${top + 4}V${base}Z`, class: 'mark grow', style: `transition-delay:${i * 80}ms`}, s);
        text(s, x + w / 2, top - 6, fmt(r * 100) + '%', 'lbl fade', 'middle');
        text(s, x + w / 2, base + 16, c.band, 'ax-text', 'middle');
        text(s, x + w / 2, base + 30, 'n = ' + K(c.sessions), 'ax-text', 'middle');
      });
      text(s, 275, 216, T('Same slot, share of sessions full in 2024-25', 'Mismo horario, porcentaje de sesiones llenas en 2024-25'), 'ax-text', 'middle');
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
  const figs = {calib};
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
