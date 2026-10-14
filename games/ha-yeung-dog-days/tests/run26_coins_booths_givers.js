const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
const SHIM = `<script>(()=>{const booth={name:'Lion Wheel',label:'a lucky wheel booth',hello:'Spin to win!',booth:{game:'wheel',stake:20},parts:[{s:'box',c:'#c8322b',x:0,y:0.5,z:0,sx:2,sy:1,sz:1},{s:'cyl',c:'#f2c230',x:0,y:1.6,z:0,sx:1.2,sy:0.1,sz:1.2,rx:90}]};
 const giver={name:'Uncle Fong',label:'a retired uncle with a fan',hello:'Psst, dog. I have a job.',person:{shirt:'#ffffff',pants:'#333333',hair:'#999999',skin:'#d9ad85'},giver:{theme:'heist'},talk:'old storyteller',parts:[]};
 const mission={title:'Stick Heist',brief:'Bring me sticks, quick!',time:200,reward:400,steps:[{type:'collect',item:'stick',n:2,text:'Grab 2 sticks'},{type:'race',to:'Granny Chan',secs:60,text:'Run to Granny'}],win:'Nice',lose:'Aiya'};
 const db={docs:[],fn:null,collection(){const q={orderBy(){return q},limit(){return q},onSnapshot(fn){db.fn=fn;fn({docChanges:()=>[]});return()=>{}},doc(id){return {set:async d=>{db.docs.push([id,d])},update:async d=>{db.upd=d}}}};return q},doc(p){return {get:async()=>({exists:true,data:()=>({coins:250})}),set:async d=>{db.wallet=d}}}};
 let n=0;const sample={json:async p=>p.includes('content reviewer')?{ok:true}:p.includes('ONE mission')?JSON.parse(JSON.stringify(mission)):JSON.parse(JSON.stringify(n++?giver:booth))};
 window.__db=db;window.claude={use:async x=>x==='db'?db:x==='sample'?sample:x==='user'?{id:async()=>'u_test'}:null}})()</script>`;
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1 }; const g = f => p.evaluate(f);
  await p.setContent(SHIM + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.click('#startBtn');
  await p.waitForFunction(() => __g.S.coins === 250, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => __g.S.coins === 250), 'wallet loaded (250 coins)');
  await p.keyboard.press('n'); await p.fill('#createIdea', 'a lucky wheel booth'); await p.keyboard.press('Enter');
  await p.waitForFunction(() => __g.genFolk.length === 1, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => __g.genFolk.length === 1 && __g.genFolk[0].gen.booth && window.__db.docs[0][1].owner === 'u_test'), 'booth created with owner');
  await p.waitForTimeout(1800); await g(() => { const f = __g.genFolk[0]; __g.dog.x = f.x + 2.5; __g.dog.z = f.z });
  await p.waitForFunction(() => { const a = __g.ctxAction(); return a && a.l === 'Play' }, null, { timeout: 20000 }).catch(() => {});
  await p.keyboard.press('x'); await p.waitForTimeout(300); const c0 = await g(() => __g.S.coins);
  for (let i = 0; i < 5; i++) { await p.click('#boothBtns button'); await p.waitForTimeout(200) }
  const c1 = await g(() => __g.S.coins); ok(c1 !== c0 && await g(() => __g.S.todos.booth), 'played 5 spins: ' + c0 + ' → ' + c1 + ' coins; ' + await p.textContent('#boothRes'));
  await p.screenshot({ path: process.env.OUT + '/b1.png' }); await p.click('#boothClose');
  await g(() => { __g.dog.x += 8; __g.GEN.lastAt = 0 }); await p.waitForTimeout(400); await p.keyboard.press('n'); await p.fill('#createIdea', 'a retired uncle who gives heist missions'); await p.keyboard.press('Enter');
  await p.waitForFunction(() => __g.genFolk.length === 2, null, { timeout: 30000 }).catch(() => {});
  ok(await g(() => __g.genFolk.length === 2 && __g.genFolk[1].human && __g.genFolk[1].gen.giver), 'mission-giving person created');
  await p.waitForTimeout(1800); await g(() => { const f = __g.genFolk[1]; __g.dog.x = f.x + 2; __g.dog.z = f.z });
  await p.waitForFunction(() => { const a = __g.ctxAction(); return a && a.l === 'Mission' }, null, { timeout: 20000 }).catch(() => {});
  await p.keyboard.press('x'); await p.waitForFunction(() => !!__g.MIS.cur, null, { timeout: 20000 }).catch(() => {});
  ok(await g(() => __g.MIS.cur && __g.MIS.cur.steps.length === 2 && __g.MIS.cur.steps[1].type === 'race'), 'giver handed out a 2-step mission (collect + race)');
  await p.waitForTimeout(1200); await p.screenshot({ path: process.env.OUT + '/b2.png' });
  console.log(errs.join('\n') || 'NO_ERRORS'); if (errs.length) process.exitCode = 1; await b.close()
})();
