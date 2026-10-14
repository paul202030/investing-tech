const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1100,height:650}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);
  // north end of Clear Water Bay Road with the taxi parked beside the dog
  await p.evaluate(()=>{const q=__g.cwAt(60),d=__g.dog;d.x=q.x;d.z=q.z;d.heading=Math.atan2(q.fx,q.fz);__g.cam.yaw=d.heading+0.4;__g.cam.dist=7;__g.cam.pitch=0.22;const t=__g.taxi;t.wait=0});
  await p.waitForTimeout(400);await p.evaluate(()=>{const t=__g.taxi;t.s=78;t.v=0});await p.waitForTimeout(2500);await p.screenshot({path:'shot16a.png'});
  await p.evaluate(()=>{const q=__g.cwAt(300),d=__g.dog;d.x=q.x+q.fz*1.5;d.z=q.z-q.fx*1.5;d.heading=Math.atan2(q.fx,q.fz);__g.cam.yaw=d.heading;__g.cam.dist=8;__g.cam.pitch=0.25});
  await p.waitForTimeout(2500);await p.screenshot({path:'shot16b.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
