// Language switch for the narrative pages. Content exists in both languages
// (data-l="en" / data-l="es"); CSS hides the inactive one based on <html lang>.
(function(){
  function initial(){
    var q = new URLSearchParams(location.search).get('lang');
    if(q === 'es' || q === 'en') return q;
    try{ var s = localStorage.getItem('ccl-lang'); if(s) return s; }catch(e){}
    return (navigator.language || '').toLowerCase().indexOf('es') === 0 ? 'es' : 'en';
  }
  function apply(lang){
    document.documentElement.lang = lang;
    try{ localStorage.setItem('ccl-lang', lang); }catch(e){}
    var t = document.querySelector('meta[name="title-' + lang + '"]');
    if(t) document.title = t.content;
    document.querySelectorAll('[data-set-lang]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.setLang === lang)); });
    document.querySelectorAll('a[data-keep-lang]').forEach(function(a){
      var base = a.getAttribute('href').split('?')[0].split('#'), hash = base[1] ? '#' + base[1] : '';
      a.href = base[0] + '?lang=' + lang + hash;
    });
    document.dispatchEvent(new CustomEvent('ccl:lang', {detail: lang}));
  }
  document.documentElement.lang = initial();
  document.documentElement.classList.add('js');
  document.addEventListener('DOMContentLoaded', function(){
    apply(document.documentElement.lang);
    document.addEventListener('click', function(e){
      var b = e.target.closest('[data-set-lang]');
      if(b) apply(b.dataset.setLang);
    });
  });
})();
