const { chromium } = require('playwright');const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:700,height:450}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.route('**/*',r=>{const u=r.request().url();if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(path.join(__dirname,'lib/node_modules/three/build/three.min.js')),contentType:'application/javascript'});return r.abort()});
  await p.setContent('<!doctype html><html><head><meta charset="utf-8"></head><body>'+fs.readFileSync(path.join(__dirname,'perf3.html'),'utf8')+'</body></html>');
  await p.waitForTimeout(2000);await p.waitForSelector('#startBtn:not([disabled])');await p.click('#startBtn');await p.waitForTimeout(500);
  const pos=()=>p.evaluate(()=>{const d=window.__g.dog;return [+d.x.toFixed(1),+d.z.toFixed(1),+d.y.toFixed(1),+d.speed.toFixed(2),d.action,d.posture]});
  for(const k of ['w','d','s','a','w','w','w','d','d','w','a','s','w','d','s']){const a=await pos();await p.keyboard.down('Shift');await p.keyboard.down(k);await p.waitForTimeout(3000);await p.keyboard.up(k);await p.keyboard.up('Shift');const c=await pos();
    console.log(k,JSON.stringify(a),'->',JSON.stringify(c),'moved',Math.hypot(c[0]-a[0],c[1]-a[1]).toFixed(1))}
  console.log(errs.join('\n')||'NO_ERRORS');await b.close()})();
