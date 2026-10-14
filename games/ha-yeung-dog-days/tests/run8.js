const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1000,height:700}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:60000});await p.click('#startBtn');await p.waitForTimeout(1500);
  await p.evaluate(()=>{__g.dog.heading+=Math.PI*0.6;__g.serve()});await p.waitForTimeout(1200);
  // swing camera to the dog's side for a profile view
  await p.mouse.move(500,350);await p.mouse.down();await p.mouse.move(700,330,{steps:8});await p.mouse.up();await p.waitForTimeout(700);
  await p.screenshot({path:'shot6.png'});
  await p.waitForTimeout(8000);console.log('hunger',await p.evaluate(()=>document.getElementById('bHunger').style.width),'action',await p.evaluate(()=>__g.dog.action));
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
