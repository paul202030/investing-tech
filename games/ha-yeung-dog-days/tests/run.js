const { chromium } = require('playwright');
const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']}).catch(async()=>chromium.launch({args:['--use-gl=swiftshader','--enable-webgl']}));
  const p=await b.newPage({viewport:{width:1100,height:700}});
  const errs=[];p.on('pageerror',e=>errs.push('PAGEERR '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});if(u.startsWith('file:'))return r.continue();return r.abort()});
  const html=fs.readFileSync(path.join(__dirname,'ha-yeung-dog-days.html'),'utf8');
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+html+'</body></html>');
  await p.waitForTimeout(1500);
  await p.click('#startBtn');
  await p.keyboard.down('w');await p.waitForTimeout(1500);await p.keyboard.up('w');
  await p.keyboard.press('c');await p.waitForTimeout(800);
  await p.keyboard.press(' ');await p.keyboard.press('e');await p.keyboard.press('f');
  await p.waitForTimeout(2500);
  await p.screenshot({path:'shot.png'});
  console.log(errs.length?errs.join('\n'):'NO_ERRORS');
  await b.close();
})();
