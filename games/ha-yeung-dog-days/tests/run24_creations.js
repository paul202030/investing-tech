const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const SHIM = `<script>(()=>{const spec={name:'Bouncy Mango',zh:'芒果',label:'a giant bouncing mango',line:'A mango bigger than my head!',move:'bounce',effect:'giant',parts:[{s:'sphere',c:'#f2a33a',x:0,y:0.45,z:0,sx:0.8,sy:0.9,sz:0.8},{s:'cyl',c:'#5e4128',x:0,y:0.95,z:0,sx:0.06,sy:0.2,sz:0.06},{s:'sphere',c:'#4f8a3a',x:0.12,y:1.0,z:0,sx:0.25,sy:0.06,sz:0.14}]};
 const db={docs:[],fn:null,collection(){const q={orderBy(){return q},limit(){return q},onSnapshot(fn){db.fn=fn;fn({docChanges:()=>[]});return()=>{}},doc(id){return {set:async d=>{db.docs.push([id,d])}}}};return q}};
 const sample={json:async()=>JSON.parse(JSON.stringify(spec))};window.__db=db;window.claude={use:async n=>n==='db'?db:n==='sample'?sample:null}})()</script>`;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 };
  await p.setContent(SHIM + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn'); await p.waitForTimeout(1500);
  await p.evaluate(() => { const d = __g.dog; d.x += 0; __g.cam.dist = 7 });
  await p.keyboard.press('n'); await p.waitForTimeout(400); ok(await p.isVisible('#createBox'), 'N opens the Create box');
  await p.fill('#createIdea', 'a giant bouncing mango'); await p.keyboard.press('Enter');
  await p.waitForFunction(() => __g.GEN.items.length === 1 && window.__db.docs.length === 1, null, { timeout: 30000 }).catch(() => {});
  ok(await p.evaluate(() => __g.GEN.items.length === 1 && window.__db.docs.length === 1 && __g.S.todos.create), 'creation spawned, saved to db, to-do done: ' + await p.textContent('#createMsg'));
  await p.waitForTimeout(2500); await p.screenshot({ path: process.env.OUT + '/g1.png' });
  // another player's creation arrives
  await p.evaluate(() => { const [id, d] = window.__db.docs[0]; const d2 = JSON.parse(JSON.stringify(d)); d2.by = 'Coco'; d2.x += 3; d2.spec.name = 'Coco Mango'; window.__db.fn({ docChanges: () => [{ type: 'added', doc: { id: 'other1', data: () => d2 } }] }) });
  ok(await p.evaluate(() => __g.GEN.items.length === 2), 'other player\'s creation appears');
  // junk from the db is ignored
  await p.evaluate(() => window.__db.fn({ docChanges: () => [{ type: 'added', doc: { id: 'bad', data: () => ({ lv: 'hy', x: 0, z: 0, spec: { parts: [{ s: 'evil', c: 'red' }] } }) } }] }));
  ok(await p.evaluate(() => __g.GEN.items.length === 2), 'invalid creation ignored');
  // pick it up: giant effect
  await p.evaluate(() => { const it = __g.GEN.items[0]; __g.dog.x = it.x; __g.dog.z = it.z });
  await p.waitForFunction(() => __g.D.root.scale.x > 1.6, null, { timeout: 60000 }).catch(() => {});
  ok(await p.evaluate(() => __g.D.root.scale.x > 1.6 && __g.dog.item && __g.dog.item.T.gen), 'picked up, dog turned giant');
  await p.waitForTimeout(1500); await p.screenshot({ path: process.env.OUT + '/g2.png' });
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close()
})();
