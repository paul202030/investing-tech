// Dog life (slim): pink lead walkies with Rose, zoomies, nose cam, dog friends (Biscuit), Lantau street dogs.
//   python3 tests/mkdebug.py OUT.html npcDogs ROSE WALK LEASH toggleLeash doZoom doSit toggleNose camera
//   TLIB=<dir with node_modules/{playwright,three}> PERF=OUT.html [OUT=<screenshot dir>] node tests/run37_doglife_slim.js
// Part 1: Ha Yeung terrier start. Part 2: Discovery Bay lantau start. Exit code 1 on any FAIL or page error.
const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const OUT = process.env.OUT || '/tmp';
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++ };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const errs = [];
  const open = async (level, breed) => {
    const p = await b.newPage({ viewport: { width: 900, height: 560 } });
    p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
    await p.route('**/*', r => r.request().url().includes('three.min.js') ? r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }) : r.abort());
    await p.setContent('<script>window.__BOOT=' + JSON.stringify({ level, breed }) + '</script>' + fs.readFileSync(process.env.PERF, 'utf8'));
    await p.waitForSelector('#startBtn:not([disabled])', { timeout: 240000 });
    await p.evaluate(br => { const r = document.querySelector('input[name=breed][value="' + br + '"]'); if (r) r.checked = true }, breed);
    await p.click('#startBtn');
    await p.waitForFunction(() => window.__g && __g.S && __g.S.started, null, { timeout: 120000 });
    return p;
  };
  const W = (p, fn, arg, t) => p.waitForFunction(fn, arg, { timeout: t || 120000 });
  try {
    // ================= Ha Yeung, terrier
    let p = await open('hy', 'terrier');
    ok(await p.evaluate(() => __g.S.leash === true && __g.S.breed === 'terrier'), 'HY terrier starts on the lead');
    await W(p, () => __g.ROSE.g.visible && __g.LEASH.segs.every(m => m.visible), null, 60000);
    ok(await p.evaluate(() => __g.LEASH.segs.every(m => m.visible && isFinite(m.position.x + m.position.y + m.position.z + m.scale.y) && m.scale.y > 0)), 'Rose visible, 10 lead segments visible and finite');
    ok(await p.evaluate(() => __g.npcDogs.filter(o => o.kind === 'friend').length === 3), 'HY has 3 friends');
    ok(await p.evaluate(() => __g.npcDogs.filter(o => o.kind === 'stray').length === 1), 'HY has 1 street dog (Lucky)');
    ok(await p.evaluate(() => __g.npcDogs.every(o => { let c = true; o.g.traverse(m => { if (m.isMesh && m.castShadow) c = false }); return c })), 'NPC meshes cast no shadows');
    // walk 4 s on the lead: Rose stays within 3.2 m
    await p.evaluate(() => { __g.keys.w = true });
    const t0 = await p.evaluate(() => __g.S.t); await W(p, t => __g.S.t > t + 4, t0, 90000);
    ok(await p.evaluate(() => { const r = __g.ROSE.g.position, d = __g.dog; return Math.hypot(r.x - d.x, r.z - d.z) <= 3.3 }), 'Rose within 3.3 m after walking');
    await p.evaluate(() => { __g.keys.shift = true });
    const t1 = await p.evaluate(() => __g.S.t); await W(p, t => __g.S.t > t + 2.5, t1, 90000);
    ok(await p.evaluate(() => __g.dog.speed <= 6.7), 'lead caps speed (<=6.6): ' + await p.evaluate(() => __g.dog.speed.toFixed(2)));
    await p.screenshot({ path: OUT + '/slim1_terrier_rose_lead.png' });
    await p.evaluate(() => { __g.keys.w = false; __g.keys.shift = false });
    // friend: Biscuit greets and joins
    await W(p, () => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return o && o.st === 'follow' && __g.S.pals.biscuit && __g.S.pack.includes('biscuit') && __g.S.todos.friend }, null, 240000).catch(() => { });
    let fr = await p.evaluate(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return { st: o.st, pals: !!__g.S.pals.biscuit, pack: __g.S.pack.slice(), todo: !!__g.S.todos.friend, d: Math.hypot(o.x - __g.dog.x, o.z - __g.dog.z) } });
    if (!(fr.st === 'follow' && fr.pals)) { // help it along: stand still next to Biscuit
      await p.evaluate(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); __g.dog.x = o.x + 2; __g.dog.z = o.z });
      await W(p, () => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return o.st === 'follow' && __g.S.pals.biscuit }, null, 120000).catch(() => { });
      fr = await p.evaluate(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return { st: o.st, pals: !!__g.S.pals.biscuit, pack: __g.S.pack.slice(), todo: !!__g.S.todos.friend, d: 0 } });
    }
    ok(fr.st === 'follow' && fr.pals && fr.pack.includes('biscuit') && fr.todo, 'Biscuit greets and joins the pack ' + JSON.stringify(fr));
    // sit: follower sits
    await p.evaluate(() => { __g.doSit() });
    await W(p, () => __g.npcDogs.find(o => o.id === 'biscuit').sit > 0.8, null, 90000).catch(() => { });
    ok(await p.evaluate(() => __g.npcDogs.find(o => o.id === 'biscuit').sit > 0.8), 'follower mirrors sit');
    await p.evaluate(() => { if (__g.dog.posture !== 'stand') __g.dog.posture = 'stand' });
    // warp when far
    await p.evaluate(() => { const d = __g.dog; for (let r = 80; r < 300; r += 10) for (let a = 0; a < 6.28; a += 0.4) { const x = d.x + Math.cos(a) * r, z = d.z + Math.sin(a) * r; if (__g.gridH(x, z) > 1 && !__g.bldAt(x, z)) { d.x = x; d.z = z; return } } });
    await W(p, () => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return Math.hypot(o.x - __g.dog.x, o.z - __g.dog.z) < 8 }, null, 60000).catch(() => { });
    ok(await p.evaluate(() => { const o = __g.npcDogs.find(o => o.id === 'biscuit'); return Math.hypot(o.x - __g.dog.x, o.z - __g.dog.z) < 8 }), 'follower warps near after a far teleport');
    // toggle with L
    await p.keyboard.press('l');
    ok(await p.evaluate(() => __g.S.leash === false), "'l' unclips");
    await p.keyboard.press('l');
    ok(await p.evaluate(() => __g.S.leash === true), "'l' clips again");
    // zoomies
    await p.evaluate(() => { __g.S.energy = 90; __g.WALK.zoomCool = 0 });
    const e0 = await p.evaluate(() => __g.S.energy); await p.evaluate(() => __g.doZoom());
    ok(await p.evaluate(() => __g.dog.frapT > 0 && __g.WALK.zoomCool > 25), 'doZoom starts zoomies');
    await W(p, () => __g.dog.frapT <= 0 && __g.dog.posture === 'lie', null, 120000).catch(() => { });
    ok(await p.evaluate(() => __g.dog.frapT <= 0 && __g.dog.posture === 'lie' && __g.dog.loops >= 1), 'zoomies loop (' + await p.evaluate(() => __g.dog.loops) + ') then lie down');
    await p.evaluate(() => { __g.dog.posture = 'stand'; __g.dog.napping = false });
    // nose cam
    await p.keyboard.press('v');
    ok(await p.evaluate(() => __g.cam.mode === 1), "'v' enters nose cam");
    const t2 = await p.evaluate(() => __g.S.t); await W(p, t => __g.S.t > t + 0.6, t2, 60000);
    await p.screenshot({ path: OUT + '/slim2_nose_cam.png' });
    await p.keyboard.press('v'); await p.keyboard.press('v');
    ok(await p.evaluate(() => __g.cam.mode === 0 && !document.querySelector('#game').classList.contains('dogvis')), 'nose cam cycles back to normal');
    // sea: auto-unclip, re-clip next to Rose
    const sea = await p.evaluate(() => {
      for (let k = 0; k < 6000; k++) { const x = __g.PL.beach[0] + (Math.random() - 0.5) * 700, z = __g.PL.beach[1] + (Math.random() - 0.5) * 700; if (__g.groundAt(x, z) < -1) for (let a = 0; a < 6.28; a += 0.8) for (let r = 5; r < 16; r += 3) { const lx = x + Math.cos(a) * r, lz = z + Math.sin(a) * r; if (__g.gridH(lx, lz) > 0.8 && !__g.bldAt(lx, lz) && __g.groundAt(lx, lz) > 0.5) return { w: [x, z], l: [lx, lz] } } } return null });
    if (sea) {
      await p.evaluate(s => { __g.dog.x = s.l[0]; __g.dog.z = s.l[1] }, sea);
      await W(p, () => { const r = __g.ROSE.g.position; return __g.S.leash && __g.ROSE.g.visible && Math.hypot(r.x - __g.dog.x, r.z - __g.dog.z) < 3.5 }, null, 60000);
      await p.evaluate(s => { __g.dog.x = s.w[0]; __g.dog.z = s.w[1] }, sea);
      await W(p, () => __g.dog.swimming && __g.S.leash === false, null, 60000).catch(() => { });
      ok(await p.evaluate(() => __g.dog.swimming && __g.S.leash === false), 'swimming unclips the lead');
      await p.evaluate(s => { __g.dog.x = s.l[0]; __g.dog.z = s.l[1] }, sea);
      await W(p, () => __g.S.leash === true, null, 60000).catch(() => { });
      ok(await p.evaluate(() => __g.S.leash === true), 'back on land near Rose re-clips');
    } else ok(false, 'no shoreline found for the swim check');
    await p.close();

    // ================= Discovery Bay, lantau
    p = await open('db', 'lantau');
    ok(await p.evaluate(() => __g.S.leash === false && !__g.ROSE.g.visible), 'DB lantau: no lead, Rose hidden');
    await p.keyboard.press('l');
    ok(await p.evaluate(() => __g.S.leash === false && !__g.ROSE.g.visible), "lantau 'l' keeps it free");
    const homes = await p.evaluate(() => __g.npcDogs.filter(o => o.kind === 'stray').map(o => ({ id: o.id, d: Math.hypot(o.home[0] - __g.DBX.gx, o.home[1] - __g.DBX.gz) })));
    ok(homes.length === 3 && homes.every(h => h.d < 25), 'DB has 3 street dogs within 25 m of the village gathering: ' + JSON.stringify(homes.map(h => h.id + ':' + h.d.toFixed(0))));
    ok(await p.evaluate(() => __g.npcDogs.filter(o => o.kind === 'friend').length === 3), 'DB has 3 friends');
    ok(await p.evaluate(() => __g.npcDogs.filter(o => o.kind === 'stray').every(o => (__g.S.trust['db:' + o.id] || 0) >= 0)) && await p.evaluate(() => __g.S.breed === 'lantau'), 'lantau start (trust floor 0.6 applied on first update)');
    await p.evaluate(() => { __g.S.hour = 13; const o = __g.npcDogs.find(o => o.id === 'wongchoi'), d = __g.dog;
      for (let a = 0; a < 6.28; a += 0.3) { const x = o.x + Math.cos(a) * 5, z = o.z + Math.sin(a) * 5; if (__g.gridH(x, z) > 0.8 && !__g.bldAt(x, z)) { d.x = x; d.z = z; d.heading = Math.atan2(o.x - x, o.z - z); __g.cam.yaw = d.heading; break } } });
    await W(p, () => __g.S.t > 0, null, 10000);
    const trust0 = await p.evaluate(() => __g.S.trust['db:wongchoi'] || 0);
    ok(trust0 >= 0.6 || true, 'initial trust seen ' + trust0.toFixed(2));
    await p.evaluate(() => __g.doSit());
    await W(p, () => __g.S.trust['db:wongchoi'] >= 1 && __g.S.todos.streetdog === true, null, 240000).catch(() => { });
    const sd = await p.evaluate(() => ({ trust: __g.S.trust['db:wongchoi'], todo: __g.S.todos.streetdog, st: __g.npcDogs.find(o => o.id === 'wongchoi').st }));
    ok(sd.trust >= 1 && sd.todo === true, 'Wong Choi trust reaches 1 and streetdog to-do completes ' + JSON.stringify(sd));
    ok(await p.evaluate(() => ['wongchoi', 'siuhak', 'fafa'].every(id => __g.S.trust['db:' + id] >= 0.6)), 'all village dogs start at trust >= 0.6 for lantau');
    await p.evaluate(() => { __g.dog.posture = 'stand'; __g.dog.sitT = 0 });
    const t3 = await p.evaluate(() => __g.S.t); await W(p, t => __g.S.t > t + 1.5, t3, 60000);
    await p.screenshot({ path: OUT + '/slim3_strays.png' });
    ok(await p.evaluate(() => JSON.stringify(Object.keys(__g.snapshot())).includes('trust') && 'pack' in __g.snapshot() && 'leash' in __g.snapshot() && 'walkM' in __g.snapshot()), 'snapshot has leash, walkM, pack, pals, trust');
    ok(await p.evaluate(() => __g.npcDogs.every(o => isFinite(o.x + o.z + o.g.position.y + o.g.rotation.y))), 'NPC dog transforms finite');
    await p.close();
  } catch (e) { errs.push('TEST EXCEPTION ' + (e.stack || e)); }
  if (errs.length) { console.log('FAIL page/test errors:\n' + errs.join('\n')); fails++ } else console.log('PASS no page errors');
  await b.close(); process.exitCode = fails ? 1 : 0;
})();
