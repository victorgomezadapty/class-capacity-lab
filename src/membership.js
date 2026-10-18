const MEMBERS=JSON.parse(document.getElementById('membership-analysis').textContent);
let memberCurrent=[];
const memberBands=['Morning (05–12)','Afternoon (12–17)','Evening (17–22)','Night (22–05)'];
const memberSegments=['Group + PT','Group only','PT only','Neither group nor PT'];
const originalNav=[...document.querySelectorAll('.navlink')].map(a=>({html:a.innerHTML,href:a.getAttribute('href')}));
function switchDataset(which){
 activeDataset=which;
 $('attendance-panel').hidden=which!=='attendance';$('membership-panel').hidden=which!=='membership';
 $('tab-attendance').setAttribute('aria-pressed',String(which==='attendance'));$('tab-membership').setAttribute('aria-pressed',String(which==='membership'));
 const navB=[['#member-overview','Overview'],['#member-preferences','Favorites & overlap'],['#member-usage','Member usage'],['#member-rules','Association rules'],['#member-operations','Programming & evidence']];
 document.querySelectorAll('.navlink').forEach((a,i)=>{a.innerHTML=which==='attendance'?originalNav[i].html:'<span class="navnum">0'+(i+1)+'</span>'+navB[i][1];a.setAttribute('href',which==='attendance'?originalNav[i].href:navB[i][0]);a.classList.toggle('active',i===0);});
 document.querySelector('.brand-note').textContent=which==='attendance'?'CLASS CAPACITY LAB':'MEMBER PREFERENCES';
 document.title=which==='attendance'?'OGDT · Class Capacity Lab':'OGDT · Member Preferences Lab';
}
$('tab-attendance').addEventListener('click',()=>switchDataset('attendance'));
$('tab-membership').addEventListener('click',()=>switchDataset('membership'));
function memberStats(rows){const n=rows.length,g=rows.filter(r=>r.group).length,pt=rows.filter(r=>r.pt).length,both=rows.filter(r=>r.group&&r.pt).length;return {n,g,pt,both};}
function preferenceCounts(rows){const result=Object.fromEntries(MEMBERS.classes.map(c=>[c,0]));rows.forEach(r=>r.favorites.forEach(c=>result[c]++));return result;}
function memberBars(groups,target){$(target).innerHTML=groups.map(s=>'<div class="bar-row"><div class="bar-label">'+s.label+'<span>'+s.count+' / '+s.n+' members</span></div><div class="bar-track"><div class="bar-fill" style="width:'+(s.n?s.count/s.n*100:0)+'%"></div></div><div class="rate">'+pct(s.n?s.count/s.n:null)+'</div></div>').join('')+'<div class="axis"><span>0%</span><span>50%</span><span>100%</span></div>';}
function favoriteMatrix(rows,key,labels,target){
 let out='<table class="b-matrix"><caption class="visually-hidden">Preference share among group participants by '+key+'</caption><thead><tr><th scope="col">Member group</th>'+MEMBERS.classes.map(c=>'<th scope="col">'+c+'</th>').join('')+'</tr></thead><tbody>';
 labels.forEach(label=>{const g=rows.filter(r=>r.group&&r[key]===label),counts=preferenceCounts(g);out+='<tr><th scope="row">'+label+'<br><span class="b-subtitle">n = '+g.length+'</span></th>';MEMBERS.classes.forEach(c=>{const p=g.length?counts[c]/g.length:null;const color=p==null?'#f2f3ef':'rgb('+Math.round(238-100*p)+','+Math.round(243-70*p)+','+Math.round(232-110*p)+')';out+='<td style="background:'+color+'" title="'+label+' / '+c+': '+counts[c]+' of '+g.length+' group participants">'+pct(p)+'<small>'+counts[c]+' members</small></td>';});out+='</tr>';});out+='</tbody></table>';$(target).innerHTML=out;
}
function renderMemberFavorites(){
 const group=memberCurrent.filter(r=>r.group),counts=preferenceCounts(group);
 $('b-favorite-desc').textContent='Base: '+num(group.length)+' group participants in the selected cohort. Original class labels are preserved.';
 memberBars(MEMBERS.classes.map(label=>({label,count:counts[label],n:group.length})).sort((a,b)=>b.count-a.count||a.label.localeCompare(b.label)),'b-favorites');
 const sets=new Map();group.filter(r=>r.favorites.length>=2).forEach(r=>{const key=r.favorites.join(' + ');sets.set(key,(sets.get(key)||0)+1);});
 const top=[...sets].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,10);
 $('b-combinations').innerHTML=top.length?'<table class="member-table"><caption>Top 10 exact multi-class sets · denominator: '+group.length+' group participants</caption><thead><tr><th scope="col">Exact combination</th><th class="numeric" scope="col">Members</th><th class="numeric" scope="col">Share</th></tr></thead><tbody>'+top.map(([set,n])=>'<tr><th scope="row">'+set+'</th><td class="numeric">'+n+'</td><td class="numeric">'+pct(n/group.length)+'</td></tr>').join('')+'</tbody></table>':'<p class="b-empty">No multi-class preference sets in this cohort.</p>';
 favoriteMatrix(memberCurrent,'membership',['Premium','Standard'],'b-tier-matrix');
 favoriteMatrix(memberCurrent,'checkin_band',memberBands,'b-checkin-matrix');
 let pairHtml='<table class="b-matrix"><caption class="visually-hidden">Members naming both classes</caption><thead><tr><th scope="col">Class</th>'+MEMBERS.classes.map(c=>'<th scope="col">'+c+'</th>').join('')+'</tr></thead><tbody>';
 MEMBERS.classes.forEach(a=>{pairHtml+='<tr><th scope="row">'+a+'</th>';MEMBERS.classes.forEach(b=>{const n=group.filter(r=>r.favorites.includes(a)&&r.favorites.includes(b)).length;pairHtml+='<td style="background:'+(a===b?'#e0e8d8':n?'#eef3e8':'#f7f8f4')+'" title="'+a+' and '+b+': '+n+' members">'+n+'</td>';});pairHtml+='</tr>';});pairHtml+='</tbody></table>';$('b-pairs').innerHTML=pairHtml;
}
function renderMemberUsage(){
 memberBars([1,2,3,4,5].map(v=>{const g=memberCurrent.filter(r=>r.visits===v);return {label:v+(v===1?' visit':' visits'),count:g.filter(r=>r.group).length,n:g.length};}),'b-frequency');
 const ptrows=[true,false].map(pt=>{const g=memberCurrent.filter(r=>r.pt===pt);return {label:pt?'PT users':'No PT use',n:g.length,group:g.filter(r=>r.group).length};});
 $('b-pt-table').innerHTML='<table class="member-table"><caption>Group-class participation within PT groups</caption><thead><tr><th scope="col">PT use</th><th class="numeric" scope="col">Members</th><th class="numeric" scope="col">Group users</th><th class="numeric" scope="col">Group rate</th></tr></thead><tbody>'+ptrows.map(s=>'<tr><th scope="row">'+s.label+'</th><td class="numeric">'+s.n+'</td><td class="numeric">'+s.group+'</td><td class="numeric">'+pct(s.n?s.group/s.n:null)+'</td></tr>').join('')+'</tbody></table>';
 const s=memberStats(memberCurrent);$('b-participation').textContent='Group participation: '+s.g+' yes / '+(s.n-s.g)+' no. No report of participation is not a dated no-show.';
 $('b-segments').innerHTML=memberSegments.map(segment=>{const g=memberCurrent.filter(r=>r.segment===segment),n=g.length,mean=n?Math.round(g.reduce((s,r)=>s+r.duration,0)/n):null;return '<article class="usage-card"><h3>'+segment+'</h3><div class="segment-count">'+n+'</div><p>'+pct(s.n?n/s.n:null)+' of selected members</p><p class="segment-detail">Mean reported visit duration: '+(mean==null?'n.a.':mean+' min')+'<br>Sauna use: '+pct(n?g.filter(r=>r.sauna).length/n:null)+'</p></article>';}).join('');
}
function memberRules(rows){const group=rows.filter(r=>r.group),counts=preferenceCounts(group),result=[];if(!group.length)return result;for(let i=0;i<MEMBERS.classes.length;i++)for(let j=i+1;j<MEMBERS.classes.length;j++){const a=MEMBERS.classes[i],b=MEMBERS.classes[j],n=group.filter(r=>r.favorites.includes(a)&&r.favorites.includes(b)).length;if(!n)continue;for(const [from,to] of [[a,b],[b,a]]){const confidence=n/counts[from];result.push({from,to,n,support:n/group.length,confidence,lift:confidence/(counts[to]/group.length)});}}return result.sort((a,b)=>b.lift-a.lift||b.n-a.n||a.from.localeCompare(b.from)||a.to.localeCompare(b.to));}
function renderMemberRules(){const count=Number($('b-min-pair').value),group=memberCurrent.filter(r=>r.group);if(!Number.isInteger(count)||count<1||count>503){$('b-rule-note').textContent='Enter a whole number from 1 to 503.';$('b-rules-table').innerHTML='';return;}const eligible=memberRules(memberCurrent).filter(r=>r.n>=count),rules=eligible.slice(0,20);$('b-rule-note').textContent='Base: '+group.length+' group participants. '+eligible.length+' directed pair rules meet n ≥ '+count+'. Showing up to 20, ranked by lift.';
 $('b-rules-table').innerHTML=rules.length?'<table class="member-table"><caption>Exploratory rules for the selected cohort</caption><thead><tr><th scope="col">If favorite A</th><th scope="col">Also favorite B</th><th class="numeric" scope="col">Pair n</th><th class="numeric" scope="col">Support</th><th class="numeric" scope="col">Confidence</th><th class="numeric" scope="col">Lift</th></tr></thead><tbody>'+rules.map(r=>'<tr><th scope="row">'+r.from+'</th><td>'+r.to+'</td><td class="numeric">'+r.n+'</td><td class="numeric">'+pct(r.support)+'</td><td class="numeric">'+pct(r.confidence)+'</td><td class="numeric">'+r.lift.toFixed(2)+'</td></tr>').join('')+'</tbody></table>':'<p class="b-empty">No pair rules meet this count cutoff. Broaden the cohort or reduce the cutoff to explore the data.</p>';
}
function renderMembers(){
 memberCurrent=MEMBERS.records.filter(r=>($('b-membership').value==='all'||r.membership===$('b-membership').value)&&($('b-visits').value==='all'||r.visits===Number($('b-visits').value))&&($('b-time').value==='all'||r.checkin_band===$('b-time').value));
 const s=memberStats(memberCurrent);$('b-n').textContent=num(s.n);$('b-group-rate').textContent=pct(s.n?s.g/s.n:null);$('b-pt-rate').textContent=pct(s.n?s.pt/s.n:null);$('b-both').textContent=num(s.both);$('b-group-foot').textContent=s.g+' of '+s.n+' profiles report participation';$('b-pt-foot').textContent=s.pt+' of '+s.n+' profiles report PT use';$('b-both-foot').textContent=pct(s.n?s.both/s.n:null)+' of selected profiles';
 $('b-filter-note').textContent='Selected cohort · '+num(s.n)+' of 1,000 member profiles · '+s.g+' group participants · Preferences are not attendance events.';
 if(!$('b-distribution')){const dist=document.createElement('div');dist.id='b-distribution';dist.className='card';dist.style.marginTop='13px';document.querySelector('#member-overview .kpis').after(dist);}
 $('b-distribution').innerHTML='<h3>Distribution of reported group-class participation</h3><p class="desc">Participates: '+s.g+' ('+pct(s.n?s.g/s.n:null)+') · Does not report participation: '+(s.n-s.g)+' ('+pct(s.n?(s.n-s.g)/s.n:null)+')</p>'+(s.n?'<div role="img" aria-label="'+s.g+' participants and '+(s.n-s.g)+' nonparticipants" style="height:16px;display:flex;border-radius:4px;overflow:hidden;margin-top:12px;background:#e7ebdf"><div style="width:'+(s.g/s.n*100)+'%;background:#16644f"></div></div>':'<p class="desc">No member profiles match these filters.</p>');
 renderMemberFavorites();renderMemberUsage();renderMemberRules();
}
for(const id of ['b-membership','b-visits','b-time'])$(id).addEventListener('change',renderMembers);
$('b-reset').addEventListener('click',()=>{for(const id of ['b-membership','b-visits','b-time'])$(id).value='all';$('b-min-pair').value=10;renderMembers();});$('b-min-pair').addEventListener('input',renderMemberRules);
function exportMembership(){
 const cols=['membership','visits','group','pt','favorites','checkin_band','duration','sauna','segment'];
 const quote=v=>'"'+String(Array.isArray(v)?v.join('; '):v).replaceAll('"','""')+'"';
 const csv=cols.join(',')+'\r\n'+memberCurrent.map(r=>cols.map(c=>quote(r[c])).join(',')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='membership-selected-cohort.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('b-status').textContent='Exported '+memberCurrent.length+' member profiles. Source IDs, birthdays, gender, age and trainer names are excluded.';
}
const bq=MEMBERS.quality;$('b-audit').innerHTML=[['Member profiles',num(bq.rows)],['Unique source IDs',num(bq.unique_ids)],['Duplicate rows',bq.duplicate_rows],['Group participants with favorites','503 / 503'],['Blank favorites for nonparticipants','497 / 497 · structural absence'],['Usual-day / frequency mismatch',bq.day_frequency_mismatches],['Observed check-in range',bq.checkin_min+'–'+bq.checkin_max],['Class vocabulary',MEMBERS.classes.length+' labels retained'],['Favorite list length','1–3 classes per participant']].map(([a,b])=>'<li><span>'+a+'</span><strong>'+b+'</strong></li>').join('');
$('b-findings').innerHTML=MEMBERS.findings.map((f,i)=>'<article class="insight"><div class="insight-index">DATASET-WIDE FINDING 0'+(i+1)+'</div><h3>'+f.title+'</h3><p>'+f.text+'</p><p class="action"><strong>Next check:</strong> '+f.action+'</p></article>').join('');
renderMembers();
if(new URLSearchParams(location.search).get('view')==='members')switchDataset('membership');
