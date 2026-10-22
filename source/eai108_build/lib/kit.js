// helpers for the 108 s scenes. All times in scenes are absolute seconds of the narration script (Storyline A).
function shiftTimes(off){document.querySelectorAll('[data-in],[data-out],[data-draw],[data-type]').forEach(e=>{['in','out','draw','type'].forEach(k=>{if(e.dataset[k]!==undefined)e.dataset[k]=(+e.dataset[k]+off).toFixed(3)})})}
function floats(t){document.querySelectorAll('[data-float]').forEach(e=>{const [a,p,ph]=e.dataset.float.split(',').map(Number);e.style.transform=`translateY(${(Math.sin(t*6.283/(p||7)+(ph||0))*(a||4)).toFixed(2)}px)`})}
function cnt(id,t,a,d,from,to,fmt){const e=document.getElementById(id);if(!e)return;const p=P(t,a,d,E.io);e.textContent=fmt?fmt(from+(to-from)*p):Math.round(from+(to-from)*p)}
function bar(id,t,a,d,pct){const e=document.getElementById(id);if(e)e.style.width=(pct*P(t,a,d,E.io)).toFixed(2)+'%'}
