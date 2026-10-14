// Discovery Bay part 1: bus between levels, carried state, golf carts (drive, water stop, building bump, hop off), resident carts.
// Needs perf3.html = index.html with the debug hook (see HANDOFF #3) and three r128 + playwright under $TLIB (default tests/lib).
const { chromium } = require(process.env.TLIB ? process.env.TLIB + '/node_modules/playwright' : 'playwright'); const fs = require('fs'), path = require('path');
const LIB = process.env.TLIB || path.join(__dirname, 'lib'), OUT = process.env.OUT || __dirname;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(path.join(LIB, 'node_modules/three/build/three.min.js')), contentType: 'application/javascript' }); return r.abort() });
  await p.setContent(fs.readFileSync(process.env.PERF || path.join(__dirname, 'perf3.html'), 'utf8'));
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 };
  const g = f => p.evaluate(f);
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.fill('#dogName', 'Biscuit'); await p.click('#startBtn'); await p.waitForTimeout(1500);
  ok(await g(() => __g.LEVEL === 'hy'), 'starts in Ha Yeung');
  // park the bus at the stop and walk the dog over
  await g(() => { const G = __g; G.S.points = 777; G.S.stash = ['stick', 'stone']; G.S.todos.dig = true;
    Object.assign(G.bus, { state: 'dwell', dwell: 120, s: G.PL.stop_s, stopped: true, v: 0 }); G.bus.g.visible = true; G.placeVehicle(G.bus);
    G.dog.x = G.PL.stop[0]; G.dog.z = G.PL.stop[1] });
  await p.waitForTimeout(1500);
  ok(await g(() => { const a = __g.ctxAction(); return a && a.l === 'Board bus' }), 'Board bus offered at the stop');
  ok(await p.isVisible('#aCtx'), 'Board bus button visible: ' + await p.textContent('#aCtx'));
  await p.screenshot({ path: path.join(OUT, 'db1_hy_stop.png') });
  await p.keyboard.press('x'); await p.waitForTimeout(400);
  ok(await p.evaluate(() => document.getElementById('fade').classList.contains('on') && document.getElementById('fadeMsg').textContent), 'fade shown: ' + await p.textContent('#fadeMsg'));
  await p.screenshot({ path: path.join(OUT, 'db2_fade.png') });
  await p.waitForFunction(() => window.__g && __g.LEVEL === 'db' && !document.getElementById('fade').classList.contains('on'), null, { timeout: 120000 });
  await p.waitForTimeout(1500);
  const st = await g(() => ({ name: __g.S.name, pts: __g.S.points, stash: __g.S.stash.join(','), dig: __g.S.todos.dig, bus: __g.S.todos.bus, canvases: document.querySelectorAll('canvas').length, place: document.getElementById('plName').textContent, taxi: __g.taxi.wait, mini: __g.mini.wait,
    stashItems: __g.items.filter(i => i.state === 'stash').length, nearStop: Math.hypot(__g.dog.x - __g.PL.stop[0], __g.dog.z - __g.PL.stop[1]) - 6 }));
  console.log(JSON.stringify(st));
  ok(st.name === 'Biscuit' && st.pts >= 777 && st.stash === 'stick,stone' && st.dig && st.bus, 'name, points, stash, to-dos carried; bus to-do done');
  ok(st.canvases === 3, 'one WebGL canvas (plus the 2 map canvases): ' + st.canvases);
  ok(st.place === 'Discovery Bay' && st.taxi === Infinity && st.mini === Infinity && st.stashItems === 2 && Math.abs(st.nearStop) < 3, 'DB labels, no taxi/minibus, stash rebuilt, dog at terminus');
  await p.screenshot({ path: path.join(OUT, 'db3_arrive.png') });
  // hop on a parked cart and drive
  await g(() => { const k = __g.carts[0]; __g.dog.x = k.x + Math.cos(k.h) * 1.8; __g.dog.z = k.z - Math.sin(k.h) * 1.8 });
  await p.waitForTimeout(800);
  ok(await g(() => { const a = __g.ctxAction(); return a && a.l === 'Hop on' }), 'Hop on offered next to a parked cart');
  await p.keyboard.press('x'); await p.waitForTimeout(500);
  ok(await g(() => !!__g.dog.cart), 'dog is in the cart');
  const p0 = await g(() => [__g.dog.cart.x, __g.dog.cart.z]);
  await g(() => { __g.dog.cart.dist = 50 }); await p.keyboard.down('w'); await p.waitForTimeout(14000); await p.keyboard.down('a'); await p.waitForTimeout(2500); await p.keyboard.up('a');
  const p1 = await g(() => ({ x: __g.dog.cart.x, z: __g.dog.cart.z, v: __g.dog.cart.v, dx: __g.dog.x, dy: __g.dog.y, cy: __g.dog.cart.y }));
  await p.screenshot({ path: path.join(OUT, 'db4_drive.png') });
  await p.keyboard.up('w');
  console.log(JSON.stringify(p1));
  ok(Math.hypot(p1.x - p0[0], p1.z - p0[1]) > 2 && p1.dy > p1.cy + 0.5, 'cart drove ' + Math.hypot(p1.x - p0[0], p1.z - p0[1]).toFixed(1) + ' m with the dog on the seat');
  // water: aim at the sea from the fisherman's spot
  await g(() => { const G = __g, k = G.dog.cart, f = G.PL.fisher, l = G.PL.fisherLook; const dx = l[0] - f[0], dz = l[1] - f[1], L = Math.hypot(dx, dz); k.h = Math.atan2(dx, dz); k.x = f[0] - dx / L * 10; k.z = f[1] - dz / L * 10; k.v = 0 });
  await p.keyboard.down('w'); await p.waitForTimeout(9000);
  const w = await g(() => ({ h: __g.gridH(__g.dog.cart.x, __g.dog.cart.z), v: __g.dog.cart.v }));
  await p.screenshot({ path: path.join(OUT, 'db5_water.png') }); await p.keyboard.up('w');
  ok(w.h > 0.2, 'cart stopped at the water (ground under cart ' + w.h.toFixed(2) + ' m)');
  // building: aim at the nearest building's centre
  const inB = await g(() => { const G = __g, k = G.dog.cart; let best = null, bd = 1e9; for (const b of G.BL) { const cx = (b.bb[0] + b.bb[1]) / 2, cz = (b.bb[2] + b.bb[3]) / 2; const d = Math.hypot(cx - G.PL.stop[0], cz - G.PL.stop[1]); if (d < bd && b.a > 80) { bd = d; best = [cx, cz] } }
    k.x = best[0] - 14; k.z = best[1]; k.h = Math.PI / 2; k.v = 0; return best });
  await p.keyboard.down('w'); let entered = false; for (let i = 0; i < 12; i++) { await p.waitForTimeout(600); if (await g(() => !!__g.bldAt(__g.dog.cart.x, __g.dog.cart.z))) entered = true }
  await p.keyboard.up('w');
  ok(!entered, 'cart never entered the building');
  await p.waitForTimeout(2500);
  ok(await g(() => { const a = __g.ctxAction(); return a && a.l === 'Hop off' }), 'Hop off offered when stopped');
  await p.keyboard.press('x'); await p.waitForTimeout(500);
  ok(await g(() => !__g.dog.cart && !__g.bldAt(__g.dog.x, __g.dog.z)), 'hopped off onto open ground');
  ok(await g(() => __g.aiCarts.some(c => c.g.visible)), 'resident carts on ' + await g(() => __g.WD.roadName));
  await g(() => { const k = __g.aiCarts.find(c => c.g.visible); __g.dog.x = k.x + 6; __g.dog.z = k.z + 6; __g.cam.dist = 9 });
  await p.waitForTimeout(1200); await p.screenshot({ path: path.join(OUT, 'db6_resident_cart.png') });
  // and back
  await g(() => { const G = __g; Object.assign(G.bus, { state: 'dwell', dwell: 120, s: G.PL.stop_s, stopped: true, v: 0 }); G.bus.g.visible = true; G.placeVehicle(G.bus); G.dog.x = G.PL.stop[0]; G.dog.z = G.PL.stop[1] });
  await p.waitForTimeout(800); await p.click('#aCtx');
  await p.waitForFunction(() => window.__g && __g.LEVEL === 'hy' && !document.getElementById('fade').classList.contains('on'), null, { timeout: 120000 });
  await p.waitForTimeout(1500);
  const back = await g(() => ({ pts: __g.S.points, cart: __g.S.todos.cart, stash: __g.items.filter(i => i.state === 'stash').length, canvases: document.querySelectorAll('canvas').length, bubbles: document.querySelectorAll('#bubbles .bubble').length }));
  console.log(JSON.stringify(back));
  ok(back.cart && back.stash === 2 && back.canvases === 3, 'back in Ha Yeung with cart to-do, stash and a single GL canvas');
  await p.screenshot({ path: path.join(OUT, 'db7_back.png') });
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close()
})();
