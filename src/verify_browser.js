// Run in the dashboard using agent-browser eval -b after substituting CSV-derived cases.
(async () => {
  const cases = __GOLDEN_CASES__;
  const failures = [];
  const set = (id, value) => {const el = document.getElementById(id); el.value = value; el.dispatchEvent(new Event('change'));};
  for (const c of cases) {
    set('category', c.category); set('day', c.day); set('time', c.time);
    const n = document.getElementById('k-n').textContent.replaceAll(',', '');
    const a = document.getElementById('k-a').textContent.replaceAll(',', '');
    const rate = document.getElementById('k-rate').textContent;
    if (Number(n)!==c.n || Number(a)!==c.a || rate!==c.rate) failures.push({c,n,a,rate});
  }
  document.getElementById('reset').click();
  for (const v of ['category','day_of_week','time','matrix']) {
    document.querySelector('[data-view="'+v+'"]').click();
    const total = [...document.querySelectorAll('#schedule-table tbody tr')].reduce((s,r)=>s+Number(r.cells[1].textContent.replaceAll(',','')),0);
    if (total!==1500) failures.push({view:v,total});
  }
  set('category','Unknown'); set('day','Wed'); set('time','PM');
  if (document.getElementById('k-rate').textContent!=='n.a.' || !document.getElementById('lead').textContent.includes('No bookings')) failures.push('Empty cohort handling');
  set('category','Aqua');set('day','Thu');set('time','PM');
  let exported;
  const oldCreate=URL.createObjectURL,oldClick=HTMLAnchorElement.prototype.click;
  URL.createObjectURL=b=>{exported=b;return oldCreate(b);};
  HTMLAnchorElement.prototype.click=function(){};
  document.getElementById('download').click();
  URL.createObjectURL=oldCreate;HTMLAnchorElement.prototype.click=oldClick;
  const csv=await exported.text();
  if (csv.split('\r\n').length!==8 || csv.split('\r\n')[0].includes('weight')) failures.push('CSV export');
  document.getElementById('reset').click();
  document.querySelector('[data-view="category"]').click();
  return {cohortsChecked:cases.length,scheduleViewsChecked:4,emptyCohortChecked:true,exportRows:7,failures,
          globalRate:document.getElementById('k-rate').textContent,
          horizontalOverflow:document.documentElement.scrollWidth>window.innerWidth};
})()
