const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f); const w = (f, t) => p.waitForFunction(f, null, { timeout: t || 60000 }).then(() => true, () => false);
  await p.setContent(fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 180000 }); await p.click('#startBtn'); await p.waitForTimeout(1200);
  const info = await g(() => ({ lv: __g.LEVEL, bld: __g.BL.length, box: [__g.WD.x0, __g.WD.z0], carts: __g.carts.length, police: !!__g.police, marina: __g.DBX.marina }));
  console.log(JSON.stringify(info)); ok(info.lv === 'db' && info.bld > 800 && info.marina > 10, 'one Discovery Bay level with north + middle buildings');
  await p.evaluate(() => { document.getElementById('hud').style.display = 'none' });
  for (const [n, x, z, h, d, pt] of [['m1_marina', 880, 300, 1.6, 70, 0.55], ['m2_marina', 1000, 250, 3.1, 50, 0.4]]) {
    await p.evaluate(([x, z, h, d, pt]) => { const G = __g; G.dog.x = x; G.dog.z = z; G.dog.heading = h; G.cam.yaw = h; G.cam.dist = d; G.cam.pitch = pt; G.cam.lastDrag = 1e9; G.S.hour = 13 }, [x, z, h, d, pt]);
    await p.waitForTimeout(2500); await p.screenshot({ path: process.env.OUT + '/' + n + '.png' }) }
  await p.evaluate(() => { document.getElementById('hud').style.display = '' });
  await g(() => { const G = __g; Object.assign(G.bus, { state: 'dwell', dwell: 120, s: G.PL.stop_s, stopped: true, v: 0 }); G.bus.g.visible = true; G.placeVehicle(G.bus); G.dog.x = G.PL.stop[0]; G.dog.z = G.PL.stop[1] });
  await w(() => { const a = __g.ctxAction(); return a && a.l === 'Board bus' }); await p.keyboard.press('x');
  ok(await w(() => window.__g && __g.LEVEL === 'hy' && !document.getElementById('fade').classList.contains('on'), 120000), 'bus goes straight to Ha Yeung (no picker)');
  console.log(errs.join('\n') || 'NO_ERRORS'); await b.close()
})();
