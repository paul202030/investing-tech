// Police chase 3:00 rules + friends riding along. TLIB=... PERF=<mkdebug copy with: npcDogs hopOn spawnPolice endPolice policeCrash nearCart> OUT=... node tests/run38_police_rideon.js
const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 600 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => r.request().url().includes('three.min.js') ? r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }) : r.abort());
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 };
  const w = (f, t) => p.waitForFunction(f, null, { timeout: t || 60000 }).then(() => true, () => false);
  await p.setContent('<script>window.__BOOT={level:"db",breed:"terrier"}</script>' + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 180000 }); await p.click('#startBtn');
  await w(() => window.__g && __g.S.started && __g.npcDogs && __g.npcDogs.length);
  // put Biscuit in the pack, then board a cart
  await p.evaluate(() => { const G = __g, o = G.npcDogs.find(o => o.id === 'biscuit'); G.S.pals.biscuit = { met: 1 }; G.S.pack = ['biscuit']; o.st = 'follow'; o.greeted = true; G.S.leash = false; const k = G.carts[0]; G.dog.x = k.x + 1; G.dog.z = k.z; o.x = k.x + 2; o.z = k.z + 1; G.hopOn(k) });
  ok(await w(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'), k = __g.dog.cart; return k && o.ride === k && !(o.hopT > 0) && Math.hypot(o.x - k.x, o.z - k.z) < 2.5 && o.y > __g.groundAt(o.x, o.z) + 0.3 }, 30000), 'Biscuit jumps into the golf cart');
  ok(await w(() => { if (__g.police.state !== 'chase') { __g.dog.cart.v = 10; __g.spawnPolice() } return __g.police.state === 'chase' }, 30000), 'police spawn');
  ok(await w(() => __g.police.state === 'chase' && document.getElementById('copFx').classList.contains('on')), 'chase starts with red-blue screen FX');
  ok(await p.evaluate(() => document.getElementById('copWipe').className.includes('show')), 'start wipe transition shows');
  ok(await w(() => /POLICE \d:\d\d/.test(document.querySelector('#chaseHud .chWho').textContent), 20000), 'HUD shows a m:ss countdown: ' + await p.evaluate(() => document.querySelector('#chaseHud .chWho').textContent));
  await p.evaluate(() => { __g.police.t = 61 });
  ok(await w(() => __g.police.stage >= 2, 20000), 'stage banners every 30 s');
  await p.evaluate(() => { __g.police.x = __g.dog.x + 40; __g.police.z = __g.dog.z; __g.police.t = 40 });
  await p.waitForTimeout(1500);
  ok(await p.evaluate(() => __g.police.state === 'chase'), 'being 40 m away no longer ends the chase early');
  const pts = await p.evaluate(() => __g.S.points);
  await p.evaluate(() => { __g.police.t = 181 });
  ok(await w(() => __g.police.state === 'leave' && __g.S.points >= 2000), 'surviving 3:00 escapes with +2000');
  await p.screenshot({ path: process.env.OUT + '/police_win.png' });
  await p.evaluate(() => { __g.police.state = 'off' });
  await w(() => { if (__g.police.state !== 'chase') { __g.dog.cart.v = 10; __g.spawnPolice() } return __g.police.state === 'chase' }, 30000);
  await p.evaluate(() => __g.policeCrash('crash'));
  ok(await w(() => __g.police.state === 'leave' && !__g.dog.cart && /CRASH/.test(document.querySelector('#arcade .arcSub').textContent)), 'a crash means BUSTED and out of the cart');
  ok(await w(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return !o.ride && Math.abs(o.g.rotation.x) < 1e-6 }, 20000), 'Biscuit hops out when the dog leaves the cart');
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close();
})();
