const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);
  const g=()=>p.evaluate(()=>({bbq:__g.bbq.state,item:__g.dog.item&&[__g.dog.item.type,__g.dog.item.state],carry:__g.bbq.carry&&__g.bbq.carry.state,action:__g.dog.action,todos:Object.keys(__g.S.todos),bones:__g.items.filter(i=>i.type==='bone').length}));
  await p.evaluate(()=>{__g.S.hour=12;const B=__g.bbq,d=__g.dog;d.x=B.gx+1.6;d.z=B.gz+1.6;d.heading=Math.atan2(B.gx-d.x,B.gz-d.z);__g.cam.yaw=d.heading+1.0;__g.cam.dist=5.5;__g.cam.pitch=0.3});
  await p.waitForTimeout(1500);await p.screenshot({path:'shot13a.png'});
  await p.keyboard.press('t');await p.waitForTimeout(900);await p.screenshot({path:'shot13b.png'});await p.waitForTimeout(1600);await p.screenshot({path:'shot13d.png'});console.log('grabbed',JSON.stringify(await g()));
  // stand still -> uncle catches us
  await p.waitForTimeout(5000);console.log('caught?',JSON.stringify(await g()));await p.screenshot({path:'shot13c.png'});
  // second attempt: escape by teleporting far away
  await p.evaluate(()=>{const B=__g.bbq;B.cool=0;B.state='grill';const U=B.uncle.g.position;U.x=B.ux;U.z=B.uz;if(B.carry){B.carry=null}});await p.waitForTimeout(500);
  await p.evaluate(()=>{const B=__g.bbq,d=__g.dog;d.x=B.gx+1.6;d.z=B.gz+1.6;});await p.waitForTimeout(800);await p.keyboard.press('t');await p.waitForTimeout(1500);
  await p.evaluate(()=>{const d=__g.dog;d.x+=30;});await p.waitForTimeout(6000);console.log('escaped',JSON.stringify(await g()));
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
