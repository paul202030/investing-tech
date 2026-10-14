const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:430,height:760},deviceScaleFactor:2});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');
  // stand on the pavement of Clear Water Bay Road near the bus stop, looking along the road
  await p.evaluate(()=>{const q=__g.cwAt(380),d=__g.dog;d.x=q.x+q.fz*5.3;d.z=q.z-q.fx*5.3;d.heading=Math.atan2(q.fx,q.fz);__g.cam.yaw=d.heading-0.5;__g.cam.dist=6;__g.cam.pitch=0.22});
  await p.waitForTimeout(3000);await p.screenshot({path:'shot7.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
