#!/usr/bin/env python3
# Harder, more arcade police chases (survive 3:00 with no crashes; crash / hop off = busted; stages, countdown,
# red-blue screen edges, full-screen wipe transitions) + pack friends jump into your golf cart / plane with you.
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'CHASE_T' not in src, 'already transformed'
k = src.rfind('<script>'); h, c = src[:k], src[k:]
def R(part, old, new):
    assert part.count(old) == 1 and src.count(old) == 1, (part.count(old), old[:80])
    return part.replace(old, new)

# ---------- HTML + CSS
h = R(h, '<div id="vignette"></div>', '<div id="vignette"></div><div id="copFx"></div><div id="copWipe"><div class="cwIn"><b class="cwT"></b><span class="cwS"></span></div></div>')
h = R(h, '</style>', '''#copFx{position:fixed;inset:0;pointer-events:none;z-index:6;opacity:0;transition:opacity .4s}
#copFx.on{opacity:1;animation:copFl .5s steps(1) infinite}
@keyframes copFl{0%{box-shadow:inset 26px 0 40px -10px rgba(255,30,40,.75),inset -26px 0 40px -10px rgba(30,90,255,.75)}50%{box-shadow:inset 26px 0 40px -10px rgba(30,90,255,.75),inset -26px 0 40px -10px rgba(255,30,40,.75)}}
#copWipe{position:fixed;inset:0;pointer-events:none;z-index:40;display:none;align-items:center;justify-content:center;overflow:hidden}
#copWipe.show{display:flex}
#copWipe::before{content:"";position:absolute;inset:-20% -60%;background:repeating-linear-gradient(-55deg,#ffd400 0 46px,#14161c 46px 92px);animation:cwSweep 1.7s cubic-bezier(.7,0,.3,1) forwards}
#copWipe.win::before{background:repeating-linear-gradient(-55deg,#2fd06a 0 46px,#0f2a1a 46px 92px)}
#copWipe.lose::before{background:repeating-linear-gradient(-55deg,#ff3045 0 46px,#1a0b0e 46px 92px)}
#copWipe .cwIn{position:relative;text-align:center;background:#0d0f14;color:#fff;padding:14px 26px;border:4px solid #fff;border-radius:6px;transform:skewX(-8deg);animation:cwPop 1.7s ease forwards;font-family:inherit}
#copWipe .cwT{display:block;font-size:clamp(28px,7vw,64px);font-weight:900;letter-spacing:.04em;text-shadow:3px 3px 0 #ff3045,-3px -3px 0 #2a6cff}
#copWipe .cwS{display:block;margin-top:4px;font-size:clamp(13px,2.6vw,20px);font-weight:700;color:#ffd400}
@keyframes cwSweep{0%{transform:translateX(-110%)}35%,65%{transform:translateX(0)}100%{transform:translateX(110%)}}
@keyframes cwPop{0%{opacity:0;transform:skewX(-8deg) scale(2.4)}22%{opacity:1;transform:skewX(-8deg) scale(1)}75%{opacity:1;transform:skewX(-8deg) scale(1.04)}100%{opacity:0;transform:skewX(-8deg) scale(.8)}}
</style>''')

# ---------- police: survive 3 minutes, no crashes
c = R(c, "function endPolice(won){const P=police;P.state='leave';P.t=0;",
      "const CHASE_T=180;let wipeTimer=null;\n"
      "function copWipe(t,sub,kind){const el=$('#copWipe');el.querySelector('.cwT').textContent=t;el.querySelector('.cwS').textContent=sub;el.className='';void el.offsetWidth;el.className='show '+(kind||'');clearTimeout(wipeTimer);wipeTimer=setTimeout(()=>{el.className=''},1750)}\n"
      "function policeCrash(why){if(police&&police.state==='chase'){police.why=why;endPolice(false)}}\n"
      "function endPolice(won){const P=police;P.state='leave';P.t=0;$('#copFx').classList.remove('on');shake();")
c = R(c, "popScore('+500');S.points+=500;S.happy=Math.min(100,S.happy+15);complete('police');",
      "popScore('PERFECT RUN! +2000');S.points+=2000;S.happy=Math.min(100,S.happy+25);complete('police');copWipe('にげきった!!','3:00 PERFECT RUN · ESCAPED!','win');")
c = R(c, "else{arcade('つかまった…','BUSTED!','lose');",
      "else{const why=P.why;P.why='';arcade(why==='crash'?'クラッシュ!':'つかまった…',why==='crash'?'CRASHED! BUSTED!':why==='hop'?'OUT OF THE CART! BUSTED!':'BUSTED!','lose');copWipe('BUSTED!',why==='crash'?'You crashed. Drive perfectly!':why==='hop'?'Never leave the cart mid-chase!':'They caught up with you!','lose');")
c = R(c, "if(!k){P.state='leave';P.t=0;", "if(!k){P.why='hop';endPolice(false);return;")
c = R(c, "const top=(d>45?19.5:18)*", "const top=(d>45?23.5:21)*")
c = R(c, "else if(d>90||P.t>30)endPolice(true)}",
      "else if(P.t>CHASE_T)endPolice(true);\n"
      "    else{const st=Math.floor(P.t/30);if(st>(P.stage||0)){P.stage=st;S.points+=100;popScore('CLEAN '+st*30+'s +100');arcade('ステージ '+st+'!','STAGE '+st+' · '+Math.ceil((CHASE_T-P.t)/60*10)/10+' MIN LEFT','clear');sfx.ding()}\n"
      "      const left=CHASE_T-P.t;if(left<10&&Math.ceil(left)!==P.lastSec){P.lastSec=Math.ceil(left);sfx.beep();popScore(String(P.lastSec))}\n"
      "      if(d>120){P.farT=(P.farT||0)+dt;if(P.farT>3){P.farT=0;const bx=dog.x-Math.sin(k.h)*55,bz=dog.z-Math.cos(k.h)*55;if(gridH(bx,bz)>0.5&&!bldAt(bx,bz)){P.x=bx;P.z=bz;P.h=k.h;P.v=15;toast('📻 Backup unit right behind you!')}}}else P.farT=0}}")
c = R(c, "arcade('逃げろ!','POLICE!','run');shake();",
      "P.stage=0;P.lastSec=-1;P.why='';P.farT=0;$('#copFx').classList.add('on');copWipe('警察追跡!','POLICE CHASE · SURVIVE 3:00 · NO CRASHES','');arcade('逃げろ!','POLICE!','run');shake();")
c = R(c, "Lose them: get 90 m away or hold out for 30 seconds.",
      "Survive 3 minutes: no crashes, no hopping off. Turbo with Shift!")
c = R(c, "police.state==='chase'?[police,'POLICE '+Math.max(0,Math.ceil(30-police.t))+'s',90]:null",
      "police.state==='chase'?[police,'POLICE '+Math.floor(Math.max(0,CHASE_T-police.t)/60)+':'+String(Math.floor(Math.max(0,CHASE_T-police.t)%60)).padStart(2,'0'),60]:null")
# crashes while chased: walls at speed, or driving into the water fast
c = R(c, "x=nx;z=nz;if(hit){if(Math.abs(k.v)>1.8){sfx.bonk();",
      "x=nx;z=nz;if(hit){if(Math.abs(k.v)>4&&police&&police.state==='chase'){sfx.bonk();policeCrash('crash');break}if(Math.abs(k.v)>1.8){sfx.bonk();")
c = R(c, "if(gridH(px,pz)<0.3||CLS[cellIdx(px,pz)]===4){k.v=0;",
      "if(gridH(px,pz)<0.3||CLS[cellIdx(px,pz)]===4){if(Math.abs(k.v)>6&&police&&police.state==='chase'){k.v=0;policeCrash('crash');break}k.v=0;")
c = R(c, "$('#arcade').className='';$('#game').classList.remove('dogvis');",
      "$('#arcade').className='';$('#game').classList.remove('dogvis');$('#copFx').classList.remove('on');$('#copWipe').className='';")

# ---------- pack friends ride along in carts and planes
c = R(c, "const npcDogs=[];", "const npcDogs=[];const RIDEV=new THREE.Vector3();")
c = R(c, "if(o.kind==='friend')friendUpd(o,d,dt);",
      "if(o.kind==='friend'&&o.st==='follow'&&dog.cart&&dog.cart.g){const rk=dog.cart,si=S.pack.indexOf(o.id);if(si>=0&&si<2){\n"
      "      if(o.ride!==rk){o.ride=rk;o.hopT=0.6;o.hx=o.x;o.hz=o.z;o.hy=o.y;if(si===0){arcade('のって!','ALL ABOARD!','clear');sfx.beep()}say(o,breedInfo(o.breed).bark.split(' ')[0],1)}\n"
      "      rk.g.updateMatrixWorld();const se=rk.seat||{x:-0.15,y:0.78,z:0.22};rk.g.localToWorld(RIDEV.set(se.x-0.8,se.y+0.02,si?-0.3:0.3));\n"
      "      if(o.hopT>0){o.hopT-=dt;const t=1-Math.max(0,o.hopT)/0.6;o.x=o.hx+(RIDEV.x-o.hx)*t;o.z=o.hz+(RIDEV.z-o.hz)*t;o.y=o.hy+(RIDEV.y-o.hy)*t+Math.sin(t*Math.PI)*1.3}else{o.x=RIDEV.x;o.z=RIDEV.z;o.y=RIDEV.y}\n"
      "      o.g.visible=true;o.h=rk.h;o.sit=o.tSit=1;o.lie=o.tLie=0;o.tail&&0;poseDog2(o,0,dt);o.g.position.set(o.x,o.y,o.z);o.g.rotation.set(-(rk.pitch||0),o.h,0);continue}}\n"
      "    if(o.ride&&!dog.cart){o.ride=null;o.g.rotation.x=0;o.tSit=0;const gy=groundAt(o.x,o.z);if(o.y-gy>3){o.x=dog.x+1.2;o.z=dog.z+1.2}}\n"
      "    if(o.kind==='friend')friendUpd(o,d,dt);")
src = h + c
open(G + 'index.html', 'w', encoding='utf-8').write(src)
print('ok')
