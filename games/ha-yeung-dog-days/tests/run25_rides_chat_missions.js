const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const SHIM = `<script>(()=>{const plane={name:'Little Red Plane',label:'a little red plane',ride:'fly',seat:{x:0,y:0.9,z:0},parts:[{s:'box',c:'#c8322b',x:0,y:0.6,z:0,sx:3,sy:0.6,sz:0.7},{s:'box',c:'#f2f0e8',x:0.2,y:0.7,z:0,sx:0.8,sy:0.08,sz:3.6},{s:'cone',c:'#222222',x:1.6,y:0.6,z:0,sx:0.4,sy:0.4,sz:0.4,rz:-90}]};
 const mission={title:'Granny needs company',brief:'Go say hi to Granny Chan, quick!',time:120,reward:300,steps:[{type:'goto',to:'Granny Chan',text:'Visit Granny Chan'},{type:'bark',at:'Granny Chan',text:'Bark hello'}],win:'Good dog!',lose:'Aiya'};
 const db={docs:[],fn:null,collection(){const q={orderBy(){return q},limit(){return q},onSnapshot(fn){db.fn=fn;fn({docChanges:()=>[]});return()=>{}},doc(id){return {set:async d=>{db.docs.push([id,d])}}}};return q}};
 const sample={json:async p=>p.includes('ONE mission')?JSON.parse(JSON.stringify(mission)):p.includes('talking to you')?{reply:'Aiya, so fluffy! Have you eaten?',action:'pat'}:JSON.parse(JSON.stringify(plane))};
 window.__db=db;window.claude={use:async n=>n==='db'?db:n==='sample'?sample:null}})()</script>`;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f); const OUT = process.env.OUT;
  await p.setContent(SHIM + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.check('input[value=bichon]'); await p.click('#startBtn'); await p.waitForTimeout(1500);
  ok(await g(() => __g.D.breed === 'bichon' && __g.S.breed === 'bichon'), 'bichon frise chosen');
  // chat with Granny
  await g(() => { const q = __g.granny.g.position; __g.dog.x = q.x + 2; __g.dog.z = q.z; __g.dog.heading = -Math.PI / 2; __g.cam.yaw = -Math.PI / 2; __g.cam.dist = 5 });
  await p.waitForFunction(() => { const a = __g.ctxAction(); return a && a.l === 'Chat' }, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => { const a = __g.ctxAction(); return a && a.l === 'Chat' }), 'Chat offered next to Granny Chan');
  await p.screenshot({ path: OUT + '/c0_bichon.png' });
  await p.keyboard.press('x'); await p.waitForTimeout(300); await p.fill('#chatIn', 'Woof! Any snacks?'); await p.keyboard.press('Enter');
  await p.waitForFunction(() => document.querySelectorAll('#chatLog .them').length === 1, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => document.querySelectorAll('#chatLog .them').length === 1 && __g.S.todos.chat), 'Granny replied: ' + await p.evaluate(() => (document.querySelector('#chatLog .them') || {}).textContent));
  await p.screenshot({ path: OUT + '/c1_chat.png' }); await p.keyboard.press('Escape');
  // mission from Auntie
  await g(() => { const q = __g.auntie.g.position; __g.dog.x = q.x + 1.8; __g.dog.z = q.z });
  await p.waitForFunction(() => { const a = __g.ctxAction(); return a && a.l === 'Mission' }, null, { timeout: 30000 }).catch(() => {});
  await p.keyboard.press('x'); await p.waitForFunction(() => !!__g.MIS.cur, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => !!__g.MIS.cur && __g.MIS.cur.steps.length === 2), 'Auntie gave a 2-step mission');
  await p.waitForTimeout(1500); await p.screenshot({ path: OUT + '/c2_mission.png' });
  await g(() => { const q = __g.granny.g.position; __g.dog.x = q.x + 2; __g.dog.z = q.z });
  await p.waitForFunction(() => __g.MIS.cur && __g.MIS.cur.i === 1, null, { timeout: 30000 }).catch(() => {});
  await p.keyboard.press(' '); await p.waitForFunction(() => !__g.MIS.cur, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => !__g.MIS.cur && __g.S.todos.mission), 'mission completed');
  // create a plane and fly it
  await g(() => { __g.dog.x += 6 }); await p.waitForTimeout(500); await p.keyboard.press('n'); await p.fill('#createIdea', 'a little red plane I can fly'); await p.keyboard.press('Enter');
  await p.waitForFunction(() => __g.rides.length === 1, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => __g.rides.length === 1 && __g.rides[0].fly), 'plane created as a flying ride');
  await p.waitForTimeout(1800); await g(() => { const k = __g.rides[0]; __g.dog.x = k.x + 2; __g.dog.z = k.z });
  await p.waitForFunction(() => { const a = __g.ctxAction(); return a && a.l === 'Hop on' }, null, { timeout: 30000 }).catch(() => {});
  await p.keyboard.press('x'); await p.waitForTimeout(300); await p.keyboard.down('w');
  await p.waitForFunction(() => __g.dog.cart && __g.dog.cart.alt > 8, null, { timeout: 120000 }).catch(() => {});
  ok(await g(() => __g.dog.cart && __g.dog.cart.alt > 8), 'flying: ' + await g(() => __g.dog.cart ? Math.round(__g.dog.cart.alt) + ' m up' : 'not in plane'));
  await p.screenshot({ path: OUT + '/c3_fly.png' }); await p.keyboard.up('w');
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close()
})();
