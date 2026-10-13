const {chromium}=require('playwright-core');const {spawn}=require('child_process');
const [,,scene,out,qs='6',startArg,endArg]=process.argv;
(async()=>{
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox','--font-render-hinting=none']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.log('PAGEERR',e.message));p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text())});
 await p.goto(`http://127.0.0.1:8123/scenes/${scene}.html`);await p.waitForFunction('window.ready===true',{timeout:60000});
 await p.evaluate(()=>document.fonts.ready);
 const N=await p.evaluate('frames()');
 if(out.endsWith('.png')){const f=+startArg;await p.evaluate(`render(${f/30})`);await p.screenshot({path:out,omitBackground:true});console.log('png',scene,f,'of',N);await b.close();return;}
 const s=startArg?+startArg:0,e=endArg?+endArg:N;
 const enc=out.endsWith('.mp4')?['-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p']:['-c:v','prores_ks','-profile:v','4444','-pix_fmt','yuva444p10le','-vendor','apl0','-qscale:v',qs];
 const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-c:v','png','-i','-',...enc,out],{stdio:['pipe','inherit','inherit']});
 const t0=Date.now();
 for(let f=s;f<e;f++){await p.evaluate(`render(${f/30})`);const buf=await p.screenshot({omitBackground:true});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%60==0)console.log(scene,f,'/',N,((Date.now()-t0)/1000).toFixed(0)+'s');}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',scene,N,'frames');
})();
