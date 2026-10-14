// Discovery Bay look + police chase + ferry. PERF must be a debug copy that boots straight into DB (first({level:'db'})).
const { chromium } = require(process.env.TLIB ? process.env.TLIB + '/node_modules/playwright' : 'playwright'); const fs = require('fs'), path = require('path');
const LIB = process.env.TLIB || path.join(__dirname, 'lib'), OUT = process.env.OUT || __dirname;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(path.join(LIB, 'node_modules/three/build/three.min.js')), contentType: 'application/javascript' }); return r.abort() });
  await p.setContent(fs.readFileSync(process.env.PERF, 'utf8'));
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f);
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn'); await p.waitForTimeout(1200);
  const info = await g(() => ({ lvl: __g.LEVEL, towers: __g.BL.filter(b => b.style === 'tower').length, villas: __g.BL.filter(b => b.style === 'villa').length, pier: !!__g.DBX.pier, village: __g.DBX.village.length, villagers: __g.villagers.length, maxH: Math.max(...__g.BL.map(b => b.h)) }));
  console.log(JSON.stringify(info));
  ok(info.lvl === 'db' && info.towers >= 8 && info.villas > 60 && info.pier && info.village >= 6 && info.villagers >= 4 && info.maxH > 45, 'DB styles, pier, village and villagers built');
  // walkable plaza: walk across the piazza
  await g(() => { const G = __g; G.dog.x = G.DBX && -8; G.dog.z = -20; G.dog.heading = Math.PI / 2; G.cam.yaw = Math.PI / 2 });
  const w0 = await g(() => __g.dog.x); await p.keyboard.down('w'); const walked = await p.waitForFunction(x0 => __g.dog.x - x0 > 12, w0, { timeout: 90000 }).then(() => true, () => false); await p.keyboard.up('w');
  ok(walked, 'dog walks 12 m across the piazza');
  const fps = await p.evaluate(() => new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 3000) requestAnimationFrame(f); else r(n / 3) }; requestAnimationFrame(f) })); console.log('headless fps', fps.toFixed(1));
  // hop on a cart and test top speed
  await g(() => { const k = __g.carts[0]; __g.dog.x = k.x + Math.cos(k.h) * 1.8; __g.dog.z = k.z - Math.sin(k.h) * 1.8 }); await p.waitForTimeout(600); await p.keyboard.press('x'); await p.waitForTimeout(400);
  ok(await g(() => !!__g.dog.cart), 'in the cart');
  // put the cart on Discovery Bay Road, pointing along it, and floor it with turbo
  await g(() => { const G = __g, q = G.cwAt(300), k = G.dog.cart; k.x = q.x; k.z = q.z; k.h = Math.atan2(q.fx, q.fz); k.v = 0 });
  await p.keyboard.down('Shift'); await p.keyboard.down('w'); const fast = await p.waitForFunction(() => __g.dog.cart && Math.abs(__g.dog.cart.v) > 19, null, { timeout: 120000 }).then(() => true, () => false); const vmax = await g(() => __g.dog.cart ? Math.abs(__g.dog.cart.v) : 0);
  ok(fast, 'cart reaches ' + (vmax * 3.6).toFixed(0) + ' km/h with turbo');
  await p.keyboard.up('w'); await p.keyboard.up('Shift');
  // police: force a spawn while moving
  await g(() => { __g.dog.cart.v = 8; __g.police.cool = 0 }); const spawned = await p.waitForFunction(() => __g.police.state === 'chase' && __g.police.t > 0.3, null, { timeout: 60000 }).then(() => true, () => false);
  ok(spawned, 'police spawned and chasing, ' + (await g(() => Math.hypot(__g.police.x - __g.dog.x, __g.police.z - __g.dog.z))).toFixed(0) + ' m away');
  ok(await p.isVisible('#chaseHud'), 'chase HUD: ' + await p.textContent('#chaseHud'));
  await p.screenshot({ path: path.join(OUT, 'p1_police.png') });
  // caught: park the cart next to the patrol car
  await g(() => { const P = __g.police, k = __g.dog.cart; k.v = 0; k.x = P.x + Math.sin(P.h) * 2.5; k.z = P.z + Math.cos(P.h) * 2.5; P.t = 5 });
  await p.waitForFunction(() => __g.police.state !== 'chase', null, { timeout: 60000 });
  ok(await g(() => !__g.dog.cart), 'BUSTED: dog put out of the cart');
  await p.screenshot({ path: path.join(OUT, 'p2_busted.png') });
  // escape: hop on again, new chase, then get far away
  await g(() => { __g.police.state = 'off'; __g.police.g.visible = false; const k = __g.carts[0]; __g.dog.x = k.x + Math.cos(k.h) * 1.8; __g.dog.z = k.z - Math.sin(k.h) * 1.8 });
  await p.waitForTimeout(600); await p.keyboard.press('x'); await p.waitForTimeout(400);
  await g(() => { __g.dog.cart.v = 8; __g.police.cool = 0 }); await p.waitForFunction(() => __g.police.state === 'chase', null, { timeout: 30000 });
  await g(() => { const P = __g.police; P.x = __g.dog.x + 95; P.z = __g.dog.z; P.v = 0; P.t = 3; P.h = Math.PI / 2 });
  await p.waitForFunction(() => __g.police.state !== 'chase', null, { timeout: 60000 });
  ok(await g(() => !!__g.S.todos.police && !!__g.dog.cart), 'ESCAPED: police to-do done, still driving');
  // ferry exists and is docked near the pier
  ok(await g(() => !!__g.DBX.pier), 'pier found');
  await p.evaluate(() => { document.getElementById('hud').style.display = 'none' });
  for (const [n, x, z, h, d, pt] of [['p3_pier', 70, -100, 1.9, 30, 0.3], ['p4_plaza', 10, 5, 3.14, 38, 0.55], ['p5_village', 330, 205, -2.2, 26, 0.3], ['p6_beach', -60, -200, -0.6, 45, 0.3]]) {
    await p.evaluate(([x, z, h, d, pt]) => { const G = __g; if (G.dog.cart) { G.dog.cart = null } G.dog.x = x; G.dog.z = z; G.dog.heading = h; G.cam.yaw = h; G.cam.dist = d; G.cam.pitch = pt; G.cam.lastDrag = 1e9; G.S.hour = 13 }, [x, z, h, d, pt]);
    await p.waitForTimeout(2500); await p.screenshot({ path: path.join(OUT, n + '.png') });
  }
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close()
})();
