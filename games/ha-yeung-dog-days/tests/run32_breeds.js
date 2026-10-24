// Unit 1/5 (breeds): border terrier + Lantau street dog (唐狗) playable next to golden and bichon.
//   python3 tests/mkdebug.py OUT/dbg.html BREEDS BREED_IDS doDig surface breedInfo toastQ
//   TLIB=<dir with node_modules/{playwright,three}> PERF=OUT/dbg.html OUT=<dir> node tests/run32_breeds.js
// Boots each breed via __BOOT (HY: golden, bichon, terrier, lantau; DB: terrier, lantau), clicks Start, runs with
// keys.w + keys.shift for 3 game seconds, checks the breed sticks, the rig stays finite, model options and perks,
// saves a side-view screenshot per breed (#hud hidden), and checks the start card at 390x844.
const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const OUT = process.env.OUT || '.';
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const errs = []; let fails = 0;
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++ };
  const html = fs.readFileSync(process.env.PERF, 'utf8');
  async function open(boot, vp) {
    const p = await b.newPage({ viewport: vp || { width: 1000, height: 620 } });
    p.on('pageerror', e => errs.push(JSON.stringify(boot) + ' ' + (e.stack || e.message)));
    p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(JSON.stringify(boot) + ' ' + m.text()) });
    await p.route('**/*', r => r.request().url().includes('three.min.js') ? r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }) : r.abort());
    await p.setContent('<script>window.__BOOT=' + JSON.stringify(boot) + '</script>' + html);
    await p.waitForSelector('#startBtn:not([disabled])', { timeout: 240000 });
    return p;
  }
  const w = (p, f, a, t) => p.waitForFunction(f, a, { timeout: t || 120000 }).then(() => true, () => false);

  // ---------------------------------------------------------------- start card on a phone
  {
    const p = await open({ level: 'hy' }, { width: 390, height: 844 });
    const r = await p.evaluate(() => {
      const rs = [...document.querySelectorAll('#start input[name=breed]')];
      return { n: rs.length, vals: rs.map(x => x.value), vis: rs.every(x => { const q = x.parentElement.getBoundingClientRect(); return q.width > 0 && q.height > 0 && q.left >= 0 && q.right <= 390 }), sw: document.documentElement.scrollWidth };
    });
    console.log(JSON.stringify(r));
    ok(r.n === 4 && r.vals.join() === 'golden,bichon,terrier,lantau' && r.vis, 'phone start card shows 4 breed radios inside the screen');
    ok(r.sw <= 390, 'phone start card: scrollWidth ' + r.sw + ' <= 390');
    await p.evaluate(() => { const c = document.querySelector('#start .startCard'); const r = document.querySelector('#start .breeds'); if (r) r.scrollIntoView({ block: 'center' }) });
    await p.screenshot({ path: OUT + '/b0_phone_start.png' }); await p.close();
  }

  // ---------------------------------------------------------------- each breed in play
  const CASES = [['hy', 'golden'], ['hy', 'bichon'], ['hy', 'terrier'], ['hy', 'lantau'], ['db', 'terrier'], ['db', 'lantau']];
  for (const [lv, br] of CASES) {
    const tag = lv + '/' + br;
    const p = await open({ level: lv, breed: br });
    const pre = await p.evaluate(() => (document.querySelector('input[name=breed]:checked') || {}).value);
    ok(pre === br, tag + ': radio pre-checked from __BOOT (' + pre + ')');
    // click Start inside the page so the start toasts can be read before the queue moves on
    const tq = await p.evaluate(() => { document.getElementById('startBtn').click(); return (window.__g && __g.toastQ || []).slice() });
    ok(await w(p, () => window.__g && __g.S && __g.S.started && __g.D), tag + ': started');
    const hello = tq.join(' | ');
    ok(br === 'terrier' ? hello.includes('Border terriers were bred to dig') : br === 'lantau' ? hello.includes('free Lantau street dog (唐狗)') : !/Border terriers|free Lantau/.test(hello), tag + ': breed hello toast (' + tq.length + ' start toasts)');
    const st = await p.evaluate(() => { let n = 0; __g.D.root.traverse(m => { if (m.isMesh) n++ }); return { lv: __g.LEVEL, D: __g.D.breed, S: __g.S.breed, radio: (document.querySelector('input[name=breed]:checked') || {}).value, meshes: n, pitch: __g.D.pitch, mouthZ: __g.D.mouthZ, prick: __g.D.prick, k: __g.D.k } });
    console.log(tag, JSON.stringify(st));
    ok(st.lv === lv && st.D === br && st.S === br && st.radio === br, tag + ': D.breed, S.breed and checked radio all ' + br);
    if (br === 'golden') ok(st.meshes === 54, tag + ': golden mesh count 54 (same as before), got ' + st.meshes);
    if (br === 'bichon') ok(st.meshes === 56, tag + ': bichon mesh count 56 (same as before), got ' + st.meshes);
    if (br === 'terrier') ok(st.pitch === 1.45 && st.mouthZ === 0.21, tag + ': terrier pitch 1.45, mouthZ 0.21');
    if (br === 'lantau') ok(st.pitch === 0.82 && st.prick === true, tag + ': lantau pitch 0.82, prick ears');

    // run for 3 game seconds with W + Shift
    const t0 = await p.evaluate(() => { const G = __g; G.S.hour = 13; G.keys.w = true; G.keys.shift = true; return { t: G.S.t, x: G.dog.x, z: G.dog.z } });
    ok(await w(p, t => __g.S.t > t + 3, t0.t, 180000), tag + ': 3 s of running');
    const fin = await p.evaluate(() => {
      const G = __g, D = G.D, a = []; D.legs.forEach(L => a.push(L.up.rotation.x, L.kn.rotation.x)); a.push(D.hip.position.y, D.root.position.x, D.root.position.y, D.root.position.z);
      G.keys.w = false; G.keys.shift = false; return { finite: a.every(Number.isFinite), x: G.dog.x, z: G.dog.z, vals: a.map(v => +v.toFixed(3)) };
    });
    const dist = Math.hypot(fin.x - t0.x, fin.z - t0.z);
    ok(fin.finite, tag + ': legs up/kn rotation.x, hip.position.y and root.position finite after running');
    ok(dist > 1, tag + ': dog moved ' + dist.toFixed(1) + ' m');

    // side-view screenshot for the looks
    await w(p, () => __g.dog.speed < 0.05, null, 60000);
    await p.evaluate(() => { // stand in the open (no building within 7 m), side on to the camera
      const G = __g, dog = G.dog, open = (x, z) => { if (G.surface(x, z) === 'water') return false; for (let r = 0; r <= 7; r += 1) for (let a = 0; a < 6.28; a += 0.5) if (G.bldAt(x + Math.sin(a) * r, z + Math.cos(a) * r)) return false; return true };
      let spot = null; for (let r = 0; r < 120 && !spot; r += 3) for (let a = 0; a < 6.28 && !spot; a += 0.3) { const x = dog.x + Math.sin(a) * r, z = dog.z + Math.cos(a) * r; if (open(x, z)) spot = [x, z] }
      if (spot) { dog.x = spot[0]; dog.z = spot[1]; dog.y = G.groundAt(dog.x, dog.z) } });
    await p.evaluate(() => { const G = __g; document.getElementById('hud').style.display = 'none'; G.cam.yaw = G.dog.heading + Math.PI / 2; G.cam.dist = G.D.k < 0.8 ? 2.6 : 3.4; G.cam.pitch = 0.12; G.cam.lastDrag = 1e9; G.S.hour = 13 });
    const t1 = await p.evaluate(() => __g.S.t); await w(p, t => __g.S.t > t + 0.4, t1, 60000);
    await p.screenshot({ path: OUT + '/b_' + lv + '_' + br + '_side.png' });
    await p.evaluate(() => { document.getElementById('hud').style.display = '' });

    // perks and model options
    if (lv === 'hy' && (br === 'terrier' || br === 'golden')) {
      const d = await p.evaluate(() => {
        const G = __g, dog = G.dog; let spot = null;
        for (let r = 0; r < 60 && !spot; r += 1.5) for (let a = 0; a < 6.28 && !spot; a += 0.4) { const x = dog.x + Math.sin(a) * r, z = dog.z + Math.cos(a) * r; const s = G.surface(x, z); if (s === 'grass' || s === 'sand') spot = [x, z] }
        if (!spot) return { err: 'no grass' };
        dog.x = spot[0]; dog.z = spot[1]; dog.y = G.groundAt(dog.x, dog.z); dog.autoRun = 0; dog.action = null; dog.posture = 'stand'; dog.swimming = false;
        G.doDig(); const r = { action: dog.action, actionT: dog.actionT }; dog.action = null; dog.actionT = 0; return r;
      });
      console.log(tag, 'dig', JSON.stringify(d));
      ok(d.action === 'dig' && d.actionT === (br === 'terrier' ? 1.05 : 1.6), tag + ': doDig actionT ' + d.actionT);
    }
    if (lv === 'hy' && br === 'terrier') {
      const m = await p.evaluate(() => {
        const G = __g, out = {}; let threw = null;
        try { out.c = G.makeDog('constructor').breed; out.p = G.makeDog('__proto__').breed; out.h = G.makeDog('hasOwnProperty').breed } catch (e) { threw = String(e) }
        out.threw = threw; const T = G.makeDog('terrier'); out.leash = T.leashPt.parent === T.neck;
        const cnt = D => { let n = 0; D.root.traverse(q => { if (q.isMesh) n++ }); return n };
        const a = G.makeDog('terrier', { lite: true, mc: true }), b2 = G.makeDog('terrier', { lite: true, mc: true });
        let shadow = false; a.root.traverse(q => { if (q.isMesh && q.castShadow) shadow = true });
        out.liteShadow = shadow; out.liteN = cnt(a); out.fullN = cnt(T); out.shareFur = a.mats.fur === b2.mats.fur && a.mats.furL === b2.mats.furL; out.sharedFlag = !!a.mats.fur.userData.shared;
        let sameMats = true; const ma = [], mb = []; a.root.traverse(q => { if (q.isMesh) ma.push(q.material) }); b2.root.traverse(q => { if (q.isMesh) mb.push(q.material) }); ma.forEach((m, i) => { if (m !== mb[i]) sameMats = false }); out.allShared = sameMats;
        const nc = G.makeDog('terrier', { lite: true, mc: true, collar: 0 }); out.noCollarN = cnt(nc);
        out.ids = G.BREED_IDS.join(); out.info = G.breedInfo('lantau').sh; out.badInfo = G.breedInfo('constructor').name;
        return out;
      });
      console.log(tag, 'model', JSON.stringify(m));
      ok(!m.threw && m.c === 'golden' && m.p === 'golden' && m.h === 'golden', 'makeDog(constructor/__proto__/hasOwnProperty) falls back to golden without throwing');
      ok(m.leash, 'makeDog(terrier).leashPt.parent === neck');
      ok(!m.liteShadow && m.liteN < m.fullN, 'lite terrier: no shadow casters, ' + m.liteN + ' < ' + m.fullN + ' meshes');
      ok(m.shareFur && m.sharedFlag && m.allShared, 'two lite+mc terriers share every material (fur, furL, ...)');
      ok(m.noCollarN === m.liteN - 2, 'collar:0 drops the collar and tag');
      ok(m.ids === 'golden,bichon,terrier,lantau' && m.info === '唐狗' && m.badInfo === 'golden retriever', 'BREED_IDS and breedInfo validation');
    }
    if (br === 'lantau' && lv === 'hy') {
      const s = await p.evaluate(() => { const G = __g; return { snap: G.snapshot().breed, bark: G.breedInfo().bark, hello: [...document.querySelectorAll('.toast,#toast')].map(e => e.textContent).join('|') } });
      ok(s.snap === 'lantau', 'snapshot().breed === lantau after a lantau start');
      ok(s.bark === 'Wuff! Wuff!', 'lantau bark line');
    }
    if (lv === 'db') ok(st.lv === 'db' && st.D === br, tag + ': __BOOT builds a ' + br + ' in Discovery Bay');
    await p.close();
  }
  console.log(errs.join('\n') || 'NO_ERRORS');
  if (errs.length || fails) process.exitCode = 1;
  await b.close();
})();
