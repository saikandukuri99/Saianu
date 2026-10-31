// Frame capture driver for the SVG engine.
//   node render.js frames <outDir> <startFrame> <endFrame>     -> f_000123.jpg ...
//   node render.js snap <outDir> <t1> <t2> ...                  -> snap_<t>.png (for review)
//   node render.js cues <outJson>                               -> sound-effect cue list
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const PAGE = process.env.PAGE ? 'file://' + path.resolve(process.env.PAGE) : 'file://' + path.resolve(__dirname, '../renderer/index.html');
const FPS = 30;

async function open() {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.type(), m.text()); });
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  await page.goto(PAGE);
  await page.waitForFunction('window.READY === true', null, { timeout: 60000 });
  return { browser, page };
}

(async () => {
  const [mode, ...rest] = process.argv.slice(2);
  const { browser, page } = await open();
  if (mode === 'frames') {
    const [out, a, b] = [rest[0], +rest[1], +rest[2]];
    fs.mkdirSync(out, { recursive: true });
    const t0 = Date.now();
    for (let f = a; f < b; f++) {
      await page.evaluate(t => window.seek(t), f / FPS);
      await page.screenshot({ path: path.join(out, `f_${String(f).padStart(6, '0')}.jpg`), type: 'jpeg', quality: 95 });
      if ((f - a) % 100 === 0) console.log(`frame ${f} (${a}-${b}) ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
  } else if (mode === 'snap') {
    const out = rest[0]; fs.mkdirSync(out, { recursive: true });
    for (const t of rest.slice(1)) {
      await page.evaluate(t => window.seek(t), +t);
      await page.screenshot({ path: path.join(out, `snap_${(+t).toFixed(2)}.png`) });
    }
  } else if (mode === 'cues') {
    const cues = await page.evaluate(() => window.getCues());
    fs.writeFileSync(rest[0], JSON.stringify(cues));
    console.log(cues.length, 'cues');
  }
  await browser.close();
})();
