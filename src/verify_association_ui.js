(()=>{
 const failures=[];
 const select=(id,value)=>{const el=document.getElementById(id);el.value=value;el.dispatchEvent(new Event('change'));};
 document.getElementById('tab-attendance').click();
 const cards=[...document.querySelectorAll('#a-association-cards .association-card')];
 if(cards.length!==5)failures.push('Five attendance association cards');
 if(!cards[1].textContent.includes('r = 0.024')||!cards[1].textContent.includes('weak linear relationship, not a quality score'))failures.push('Lead-time interpretation');
 const before=cards.map(c=>c.querySelector('.stat-number').textContent).join('|');
 select('category','Aqua');
 const after=[...document.querySelectorAll('#a-association-cards .stat-number')].map(c=>c.textContent).join('|');
 if(before!==after)failures.push('Whole-dataset estimates changed under cohort filter');
 const toggle=document.querySelector('#attendance-associations .technical-toggle');
 if(toggle.getAttribute('aria-pressed')==='true')toggle.click();toggle.click();
 if([...document.querySelectorAll('#attendance-associations .technical-detail')].some(d=>!d.open))failures.push('Expand technical details');
 toggle.click();
 if([...document.querySelectorAll('#attendance-associations .technical-detail')].some(d=>d.open))failures.push('Collapse technical details');
 document.getElementById('reset').click();document.getElementById('tab-membership').click();
 if(document.querySelectorAll('#b-association-cards .association-card').length!==4)failures.push('Four membership association cards');
 const lift=document.getElementById('b-lift-explanation').textContent;
 if(!lift.includes('Lift = 1.12')||!lift.includes('does not mean a 12% increase in sales'))failures.push('Lift interpretation');
 if(!document.querySelector('.source-confirmation').textContent.includes('synthetic demonstration data'))failures.push('Synthetic source explanation');
 return {associationCardsChecked:9,technicalToggleChecked:true,wholeDatasetScopeChecked:true,liftExplanationChecked:true,sourceStatusChecked:true,viewport:window.innerWidth,overflow:document.documentElement.scrollWidth>window.innerWidth,failures};
})()
