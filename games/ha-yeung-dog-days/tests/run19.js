const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1100,height:650}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);console.log('EARLY',errs.join(' | ')||'none');
  await p.evaluate(()=>{__g.S.hour=12;const F=__g.FISH,d=__g.dog;d.x=F.x-F.dx*3+F.dz*3;d.z=F.z-F.dz*3-F.dx*3;d.heading=Math.atan2(F.dx,F.dz);__g.cam.yaw=Math.atan2(F.dx,F.dz)+0.9;__g.cam.dist=7;__g.cam.pitch=0.25;__g.fisher.catchT=1.5});
  await p.waitForTimeout(2500);await p.screenshot({path:'shot17a.png'});await p.waitForTimeout(2500);await p.screenshot({path:'shot17b.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
