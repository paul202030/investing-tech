const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1100,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:90000});await p.click('#startBtn');
  const hd=+process.argv[2]||61,PX=+process.argv[3],PZ=+process.argv[4];
  await p.evaluate(([hd,PX,PZ])=>{__g.S.hour=13;const d=__g.dog;d.x=PX;d.z=PZ;const a=Math.atan2(Math.sin(hd*Math.PI/180),-Math.cos(hd*Math.PI/180));d.heading=a;__g.cam.yaw=a;__g.cam.dist=6;__g.cam.pitch=0.16},[hd,PX,PZ]);
  await p.waitForTimeout(3500);await p.screenshot({path:'shot11.png'});
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
