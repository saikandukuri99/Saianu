const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
p.on('console',m=>console.log('C:',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/index.html');await p.waitForFunction('window.READY');
const ts=process.argv.slice(2).map(Number);
for(const t of ts){await p.evaluate(t=>seek(t),t);await p.screenshot({path:`frames/st_${t.toFixed(2)}.png`,omitBackground:true});}
await b.close();})();
