// node render.js preview <outdir> <scene> <t1,t2,...>   |  node render.js video <outdir> <scenes> <variants>
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs'); const path = require('path');
const [mode, out, scenesArg, extra] = process.argv.slice(2);
const NAMES = { 1: '01_The_Evolution_of_AI', 2: '02_Built_for_Real-World_Application', 3: '03_Designed_for_Experts', 4: '04_From_AI_Output_to_Real_Value', 5: '05_Bridging_AI_and_Human_Expertise' };
async function newPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text())); page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto('file://' + path.resolve(__dirname, 'index.html')); await page.evaluate(() => window.ready); return page;
}
const grab = (page, s, t, v) => page.evaluate(([s, t, v]) => { draw(s, t, v); return document.getElementById('c').toDataURL('image/png'); }, [s, t, v]).then(d => Buffer.from(d.split(',')[1], 'base64'));
(async () => {
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync'] }); fs.mkdirSync(out, { recursive: true });
  if (mode === 'preview') {
    const page = await newPage(browser);
    for (const t of extra.split(',').map(Number)) fs.writeFileSync(`${out}/s${scenesArg}_${t.toFixed(2)}.png`, await grab(page, +scenesArg, t, 'clean'));
  } else {
    const jobs = []; for (const s of scenesArg.split(',')) for (const v of extra.split(',')) jobs.push([+s, v]);
    const work = async () => { while (jobs.length) { const [s, v] = jobs.shift(); const page = await newPage(browser);
      const dir = v === 'clean' ? out : `${out}/${v === 'full' ? 'with_text' : 'text_overlay_alpha'}`; fs.mkdirSync(dir, { recursive: true });
      const file = `${dir}/${NAMES[s]}${v === 'alpha' ? '_TEXT_ALPHA.mov' : v === 'clean' ? '.mp4' : '.mp4'}`;
      const enc = v === 'alpha' ? ['-c:v', 'qtrle', '-pix_fmt', 'argb'] : ['-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart'];
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'png', '-i', '-', ...enc, '-r', '30', file], { stdio: ['pipe', 'inherit', 'inherit'] });
      const t0 = Date.now();
      for (let f = 0; f < 180; f++) { const b = await grab(page, s, f / 30, v); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r)); }
      ff.stdin.end(); await new Promise(r => ff.on('close', r)); await page.close(); console.log('done', file, ((Date.now() - t0) / 1000).toFixed(0) + 's'); } };
    await Promise.all([work(), work(), work(), work()]);
  }
  await browser.close();
})();
