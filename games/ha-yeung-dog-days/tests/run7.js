const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']});
  const p=await b.newPage({viewport:{width:1000,height:640}});const errs=[];p.on('pageerror',e=>errs.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push(m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForSelector('#startBtn:not([disabled])',{timeout:60000});await p.click('#startBtn');await p.waitForTimeout(800);
  // walk the dog onto the nearest item, check pickup, then carry it to the bed
  const st=await p.evaluate(()=>{const d=__g.dog,its=__g.items.filter(i=>i.state==='ground');its.sort((a,b)=>Math.hypot(a.x-d.x,a.z-d.z)-Math.hypot(b.x-d.x,b.z-d.z));const it=its[0];d.x=it.x-0.3;d.z=it.z;return [its.length,it.type,Math.hypot(it.x-d.x,it.z-d.z).toFixed(2)]});
  console.log('items on ground',st);await p.waitForTimeout(800);
  console.log('carrying',await p.evaluate(()=>__g.dog.item&&__g.dog.item.type));
  await p.keyboard.press(' ');await p.waitForTimeout(400);
  console.log('after bark carrying',await p.evaluate(()=>!!__g.dog.item));
  await p.keyboard.down('r');await p.keyboard.up('r');await p.keyboard.down('w');await p.waitForTimeout(2500);
  console.log('run speed',await p.evaluate(()=>__g.dog.speed.toFixed(2)));
  await p.screenshot({path:'shot5a.png'});await p.keyboard.up('w');
  await p.evaluate(()=>{const d=__g.dog;d.heading=Math.PI*0.75});await p.waitForTimeout(600);
  await p.mouse.move(500,300);await p.mouse.down();await p.mouse.move(820,330,{steps:8});await p.mouse.up();await p.waitForTimeout(800);
  await p.screenshot({path:'shot5b.png'});
  await p.waitForTimeout(12000);
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
