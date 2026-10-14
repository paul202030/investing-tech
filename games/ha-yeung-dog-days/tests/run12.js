const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(1500);
  // sit the dog at the bus stop and bring the minibus in close
  await p.evaluate(()=>{const d=__g.dog,q=__g.cwAt(445);d.x=q.x+q.fz*6.6+q.fx*30;d.z=q.z-q.fx*6.6+q.fz*30;d.posture='sit';d.heading=Math.atan2(-q.fz,q.fx)+Math.PI;
    __g.cam.yaw=Math.atan2(-q.fx,-q.fz);__g.cam.dist=9;__g.cam.pitch=0.25;const m=__g.mini;m.wait=0;});
  await p.waitForTimeout(400);await p.evaluate(()=>{const m=__g.mini;m.s=462;});
  for(let i=0;i<25;i++){await p.waitForTimeout(1000);const st=await p.evaluate(()=>[__g.mini.state,__g.mini.s.toFixed(0),__g.mini.v.toFixed(1),Object.keys(__g.S.todos).join(',')]);console.log(JSON.stringify(st));if(st[0]==='dwell'){await p.waitForTimeout(600);await p.screenshot({path:'shot10.png'});break}}
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
