(async()=>{
 const expected=__MEMBERSHIP_EXPECTED__;
 const failures=[];
 const set=(id,v)=>{const el=document.getElementById(id);el.value=String(v);el.dispatchEvent(new Event('change'));};
 document.getElementById('tab-membership').click();
 const visible=()=>!document.getElementById('membership-panel').hidden&&document.getElementById('attendance-panel').hidden;
 if(!visible())failures.push('Dataset visibility');
 for(const c of expected.cases){
  set('b-membership',c.membership);set('b-visits',c.visits);set('b-time',c.time);
  const actual={n:Number(document.getElementById('b-n').textContent.replaceAll(',','')),both:Number(document.getElementById('b-both').textContent),groupRate:document.getElementById('b-group-rate').textContent,ptRate:document.getElementById('b-pt-rate').textContent};
  if(actual.n!==c.n||actual.both!==c.both||actual.groupRate!==c.groupRate||actual.ptRate!==c.ptRate)failures.push({cohort:c,actual});
  const rows=[...document.querySelectorAll('#b-favorites .bar-row')];
  for(const row of rows){const label=row.querySelector('.bar-label').firstChild.textContent,rate=row.querySelector('.rate').textContent;if(rate!==c.favorites[label])failures.push({favorite:label,rate,expected:c.favorites[label]});}
  const segmentTotal=[...document.querySelectorAll('.segment-count')].reduce((sum,el)=>sum+Number(el.textContent),0);
  if(segmentTotal!==c.n)failures.push({segments:segmentTotal,expected:c.n});
 }
 document.getElementById('b-reset').click();
 for(const cutoff of [10,1,503]){
  const el=document.getElementById('b-min-pair');el.value=cutoff;el.dispatchEvent(new Event('input'));
  for(const row of document.querySelectorAll('#b-rules-table tbody tr')){const cells=[...row.cells].map(c=>c.textContent),key=cells[0]+'|'+cells[1],gold=expected.rules[key];if(!gold||Number(cells[2])<cutoff||cells.slice(2).join('|')!==gold.join('|'))failures.push({rule:key,actual:cells.slice(2),expected:gold});}
  if(cutoff===503&&document.querySelectorAll('#b-rules-table tbody tr').length)failures.push('Rule cutoff 503');
 }
 const cutoff=document.getElementById('b-min-pair');cutoff.value=0;cutoff.dispatchEvent(new Event('input'));
 if(!document.getElementById('b-rule-note').textContent.includes('Enter a whole number'))failures.push('Invalid rule cutoff');
 document.getElementById('b-reset').click();set('b-time','Night (22–05)');
 if(document.getElementById('b-group-rate').textContent!=='n.a.')failures.push('Empty cohort');
 document.getElementById('b-reset').click();set('b-membership','Premium');set('b-visits',4);set('b-time','Evening (17–22)');
 let blob;const oldCreate=URL.createObjectURL,oldClick=HTMLAnchorElement.prototype.click;
 URL.createObjectURL=b=>{blob=b;return oldCreate(b);};HTMLAnchorElement.prototype.click=function(){};
 document.getElementById('download').click();URL.createObjectURL=oldCreate;HTMLAnchorElement.prototype.click=oldClick;
 const csv=await blob.text(),header=csv.split('\r\n')[0],n=Number(document.getElementById('b-n').textContent);
 if(csv.split('\r\n').length!==n+1||header.includes('birthday')||header.includes('trainer')||header.includes('id')||!header.includes('favorites'))failures.push('Membership cohort export');
 document.getElementById('b-reset').click();
 if(document.documentElement.scrollWidth>window.innerWidth)failures.push('Page-level overflow');
 document.getElementById('tab-attendance').click();
 if(document.getElementById('k-rate').textContent!=='30.3%'||document.getElementById('k-n').textContent!=='1,500')failures.push('GoalZone preservation');
 document.getElementById('tab-membership').click();
 return {membershipCohortsChecked:expected.cases.length,favoriteRatesChecked:expected.cases.length*11,associationRuleMetricsChecked:true,profileTotalsChecked:true,emptyCohortChecked:true,memberExportChecked:true,datasetSwitchingChecked:true,viewport:window.innerWidth,failures};
})()
