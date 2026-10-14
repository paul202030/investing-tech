const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');await p.waitForTimeout(800);
  await p.evaluate(()=>{__g.S.hour=12;const B=__g.bbq,d=__g.dog;d.x=B.gx+1.6;d.z=B.gz+1.6;d.heading=Math.atan2(B.gx-d.x,B.gz-d.z);__g.cam.yaw=d.heading+1.0;__g.cam.dist=5.5;__g.cam.pitch=0.3});
  await p.waitForTimeout(1200);await p.screenshot({path:'shot14a.png'});
  await p.keyboard.press('t');await p.waitForTimeout(250);
  console.log(await p.evaluate(()=>{const t=document.querySelector('.arcTitle');const r=t.getBoundingClientRect();return [t.textContent,r.x,r.y,r.width,r.height,getComputedStyle(t).fontSize,getComputedStyle(document.getElementById('arcade')).zIndex,getComputedStyle(document.getElementById('arcade')).display,getComputedStyle(document.getElementById('arcade')).visibility]}));console.log(await p.evaluate(()=>{const e=document.getElementById('arcade');const b=e.querySelector('.arcBox');const cs=getComputedStyle(b);return [e.className,cs.opacity,cs.transform,cs.animationName,e.getBoundingClientRect().width]}));
  await p.addStyleTag({content:'#arcade .arcBox{animation:none!important;transform:none!important;opacity:1!important}'});await p.waitForTimeout(100);await p.screenshot({path:'shot14b.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
