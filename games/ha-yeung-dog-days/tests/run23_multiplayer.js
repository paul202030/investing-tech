const { chromium } = require(process.env.TLIB + '/node_modules/playwright'); const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 650 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.stack || e.message)); p.on('console', m => { if (m.type() === 'error' && !m.text().includes('ERR_FAILED')) errs.push(m.text()) });
  await p.route('**/*', r => { const u = r.request().url(); if (u.includes('three.min.js')) return r.fulfill({ body: fs.readFileSync(process.env.TLIB + '/node_modules/three/build/three.min.js'), contentType: 'application/javascript' }); return r.abort() });
  // fake room: records our presence, lets the test play a friend
  await p.setContent('<script>(()=>{const room={sent:null,h:null,presence(x){room.sent=x;return Promise.resolve()},onPeers(fn){room.h=fn;return()=>{room.h=null}}};window.__room=room;window.claude={use:async n=>n==="room"?room:null}})()</script>' + fs.readFileSync(process.env.PERF, 'utf8'));
  await p.waitForSelector('#startBtn:not([disabled])', { timeout: 120000 }); await p.fill('#dogName', 'Biscuit'); await p.click('#startBtn');
  await p.waitForFunction(() => window.__room.sent && window.__room.h, null, { timeout: 60000 });
  await p.waitForTimeout(2000); await p.screenshot({ path: process.env.OUT + '/mp0.png' }); console.log(await p.evaluate(() => { const e = document.elementFromPoint(550, 500); return e ? e.tagName + '#' + e.id + '.' + e.className : 'none' }));
  const sent = await p.evaluate(() => window.__room.sent); console.log('presence sent', JSON.stringify(sent));
  await p.evaluate(() => { const d = __g.dog; const friend = (s, dx, b) => ({ peer: 'f1', isMe: false, presence: { lv: 'hy', x: d.x + dx, z: d.z + dx, y: d.y, h: 1, s, n: 'Coco', b } });
    const me = { peer: 'me', isMe: true, presence: window.__room.sent }; const f = friend('stand', 2, 0); window.__room.h({ peers: [me, f], joined: [f], left: [], updated: [] }); window.__fr = friend; d.heading = Math.atan2(2, 2); __g.cam.yaw = d.heading; __g.cam.dist = 7; __g.cam.pitch = 0.35; __g.cam.lastDrag = 1e9 });
  await p.waitForFunction(() => __g.MP.dogs.size === 1, null, { timeout: 30000 }); await p.waitForTimeout(3000); await p.screenshot({ path: process.env.OUT + '/mp1.png' });
  await p.evaluate(() => { const f = window.__fr('cart', 4, 1); window.__room.h({ peers: [{ peer: 'me', isMe: true, presence: {} }, f], joined: [], left: [], updated: [f] }) });
  await p.waitForTimeout(3000); await p.screenshot({ path: process.env.OUT + '/mp2.png' });
  await p.evaluate(() => window.__room.h({ peers: [{ peer: 'me', isMe: true, presence: {} }], joined: [], left: [], updated: [] }));
  await p.waitForFunction(() => __g.MP.dogs.size === 0, null, { timeout: 30000 }); console.log('PASS friend shown, rides cart, removed on leave');
  console.log(errs.join('\n') || 'NO_ERRORS'); await b.close()
})();
