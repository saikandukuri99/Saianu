const {chromium}=require('playwright');const {spawn}=require('child_process');
const [a,b,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
(async()=>{const br=await chromium.launch({args:['--disable-gpu']});
const p=await br.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:2});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/v7.html');await p.waitForFunction('window.READY');
const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','prores_ks','-profile:v','3','-pix_fmt','yuv422p10le','-vendor','apl0','-r','30',out],{stdio:['pipe','inherit','inherit']});
const t0=Date.now();
for(let f=a;f<b;f++){await p.evaluate(t=>seek(t),f/30);const buf=await p.screenshot({type:'jpeg',quality:97});
 if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
 if((f-a)%60===0)console.log(out,f,((Date.now()-t0)/1000/(f-a+1)).toFixed(2)+'s/f');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();})();
