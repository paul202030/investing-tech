const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:900,height:600}});const errs=[];
  p.on('pageerror',e=>errs.push('PAGEERR '+(e.stack||e.message)));p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('ERR_FAILED'))errs.push('CONSOLE '+m.text())});
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'ha-yeung-dog-days.html'),'utf8')+'</body></html>');
  await p.waitForTimeout(2000);await p.click('#startBtn');
  for(let i=0;i<20;i++){
    const k=['w','a','w','d','s'][i%5];await p.keyboard.down(k);await p.waitForTimeout(1000);await p.keyboard.up(k);
    const c=await p.evaluate(()=>document.getElementById('clock').textContent);
    console.log('t',i+1,'clock',c,'errs',errs.length);
    if(errs.length)break;
  }
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
