// Headless smoke test: boots a debug copy (tests/mkdebug.py) in a level with a breed, starts the day,
// runs a few seconds, prints a state summary and any page errors. Exit code 1 on errors.
//   TLIB=<dir with node_modules/{playwright,three}> PERF=<debug copy> LEVEL=hy|db BREED=golden|... [OUT=<dir> SHOT=name] node tests/smoke.js
const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 600 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => r.request().url().includes('three.min.js') ? r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }) : r.abort());
  const boot = { level: process.env.LEVEL || 'hy' }; if (process.env.BREED) boot.breed = process.env.BREED;
  const html = '<script>window.__BOOT=' + JSON.stringify(boot) + '</script>' + fs.readFileSync(process.env.PERF, 'utf8');
  await p.setContent(html);
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 180000 });
  if (process.env.BREED) await p.evaluate(br => { const r = document.querySelector('input[name=breed][value="' + br + '"]'); if (r) r.checked = true }, process.env.BREED);
  await p.click('#startBtn');
  await p.waitForFunction(() => window.__g && __g.S && __g.S.started, null, { timeout: 60000 });
  await p.waitForTimeout(+(process.env.WAIT || 4000));
  const st = await p.evaluate(() => ({ level: __g.LEVEL, breed: __g.S.breed, Dbreed: __g.D && __g.D.breed, pos: [+__g.dog.x.toFixed(1), +__g.dog.z.toFixed(1)] }));
  console.log(JSON.stringify(st));
  if (process.env.OUT) await p.screenshot({ path: process.env.OUT + '/' + (process.env.SHOT || 'smoke') + '.png' });
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close();
})();
