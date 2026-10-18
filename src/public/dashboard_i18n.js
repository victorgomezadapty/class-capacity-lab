// Runtime EN -> ES layer for the public dashboard. The analysis code renders English;
// this layer translates text nodes and a few attributes, including re-rendered content.
// Numbers are normalised to {#} so one dictionary entry covers every filtered cohort.
(function(){
  'use strict';
  const DICT = JSON.parse(document.getElementById('i18n-es').textContent);
  const ES = DICT.strings, RULES = DICT.rules.map(([re, tpl]) => [new RegExp(re), tpl]);
  const NUM = /[-−+]?\d[\d,]*(?:\.\d+)?/g;
  const ATTRS = ['aria-label','title','placeholder'];
  const orig = new WeakMap(), shown = new WeakMap(), attrOrig = new WeakMap(), attrShown = new WeakMap();
  const missing = new Set();
  let lang = 'en', busy = false;

  function tr(s){
    const core = s.trim();
    if(!core || !/[A-Za-z]{2}/.test(core)) return null;
    const nums = [];
    const key = core.replace(NUM, m => { nums.push(m); return '{#}'; });
    let t = ES[key];
    if(t == null){
      // Combinatorial labels (class / day, class pairs, band / class): translate the captured parts.
      for(const [re, tpl] of RULES){
        const m = key.match(re);
        if(m){ t = tpl.replace(/\$(\d)/g, (_, i) => ES[m[i]] ?? m[i]); break; }
      }
    }
    if(t == null){ missing.add(key); return null; }
    let i = 0;
    const out = t.replace(/\{#\}/g, () => nums[i++] ?? '');
    return s.slice(0, s.indexOf(core[0])) + out + s.slice(s.lastIndexOf(core[core.length-1]) + 1);
  }
  function skip(el){ return !el || el.closest('script,style,[data-no-i18n]'); }
  function textNode(n){
    if(skip(n.parentElement)) return;
    const cur = n.nodeValue;
    if(shown.has(n) && shown.get(n) === cur) return;   // our own write
    orig.set(n, cur);
    if(lang === 'es'){ const t = tr(cur); if(t != null && t !== cur){ shown.set(n, t); n.nodeValue = t; return; } }
    shown.delete(n);
  }
  function element(el){
    if(skip(el)) return;
    for(const a of ATTRS){
      if(!el.hasAttribute(a)) continue;
      const o = attrOrig.get(el) || {}, s = attrShown.get(el) || {}, cur = el.getAttribute(a);
      if(s[a] !== cur) o[a] = cur;                      // app wrote a new English value
      const v = (lang === 'es' ? tr(o[a]) : null) ?? o[a];
      s[a] = v; attrOrig.set(el, o); attrShown.set(el, s);
      if(cur !== v) el.setAttribute(a, v);
    }
  }
  function walk(root){
    if(root.nodeType === 3){ textNode(root); return; }
    if(root.nodeType !== 1) return;
    element(root);
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    let n; while((n = w.nextNode())) n.nodeType === 3 ? textNode(n) : element(n);
  }
  function restore(root){
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n; while((n = w.nextNode())){ if(orig.has(n) && shown.has(n)){ n.nodeValue = orig.get(n); shown.delete(n); } }
  }
  const obs = new MutationObserver(list => {
    if(busy) return; busy = true;
    for(const m of list){
      if(m.type === 'characterData') textNode(m.target);
      else if(m.type === 'attributes') element(m.target);
      else m.addedNodes.forEach(walk);
    }
    busy = false;
  });
  function setLang(l){
    lang = l === 'es' ? 'es' : 'en';
    document.documentElement.lang = lang;
    try{ localStorage.setItem('ccl-lang', lang); }catch(e){}
    busy = true;
    if(lang === 'es') walk(document.body); else { restore(document.body); walk(document.body); }
    const title = document.querySelector('title'); if(title){ lang === 'es' ? walk(title) : (restore(title), walk(title)); }
    busy = false;
    document.querySelectorAll('[data-set-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.setLang === lang)));
    document.querySelectorAll('a[data-keep-lang]').forEach(a => { const u = new URL(a.getAttribute('href'), location.href); u.searchParams.set('lang', lang); a.href = u.pathname.split('/').pop() + u.search + u.hash; });
  }
  function initial(){
    const q = new URLSearchParams(location.search).get('lang');
    if(q) return q;
    try{ const s = localStorage.getItem('ccl-lang'); if(s) return s; }catch(e){}
    return (navigator.language || '').toLowerCase().startsWith('es') ? 'es' : 'en';
  }
  document.addEventListener('click', e => { const b = e.target.closest('[data-set-lang]'); if(b) setLang(b.dataset.setLang); });
  obs.observe(document.body, {subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:ATTRS});
  if(document.querySelector('title')) obs.observe(document.querySelector('title'), {subtree:true, childList:true, characterData:true});
  window.cclI18n = { setLang, missing: () => [...missing].sort() };
  setLang(initial());
})();
