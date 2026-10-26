// Renders loop.html frame-by-frame with headless Chromium and pipes to ffmpeg.
// usage: node render.js stills <outdir> <t1,t2,...>
//        node render.js video <out.mp4> [workers=4] [fps=60]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const PAGE = 'file://' + path.join(__dirname, 'loop.html');
const LOOP = 90;

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(PAGE);
  await page.evaluate(() => window.ready);
  const cdp = await page.context().newCDPSession(page);
  return { page, cdp };
}
async function grab({ page, cdp }, t) {
  await page.evaluate(t => window.renderFrame(t), t);
  const r = await cdp.send('Page.captureScreenshot', { format: 'png', optimizeForSpeed: true });
  return Buffer.from(r.data, 'base64');
}

async function stills(outdir, times) {
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch();
  const p = await openPage(browser);
  for (const t of times) fs.writeFileSync(path.join(outdir, `t_${String(t).padStart(5, '0')}.png`), await grab(p, t));
  await browser.close();
}

async function segment(browser, f0, f1, fps, file) {
  const p = await openPage(browser);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'animation',
    '-g', String(fps), '-bf', '2', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) {
    const buf = await grab(p, f / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 300 === 0) console.log(`${path.basename(file)} ${f - f0}/${f1 - f0}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await p.page.close();
}

async function video(out, workers, fps) {
  const total = LOOP * fps, per = Math.ceil(total / workers), tmp = out + '.parts';
  fs.mkdirSync(tmp, { recursive: true });
  const browser = await chromium.launch();
  const files = [];
  await Promise.all(Array.from({ length: workers }, (_, i) => {
    const f = path.join(tmp, `p${i}.mp4`); files.push(f);
    return segment(browser, i * per, Math.min(total, (i + 1) * per), fps, f);
  }));
  await browser.close();
  fs.writeFileSync(path.join(tmp, 'list.txt'), files.map(f => `file '${f}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-c', 'copy', '-an', '-movflags', '+faststart', out], { stdio: 'inherit' }).on('close', r));
  fs.rmSync(tmp, { recursive: true });
}

const [mode, a, b, c] = process.argv.slice(2);
if (mode === 'stills') stills(a, b.split(',').map(Number));
else video(a, Number(b || 4), Number(c || 60));
