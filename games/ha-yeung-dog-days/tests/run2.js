const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1100,height:700}});const errs=[];
  p.on('pageerror',e=>errs.push('PAGEERR '+e.message));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push('CONSOLE '+m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  const t0=Date.now();
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'ha-yeung-dog-days.html'),'utf8')+'</body></html>');
  await p.waitForTimeout(2500);console.log('load ms',Date.now()-t0);
  await p.click('#startBtn');await p.waitForTimeout(1500);
  await p.screenshot({path:'shot2a.png'});
  await p.keyboard.down('d');await p.waitForTimeout(900);await p.keyboard.up('d');await p.mouse.move(550,300);await p.mouse.down();await p.mouse.move(550,560,{steps:10});await p.mouse.up();for(let i=0;i<8;i++){await p.mouse.wheel(0,600);await p.waitForTimeout(100)}await p.waitForTimeout(1500);
  await p.screenshot({path:'shot2b.png'});
  console.log(errs.length?errs.join('\n'):'NO_ERRORS');await b.close()})();
