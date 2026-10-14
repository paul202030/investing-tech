const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 };
  await p.setContent(fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn'); await p.waitForTimeout(1500);
  await p.evaluate(() => { __g.S.points = 950; __g.S.coins = 180; __g.dog.x += 5 });
  const before = await p.evaluate(() => ({ x: __g.dog.x, pts: __g.S.points }));
  await p.evaluate(() => { const c = document.querySelector('#game canvas'); const gl = c.getContext('webgl2') || c.getContext('webgl'); gl.getExtension('WEBGL_lose_context').loseContext() });
  await p.waitForTimeout(500); ok(await p.evaluate(() => document.getElementById('fade').classList.contains('on')), 'restoring overlay shown');
  await p.waitForFunction(() => window.__g && __g.S.started && __g.S.recover && !document.getElementById('fade').classList.contains('on'), null, { timeout: 120000 }).catch(() => {});
  const after = await p.evaluate(() => ({ x: __g.dog.x, pts: __g.S.points, coins: __g.S.coins, lost: !document.getElementById('lostMsg').hidden, canvases: document.querySelectorAll('#game canvas').length }));
  console.log(JSON.stringify(before), JSON.stringify(after));
  ok(!after.lost && after.pts === 950 && after.coins === 180 && Math.abs(after.x - before.x) < 1 && after.canvases === 1, 'rebuilt in place: no Reload screen, points/coins/position kept, one canvas');
  await p.waitForTimeout(1500); await p.screenshot({ path: process.env.OUT + '/r1.png' });
  console.log(errs.join('\n') || 'NO_ERRORS'); await b.close()
})();
