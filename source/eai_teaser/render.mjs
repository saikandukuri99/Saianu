// Frame renderer: drives the composition with seek(t) in headless Chromium and
// writes JPEG frames. Usage:
//   node render.mjs stills <outdir> <scale> t1 t2 ...
//   node render.mjs frames <outdir> <scale> <fps> <worker> <nworkers>
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
const [mode, out, scale, ...rest] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--allow-file-access-from-files', '--disable-gpu-vsync', '--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: +scale });
page.on('pageerror', e => console.error('PAGEERR', e.message));
page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
await page.goto('file://' + path.resolve('web/index.html') + (process.env.NOCAP ? '?nocap' : ''));
await page.evaluate(() => window.ready);
async function shot(t, file) {
  await page.evaluate(t => window.seek(t), t);
  // page.screenshot honours deviceScaleFactor (scale 2 => native 3840x2160)
  await page.screenshot({ path: file, type: 'jpeg', quality: 95 });
}
if (mode === 'stills') {
  for (const t of rest) await shot(+t, `${out}/t${(+t).toFixed(2).padStart(7, '0')}.jpg`);
} else {
  const [fps, wi, nw] = rest.map(Number);
  const total = await page.evaluate(() => window.TOTAL);
  const N = Math.round(total * fps);
  const t0 = Date.now();
  for (let f = wi; f < N; f += nw) {
    const file = `${out}/f${String(f).padStart(5, '0')}.jpg`;
    if (fs.existsSync(file)) continue;
    await shot(f / fps, file);
    if (f % (nw * 60) === wi) console.log(`w${wi} ${f}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
}
await browser.close();
