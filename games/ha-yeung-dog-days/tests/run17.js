const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1100,height:650}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);
  await p.evaluate(()=>{const d=__g.dog;d.x=-14;d.z=-14;d.heading=Math.atan2(-1,-0.3);__g.cam.yaw=d.heading;__g.cam.dist=6;__g.cam.pitch=0.25});
  await p.waitForTimeout(2500);await p.screenshot({path:'shot15a.png'});
  await p.evaluate(()=>{const d=__g.dog,P=__g.PL;d.x=P.stop[0]+22;d.z=P.stop[1]+2;d.heading=Math.atan2(P.stop[0]-d.x,P.stop[1]-d.z)-0.3;__g.cam.yaw=d.heading;__g.cam.dist=7;__g.cam.pitch=0.2});
  await p.waitForTimeout(2500);await p.screenshot({path:'shot15c.png'});
  await p.evaluate(()=>{__g.S.hour=12;const A=__g.auntie.g.position,d=__g.dog;d.x=A.x+1.6;d.z=A.z+0.6;d.heading=Math.atan2(A.x-d.x,A.z-d.z)+1.6;__g.cam.yaw=d.heading+0.8;__g.cam.dist=5;});
  await p.waitForTimeout(600);await p.keyboard.press('c');
  const st=[];for(let i=0;i<8;i++){await p.waitForTimeout(400);st.push(await p.evaluate(()=>[__g.dog.posture,__g.dog.action,(__g.dog.sitT||0).toFixed(1)].join('/')))}
  console.log(st.join(' | '));await p.waitForTimeout(1500);await p.screenshot({path:'shot15b.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
