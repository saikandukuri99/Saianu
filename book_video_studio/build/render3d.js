// Frame capture for the Three.js engine (software WebGL).
//   node render3d.js frames <outDir> <from> <to> | snap <outDir> <t...> | cues <out.json>
const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs'); const http = require('http');
const ROOT = path.resolve(__dirname, '../renderer3d'), FPS = 30;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.ttf': 'font/ttf', '.json': 'application/json' };
function serve() { return new Promise(res => { const s = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); r.end(d); } }); }).listen(0, () => res(s)); }); }
(async () => {
  const [mode, ...rest] = process.argv.slice(2); const srv = await serve(); const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.type(), m.text()); }); page.on('pageerror', e => console.log('[pageerror]', e.message));
  await page.goto(`http://localhost:${port}/index.html`); await page.waitForFunction('window.READY === true', null, { timeout: 120000 });
  if (mode === 'frames') {
    const [out, a, b] = [rest[0], +rest[1], +rest[2]]; fs.mkdirSync(out, { recursive: true }); const t0 = Date.now();
    for (let f = a; f < b; f++) { const b64 = await page.evaluate(t => window.grab(t), f / FPS); fs.writeFileSync(path.join(out, `f_${String(f).padStart(6, '0')}.jpg`), Buffer.from(b64, 'base64')); if ((f - a) % 50 === 0) console.log(`frame ${f} (${a}-${b}) ${((Date.now() - t0) / 1000).toFixed(0)}s`); }
  } else if (mode === 'snap') {
    const out = rest[0]; fs.mkdirSync(out, { recursive: true });
    for (const t of rest.slice(1)) { const b64 = await page.evaluate(t => window.grab(t, .97), +t); fs.writeFileSync(path.join(out, `snap_${(+t).toFixed(2)}.jpg`), Buffer.from(b64, 'base64')); }
  } else if (mode === 'cues') { const cues = await page.evaluate(() => window.getCues()); fs.writeFileSync(rest[0], JSON.stringify(cues)); console.log(cues.length, 'cues'); }
  await browser.close(); srv.close();
})();
