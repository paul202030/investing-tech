const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f); const w = (f, t) => p.waitForFunction(f, null, { timeout: t || 60000 }).then(() => true, () => false);
  const parkBus = () => g(() => { const G = __g; Object.assign(G.bus, { state: 'dwell', dwell: 120, s: G.PL.stop_s, stopped: true, v: 0 }); G.bus.g.visible = true; G.placeVehicle(G.bus); G.dog.x = G.PL.stop[0]; G.dog.z = G.PL.stop[1] });
  await p.setContent(fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn'); await p.waitForTimeout(1200);
  ok(await g(() => __g.LEVEL === 'db'), 'starts in Discovery Bay');
  await parkBus(); await w(() => { const a = __g.ctxAction(); return a && a.l === 'Board bus' }); await p.keyboard.press('x'); await p.waitForTimeout(400);
  ok(await p.isVisible('#busBox') && (await p.textContent('#busBtns')).includes('Discovery Bay North'), 'bus picker: ' + await p.textContent('#busBtns'));
  await p.click('#busBtns button:has-text("North")');
  ok(await w(() => window.__g && __g.LEVEL === 'dbn' && !document.getElementById('fade').classList.contains('on'), 120000), 'arrived in Discovery Bay North');
  await p.waitForTimeout(1500);
  const info = await g(() => ({ place: document.getElementById('plName').textContent, carts: __g.carts.length, ai: __g.aiCarts.length, police: !!__g.police, towers: __g.BL.filter(b => b.style === 'tower').length, villas: __g.BL.filter(b => b.style === 'villa').length, north: !!__g.S.todos.north, canv: document.querySelectorAll('#game canvas').length }));
  console.log(JSON.stringify(info)); ok(info.place === 'Discovery Bay North' && info.carts >= 3 && info.ai === 3 && info.police && info.north && info.canv === 1, 'DB North: carts, resident carts, police, to-do, one canvas');
  await p.screenshot({ path: process.env.OUT + '/n1_arrive.png' });
  await p.evaluate(() => { document.getElementById('hud').style.display = 'none' });
  for (const [n, x, z, h, d, pt] of [['n2_plaza', 150, -20, 1.6, 40, 0.45], ['n3_beach', 300, -280, 0.8, 40, 0.35], ['n4_villas', -250, 150, 3.0, 45, 0.45]]) {
    await p.evaluate(([x, z, h, d, pt]) => { const G = __g; G.dog.x = x; G.dog.z = z; G.dog.heading = h; G.cam.yaw = h; G.cam.dist = d; G.cam.pitch = pt; G.cam.lastDrag = 1e9; G.S.hour = 13 }, [x, z, h, d, pt]);
    await p.waitForTimeout(2500); await p.screenshot({ path: process.env.OUT + '/' + n + '.png' }) }
  await p.evaluate(() => { document.getElementById('hud').style.display = '' });
  await parkBus(); await w(() => { const a = __g.ctxAction(); return a && a.l === 'Board bus' }); await p.keyboard.press('x');
  ok(await w(() => window.__g && __g.LEVEL === 'db' && !document.getElementById('fade').classList.contains('on'), 120000), 'bus back to Discovery Bay (no picker, one destination)');
  console.log(errs.join('\n') || 'NO_ERRORS'); await b.close()
})();
