const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(500);
  const g=()=>p.evaluate(()=>({bbq:[__g.bbq.gx.toFixed(0),__g.bbq.gz.toFixed(0),__g.bbq.state,__g.bbq.inRange],dog:[__g.dog.x.toFixed(1),__g.dog.z.toFixed(1),__g.dog.item&&__g.dog.item.type,__g.dog.action],hour:__g.S.hour.toFixed(2)}));
  await p.evaluate(()=>{__g.S.hour=12;const B=__g.bbq,d=__g.dog;d.x=B.gx+2.0;d.z=B.gz-1.5;d.heading=Math.atan2(B.gx-d.x,B.gz-d.z);__g.cam.yaw=d.heading+0.5;__g.cam.dist=7;__g.cam.pitch=0.35});
  await p.waitForTimeout(1500);console.log('near bbq',JSON.stringify(await g()),'steal btn shown',await p.evaluate(()=>!document.getElementById('aSteal').hidden));
  await p.screenshot({path:'shot8a.png'});
  await p.keyboard.press('t');await p.waitForTimeout(300);console.log('after steal',JSON.stringify(await g()));
  // run away (running toggled on automatically)
  await p.evaluate(()=>{const B=__g.bbq,d=__g.dog;__g.cam.yaw=Math.atan2(d.x-B.gx,d.z-B.gz)});
  await p.keyboard.down('w');await p.waitForTimeout(2500);await p.screenshot({path:'shot8b.png'});await p.waitForTimeout(6000);await p.keyboard.up('w');
  console.log('after running',JSON.stringify(await g()),'speed',await p.evaluate(()=>__g.dog.speed.toFixed(1)));
  await p.waitForTimeout(3500);console.log('later',JSON.stringify(await g()));
  // big map travel
  await p.click('#map');await p.waitForTimeout(400);await p.screenshot({path:'shot8c.png'});
  const box=await p.locator('#bigMapCv').boundingBox();await p.mouse.click(box.x+box.width*0.73,box.y+box.height*0.18);await p.waitForTimeout(800);
  console.log('after travel',JSON.stringify(await g()),'map hidden',await p.evaluate(()=>document.getElementById('bigMap').hidden));
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
