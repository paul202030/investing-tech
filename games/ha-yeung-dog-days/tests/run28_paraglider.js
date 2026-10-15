const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const SHIM = `<script>(()=>{const plane={name:'Red Plane',label:'a red plane',ride:'fly',seat:{x:0,y:0.9,z:0},parts:[{s:'box',c:'#c8322b',x:0,y:0.6,z:0,sx:3,sy:0.6,sz:0.7},{s:'box',c:'#f2f0e8',x:0.2,y:0.7,z:0,sx:0.8,sy:0.08,sz:3.6}]};
 const db={collection(){const q={orderBy(){return q},limit(){return q},onSnapshot(fn){return()=>{}},doc(){return {set:async()=>{},update:async()=>{}}}};return q},doc(){return {get:async()=>({exists:false}),set:async()=>{}}}};
 window.claude={use:async n=>n==='db'?db:n==='sample'?{json:async p=>p.includes('content reviewer')?{ok:true}:JSON.parse(JSON.stringify(plane))}:null}})()</script>`;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f); const w = (f, t) => p.waitForFunction(f, null, { timeout: t || 60000 }).then(() => true, () => false);
  await p.setContent(SHIM + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn'); await p.waitForTimeout(1200);
  await p.keyboard.press('n'); await p.fill('#createIdea', 'a red plane'); await p.keyboard.press('Enter');
  ok(await w(() => __g.rides.length === 1), 'plane created'); await p.waitForTimeout(1600);
  await g(() => { const k = __g.rides[0]; __g.dog.x = k.x + 2; __g.dog.z = k.z });
  await w(() => { const a = __g.ctxAction(); return a && a.l === 'Hop on' }); await p.keyboard.press('x');
  await g(() => { const k = __g.dog.cart; k.alt = 30; k.v = 20 });
  ok(await w(() => { const a = __g.ctxAction(); return a && a.l === 'Jump!' }), 'Jump! offered while flying');
  await p.keyboard.press('x'); ok(await w(() => !!__g.dog.para && !__g.dog.cart), 'jumped out: free fall');
  await p.waitForTimeout(600); await p.keyboard.press(' '); ok(await w(() => __g.dog.para && __g.dog.para.open), 'paraglider opened with Space');
  await p.waitForTimeout(1500); await p.screenshot({ path: process.env.OUT + '/para.png' });
  ok(await w(() => !__g.dog.para, 240000), 'landed'); ok(await g(() => !!__g.S.todos.para), 'NICE LANDING to-do done');
  ok(await w(() => !__g.rides[0].drop, 120000), 'empty plane glided down and parked');
  console.log(errs.join('\n') || 'NO_ERRORS'); await b.close()
})();
