const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(1500);console.log('EARLY',errs.join(' | ')||'none',await p.evaluate(()=>Object.keys(window.__g||{})));
  const g=()=>p.evaluate(()=>({happy:__g.S.happy.toFixed(0),pats:__g.S.patsDay||0,todos:Object.keys(__g.S.todos),item:__g.dog.item&&__g.dog.item.type,action:__g.dog.action,roll:(__g.dog.roll||0).toFixed(2)}));
  // 1) go to Granny, sit -> pat
  await p.evaluate(()=>{const G=__g.GR,d=__g.dog;d.x=G.x+1.2;d.z=G.z+1.2;d.heading=Math.atan2(G.x-d.x,G.z-d.z);__g.cam.yaw=d.heading-0.9;__g.cam.dist=5;__g.cam.pitch=0.3});
  await p.waitForTimeout(600);await p.keyboard.press('c');await p.waitForTimeout(1200);console.log('sit by granny',JSON.stringify(await g()));
  await p.screenshot({path:'shot9a.png'});
  // 2) lie -> belly rub (after pat cooldown would block; test with BBQ guest instead)
  await p.evaluate(()=>{__g.S.hour=12;const B=__g.bbq,d=__g.dog;d.posture='stand';const q=B.guests[0].g.position;d.x=q.x+1.3;d.z=q.z+0.6;d.heading=Math.atan2(q.x-d.x,q.z-d.z);__g.cam.yaw=d.heading+1.3;__g.cam.dist=4.5;});await p.waitForTimeout(300);
  await p.keyboard.press('c');await p.keyboard.press('c');await p.waitForTimeout(1500);console.log('lie near guests',JSON.stringify(await g()));
  await p.screenshot({path:'shot9b.png'});
  // 3) fetch slipper and return it
  await p.evaluate(()=>{const s=__g.slip,d=__g.dog;d.posture='stand';d.bellyT=0;d.x=s.x-0.3;d.z=s.z});await p.waitForTimeout(1000);console.log('at slipper',JSON.stringify(await g()));
  await p.evaluate(()=>{const G=__g.GR,d=__g.dog;d.x=G.x+1.5;d.z=G.z+1.0});await p.waitForTimeout(2500);console.log('returned slipper',JSON.stringify(await g()));
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
