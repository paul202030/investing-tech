const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);
  const g=()=>p.evaluate(()=>({pic:[__g.pic.state,__g.pic.inRange],item:__g.dog.item&&__g.dog.item.type,action:__g.dog.action,todos:Object.keys(__g.S.todos)}));
  // dim sum moment
  await p.evaluate(()=>{__g.dog.heading+=1.2;__g.serve()});await p.waitForTimeout(1300);await p.screenshot({path:'shot12a.png'});await p.waitForTimeout(1800);await p.screenshot({path:'shot12b.png'});
  await p.waitForTimeout(9000);console.log('after feast',JSON.stringify(await g()));
  // picnic
  await p.evaluate(()=>{__g.S.hour=11;const P=__g.pic,d=__g.dog;d.action=null;d.x=P.x+2.4;d.z=P.z+0.8;d.heading=Math.atan2(P.x-d.x,P.z-d.z);__g.cam.yaw=d.heading+0.7;__g.cam.dist=6;__g.cam.pitch=0.3});
  await p.waitForTimeout(2500);console.log('at picnic',JSON.stringify(await g()),'btn',await p.evaluate(()=>!document.getElementById('aSteal').hidden));
  await p.screenshot({path:'shot12c.png'});
  await p.keyboard.press('t');await p.waitForTimeout(500);console.log('stole',JSON.stringify(await g()));
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
