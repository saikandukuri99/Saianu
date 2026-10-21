const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const E={out:t=>1-(1-t)**3,io:t=>t<.5?4*t*t*t:1-(-2*t+2)**3/2,back:t=>{const c=1.5;return 1+(c+1)*(t-1)**3+c*(t-1)**2},lin:t=>t};
const P=(t,a,d=.6,f=E.out)=>f(clamp((t-a)/d));
const $$=s=>[...document.querySelectorAll(s)];
function auto(t){
 $$('[data-in]').forEach(el=>{
  const a=+el.dataset.in,d=+(el.dataset.dur||.6),fx=el.dataset.fx||'up',o=el.dataset.out!==undefined?+el.dataset.out:null;
  const p=P(t,a,d,fx==='pop'?E.back:E.out),q=o!==null?P(t,o,.35,E.io):0;
  const op=clamp((t-a)/(d*.7))*(1-q);
  let dx=0,dy=0,s=1;
  if(fx==='up')dy=28*(1-p);else if(fx==='down')dy=-28*(1-p);else if(fx==='left')dx=-48*(1-p);else if(fx==='right')dx=48*(1-p);else if(fx==='pop')s=.78+.22*p;else if(fx==='scale')s=.92+.08*p;
  el.style.opacity=op;el.style.transform=`translate(${dx}px,${dy}px) scale(${s})`;el.style.visibility=op<=.002?'hidden':'visible';
 });
 $$('[data-draw]').forEach(el=>{
  const a=+el.dataset.draw,d=+(el.dataset.dur||.8),o=el.dataset.out!==undefined?+el.dataset.out:null;
  const L=el.getTotalLength?el.getTotalLength():0;
  el.style.strokeDasharray=el.dataset.dots?'3 9':`${L} ${L}`;
  const p=P(t,a,d,E.io);
  if(!el.dataset.dots)el.style.strokeDashoffset=L*(1-p);
  el.style.opacity=(t<a?0:(el.dataset.dots?p:1))*(o!==null?1-P(t,o,.35,E.io):1);
 });
 $$('[data-type]').forEach(el=>{const a=+el.dataset.type,sp=+(el.dataset.cps||34);if(!el._t)el._t=el.textContent;const n=Math.floor(clamp((t-a)*sp,0,el._t.length));el.textContent=el._t.slice(0,n)+(n<el._t.length&&t>a?'▌':'');el.style.visibility=t<a?'hidden':'visible';});
}
function _ip(x,X,Y){if(x<=X[0])return Y[0]+(x-X[0]);if(x>=X[X.length-1])return Y[Y.length-1]+(x-X[X.length-1]);for(let i=0;i<X.length-1;i++)if(x>=X[i]&&x<=X[i+1])return X[i+1]===X[i]?Y[i]:Y[i]+(Y[i+1]-Y[i])*(x-X[i])/(X[i+1]-X[i]);}
function _map(){const m=typeof TM_OLD!=='undefined'&&SCENE.VS!==undefined&&!SCENE.N;if(!m)return null;if(!SCENE._m){const f0=Math.max(0,Math.floor(_ip(SCENE.VS,TM_OLD,TM_NEW)*30+1e-6)),f1=Math.ceil(_ip(SCENE.VE,TM_OLD,TM_NEW)*30-1e-6);SCENE._m={f0,f1};}return SCENE._m;}
window.render=function(tl){
 const M=_map();const t=M?_ip(tl+M.f0/30,TM_NEW,TM_OLD):tl+(SCENE.VS||0);
 const st=document.getElementById('stage');
 if(st)st.style.opacity=SCENE.VE>=100?1:(M?1-P(tl+M.f0/30,M.f1/30-.3,.3,E.io):1-P(t,SCENE.VE-.3,.3,E.io));
 auto(t);
 SCENE.update&&SCENE.update(t,tl);
 return true;
};
window.frames=()=>{const M=_map();return M?M.f1-M.f0:(SCENE.N||Math.round((SCENE.VE-(SCENE.VS||0))*30));};
const ICONS={folder:"M3 6h7l2 2h9v11H3z",db:"M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3zM4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6",layers:"M12 3l9 5-9 5-9-5zM3 12.5l9 5 9-5M3 17l9 5 9-5",home:"M3 10l9-6 9 6v10H3zM9 20v-6h6v6",check:"M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM8 12.5l3 3 5-6",chat:"M4 5h16v11H9l-5 4z",spark:"M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M18 6l-2.5 2.5M8.5 15.5L6 18",play:"M7 4l13 8-13 8z",user:"M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c0-4 3.6-7 8-7s8 3 8 7",bot:"M5 8h14v10H5zM12 8V4M9 13h.01M15 13h.01M3 12v3M21 12v3",cloud:"M7 18a4.5 4.5 0 1 1 .8-8.9A6 6 0 0 1 19 11a3.5 3.5 0 0 1-.5 7z",server:"M4 4h16v6H4zM4 14h16v6H4zM8 7h.01M8 17h.01",shield:"M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM9 12l2 2 4-4",file:"M6 3h8l4 4v14H6zM14 3v4h4M9 12h6M9 16h6",mail:"M3 6h18v12H3zM3 7l9 7 9-7",cpu:"M7 7h10v10H7zM9 3v4M15 3v4M9 17v4M15 17v4M3 9h4M3 15h4M17 9h4M17 15h4",graph:"M6 6a2 2 0 1 0 .01 0M18 6a2 2 0 1 0 .01 0M12 18a2 2 0 1 0 .01 0M7.7 7.3l3.2 8.7M16.3 7.3l-3.2 8.7M8 6h8",search:"M11 18a7 7 0 1 0 0-14 7 7 0 0 0 0 14zM21 21l-5-5",lock:"M6 11h12v9H6zM8 11V8a4 4 0 0 1 8 0v3",userok:"M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c0-4 3.6-7 8-7M15 18l2 2 4-4",globe:"M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",bolt:"M13 3L5 14h6l-1 7 8-11h-6z",tag:"M3 12V4h8l10 10-8 8z",table:"M4 5h16v14H4zM4 10h16M10 5v14",gear:"M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"};
document.addEventListener('DOMContentLoaded',()=>$$('[data-ic]').forEach(e=>{e.classList.add('ic');e.innerHTML=`<svg viewBox="0 0 24 24"><path d="${ICONS[e.dataset.ic]}"/></svg>`;}));
