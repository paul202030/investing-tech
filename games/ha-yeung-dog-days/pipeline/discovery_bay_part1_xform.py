#!/usr/bin/env python3
# Discovery Bay part 1: two-level engine, DB level, bus travel, golf carts.
import json, sys
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
i = src.find('id="worldData"'); i = src.find('>', i) + 1; j = src.find('</script>', i)
head, hy, code = src[:i], src[i:j], src[j:]
assert 'worldDataDB' not in src, 'already transformed'

def R(s, old, new, n=1):
    c = s.count(old)
    assert c == n, (c, old[:120])
    return s.replace(old, new)

# ---------------- head: CSS, HUD, overlay, start card ----------------
CSS = '''#aCtx{grid-column:1 / -1;width:150px;height:58px!important;border-radius:29px;display:flex;gap:8px;align-items:center;justify-content:center;background:var(--green);color:#fff;font-size:18px;box-shadow:0 5px 0 #144a31,0 10px 24px rgba(0,0,0,.35);animation:stealPop .45s cubic-bezier(.2,1.6,.4,1) both}
#aCtx small{color:rgba(255,255,255,.8)}
#aCtx[hidden]{display:none!important}
#fade{position:fixed;inset:0;z-index:7;display:grid;place-items:center;background:var(--night);opacity:0;pointer-events:none;transition:opacity .6s ease}
#fade.on{opacity:1;pointer-events:auto}
#fade .fadeCard{text-align:center;color:#f6efdf;font-family:var(--display);font-weight:800;font-size:clamp(20px,4.5vw,30px);padding:0 16px}
#fade .fadeBus{font-size:56px;line-height:1;margin-bottom:12px;animation:busBob .5s ease-in-out infinite alternate}
@keyframes busBob{from{transform:translateY(0)}to{transform:translateY(-6px)}}
@media (prefers-reduced-motion:reduce){#aCtx,#fade .fadeBus{animation:none}#fade{transition:none}}
</style>'''
head = R(head, '</style>', CSS)
head = R(head, '<span class="han">下洋</span> Ha Yeung · ', '<span class="han" id="plZh">下洋</span> <span id="plName">Ha Yeung</span> · ')
head = R(head, '<button class="act" id="aSteal" type="button" hidden>Steal!<small>T</small></button>',
         '<button class="act" id="aCtx" type="button" hidden>Hop on<small>X</small></button>\n    <button class="act" id="aSteal" type="button" hidden>Steal!<small>T</small></button>')
head = R(head, ' · C sit, then lie down · drag to look</div>', ' · C sit, then lie down · X bus / golf cart · drag to look</div>')
head = R(head, '<div id="bubbles"></div>', '<div id="bubbles"></div>\n<div id="fade"><div class="fadeCard"><div class="fadeBus" aria-hidden="true">🚌</div><p id="fadeMsg" role="status" aria-live="polite"></p></div></div>')
head = R(head, 'and nap in the sun.</p>', 'and nap in the sun. When the bus pulls in, hop on and ride to Discovery Bay, where the residents drive golf carts. So can you.</p>')
head = R(head, '<kbd>Q or tap the map</kbd>', '<kbd>X</kbd><span>Board the bus at the stop; hop on or off a golf cart</span>\n      <kbd>Q or tap the map</kbd>')

# ---------------- code ----------------
c = code
# move the audio section out of the level so one AudioContext serves every level
a0 = c.index('// ================= Audio (synthesized) =================')
a1 = c.index('// ================= Input =================')
audio = c[a0:a1]; c = c[:a0] + c[a1:]
audio = R(audio, "honk(){tone('square',392,390,0.38,0.06);tone('square',494,492,0.38,0.06)},",
  "honk(){tone('square',392,390,0.38,0.06);tone('square',494,492,0.38,0.06)},\n    beep(){tone('square',988,988,0.1,0.04);tone('square',988,988,0.1,0.04,0.16)},bonk(){burst(260,1.2,0.18,0.35);tone('sine',190,80,0.25,0.18)},")

LEVELS = r'''// ================= Levels: Ha Yeung and Discovery Bay share one engine =================
// Each level is built by runLevel() and torn down by its destroy(): listeners go through an AbortController,
// the frame loop is cancelled, GPU resources are disposed and the canvas removed. Dog name, points, stash,
// to-dos, time of day and stats travel in a snapshot.
const LEVELS={hy:'worldData',db:'worldDataDB'};
const LVDEF={hy:{level:'hy',name:'Ha Yeung',nameZh:'下洋',busDest:'下洋 HA YEUNG',otherDest:'愉景灣 DISCOVERY BAY',signText:'永發士多  WING FAT STORE',roadName:'Clear Water Bay Road'}};
function loadWorld(id){const w=JSON.parse(document.getElementById(LEVELS[id]).textContent);const d=LVDEF[id]||{};for(const k in d)if(w[k]===undefined)w[k]=d[k];w.places.carts=w.places.carts||[];return w}
function fade(on,msg){if(msg!==undefined)$('#fadeMsg').textContent=msg;$('#fade').classList.toggle('on',!!on)}
let LV=null;
function buildLevel(id,data,arrive){const AC=new AbortController(),P=EventTarget.prototype,orig=P.addEventListener;
  P.addEventListener=function(t,f,o){if(typeof o==='boolean')o={capture:o};return orig.call(this,t,f,Object.assign({signal:AC.signal},o||{}))};
  try{return runLevel(id,data,arrive,AC)}finally{P.addEventListener=orig}}
function switchLevel(id,carry){const old=LV;LV=null;if(old)try{old.destroy()}catch(e){console.error(e)}
  setTimeout(()=>{try{LV=buildLevel(id,carry,true)}catch(e){console.error(e);fade(false)}},40)}

function runLevel(LEVEL,BOOT,ARRIVE,AC){
seed=11;
'''
c = R(c, '// ================= Real-world data =================\nconst WD=JSON.parse(document.getElementById(\'worldData\').textContent);',
  audio + LEVELS + "// ================= Real-world data =================\nconst WD=loadWorld(LEVEL);\nconst OTHER=WD.level==='db'?'hy':'db',OTHERNAME=OTHER==='db'?'Discovery Bay':'Ha Yeung';")

# signs and labels
c = R(c, "x.fillText('下洋',w/2,56);x.font='bold 22px sans-serif';x.fillText('HA YEUNG',w/2,92)",
         "x.fillText(WD.nameZh,w/2,56,w-16);x.font='bold 22px sans-serif';x.fillText(WD.name.toUpperCase(),w/2,92,w-16)")
c = R(c, "x.fillText('永發士多  WING FAT STORE',W/2,H/2+2)", "x.fillText(WD.signText,W/2,H/2+2,W-12)")
c = R(c, "x.fillText('下洋 HA YEUNG',w/2,h/2+1)", "x.fillText(WD.otherDest,w/2,h/2+1,w-8)")
c = R(c, "// red door marker for home\n{const hb=BL[PL.home];", "// red door marker for home (Discovery Bay only has a rest spot)\nif(!PL.noHome){const hb=BL[PL.home];")
c = R(c, "const hb=BL[PL.home];c.fillStyle='#c4372d';", "const hb=PL.noHome?null:BL[PL.home];if(hb){c.fillStyle='#c4372d';")
c = R(c, "c.closePath();c.fill()}\nconst MAPWIN", "c.closePath();c.fill()}}\nconst MAPWIN")
c = R(c, "const PLACES=[['Home',", "const PLACES=[[PL.noHome?'Rest spot':'Home',")
c = R(c, "function drawBigMap(){", "if(PL.carts.length)PLACES.push(['Golf carts',PL.carts[0][0],PL.carts[0][1],'#f6f4ee']);\nfunction drawBigMap(){")
c = R(c, "'Best BBQ in Ha Yeung!'", "'Best BBQ in '+WD.name+'!'")
c = R(c, "A perfect Ha Yeung day.')", "A perfect '+WD.name+' day.')")
c = R(c, "toast('Best dog in Ha Yeung! Everything done today.')", "toast('Best dog in '+WD.name+'! Everything done today.')")
c = R(c, "toast('Night falls over Ha Yeung. Time speeds up until sunrise.')", "toast('Night falls over '+WD.name+'. Time speeds up until sunrise.')")
c = R(c, "toast('Day '+S.day+' in Ha Yeung. A new list of things to do!')", "toast('Day '+S.day+' in '+WD.name+'. A new list of things to do!')")
c = R(c, "['chaseBus','Chase the bus along Clear Water Bay Road']", "['chaseBus','Chase the bus along '+WD.roadName]")
c = R(c, "['nap','Nap in your bed at home']", "['nap','Nap in your bed']")
c = R(c, "['minibus','Sit at the bus stop to hail a green minibus'],['picnic','Snatch a snack from the beach picnic']]",
         "['minibus','Sit at the Ha Yeung bus stop to hail a green minibus'],['picnic','Snatch a snack from the beach picnic'],['bus','Ride the bus between Ha Yeung and Discovery Bay'],['cart','Drive a golf cart in Discovery Bay']]")

# state: stash list survives level changes
c = R(c, "const S={started:false,", "const S={stash:[],started:false,")
c = R(c, "dog.item=null;it.state='stash';S.stashN=(S.stashN||0)+1;S.stashDay=(S.stashDay||0)+1;const a=S.stashN*0.95,r=0.95+Math.min(0.6,S.stashN*0.03);\n      it.x=BED.x+Math.cos(a)*r;it.z=BED.z+Math.sin(a)*r;it.g.position.set(it.x,groundAt(it.x,it.z)+it.T.r,it.z);it.g.rotation.set(0,Math.random()*6.28,0);",
         "dog.item=null;S.stash.push(it.type);S.stashN=S.stash.length;S.stashDay=(S.stashDay||0)+1;stashPlace(it,S.stashN);")
c = R(c, "function updateItems(dt){",
  "function stashPlace(it,n){const a=n*0.95,r=0.95+Math.min(0.6,n*0.03);it.state='stash';it.x=BED.x+Math.cos(a)*r;it.z=BED.z+Math.sin(a)*r;it.g.position.set(it.x,groundAt(it.x,it.z)+it.T.r,it.z);it.g.rotation.set(0,Math.random()*6.28,0)}\nfunction updateItems(dt){")
c = R(c, "if(S.started&&!dog.item&&!dog.holding&&!dog.action&&", "if(S.started&&!dog.cart&&!dog.item&&!dog.holding&&!dog.action&&")
c = R(c, "if(!dog.holding&&!dog.item&&!dog.action&&Math.hypot(ball.x-dog.x", "if(!dog.cart&&!dog.holding&&!dog.item&&!dog.action&&Math.hypot(ball.x-dog.x")

# dog model: pitch with the cart
c = R(c, "const root=new THREE.Group();const hip=new THREE.Group();", "const root=new THREE.Group();root.rotation.order='YXZ';const hip=new THREE.Group();")

# no taxis or green minibuses in Discovery Bay; golf carts instead
CARTS = r'''if(WD.level==='db'){taxi.wait=Infinity;mini.wait=Infinity}
// ================= Golf carts: parked ones the dog can drive, resident ones on the main road =================
function makeCart(col){const g=new THREE.Group(),body=new THREE.Group();g.add(body);const shell=mat(col),blk=mat(0x1a1a1a),seat=mat(0x2d5f8a),pole=mat(0xbfc4c6);
  box(shell,2.3,0.32,1.15,0,0.42,0,body);box(shell,0.6,0.42,1.12,0.88,0.74,0,body);box(seat,0.55,0.14,1.0,-0.2,0.7,0,body);box(seat,0.12,0.5,1.0,-0.48,0.98,0,body);
  box(shell,0.55,0.26,1.12,-0.86,0.7,0,body);box(mat(0x3a3a3a),0.32,0.5,0.6,-0.95,1.05,0,body);
  for(const x of [0.62,-0.62])for(const z of [-0.52,0.52])cyl(pole,0.025,0.025,1.15,x,1.42,z,body,5);
  box(mat(0xf6f4ee),1.65,0.07,1.25,0,2.0,0,body);
  const ws=new THREE.Mesh(new THREE.BoxGeometry(0.03,0.6,1.05),new THREE.MeshLambertMaterial({color:0xa9d3dd,transparent:true,opacity:0.35}));ws.position.set(0.64,1.5,0);body.add(ws);
  const sw=new THREE.Mesh(new THREE.TorusGeometry(0.15,0.025,6,14),blk);sw.position.set(0.42,1.08,0.25);sw.rotation.set(0,Math.PI/2,0);sw.rotateX(0.6);body.add(sw);
  for(const x of [0.75,-0.75])for(const z of [-0.55,0.55]){const w=cyl(blk,0.22,0.22,0.16,x,0.22,z,body,12);w.rotation.x=Math.PI/2}
  scene.add(g);return {g,body}}
// heading h like the dog: forward = (sin h, cos h); the model's nose is +x
function placeCart(c){const fx=Math.sin(c.h),fz=Math.cos(c.h);const gf=groundAt(c.x+fx*0.8,c.z+fz*0.8),gb=groundAt(c.x-fx*0.8,c.z-fz*0.8);c.y=(gf+gb)/2;c.pitch=Math.atan2(gf-gb,1.6);
  c.g.position.set(c.x,c.y,c.z);c.g.rotation.set(0,c.h-Math.PI/2,c.pitch)}
const CART_COLS=[0xf2f0e8,0xe9e4d6,0xdfe9e2,0xf3e6c4,0xe6edf2,0xf2f0e8];
const carts=PL.carts.map((p,i)=>Object.assign(makeCart(CART_COLS[i%6]),{x:p[0],z:p[1],h:p[2],v:0,y:0,pitch:0,dist:0}));carts.forEach(placeCart);
const aiCarts=WD.level==='db'?[0,1,2].map(i=>{const c=makeCart([0xf2f0e8,0xdfe9e2,0xf3e6c4][i]);
  const drv=makePerson([{shirt:0x5d93b8,pants:0xe8e2cf,hair:0x2a2420},{shirt:0xf08ab0,pants:0x2a2a3a,hair:0x6b4a2a,skin:0xf0c8a8},{shirt:0xffffff,pants:0x3a5a3a,hair:0xd8d4cc}][i]);
  c.body.add(drv.g);drv.g.position.set(-0.2,-0.06,0.25);drv.g.rotation.y=Math.PI/2;drv.legs.forEach(l=>l.rotation.x=-1.45);drv.arms.forEach(a=>a.rotation.x=-1.1);c.g.visible=false;
  return Object.assign(c,{drv,x:0,z:-9999,along:-99,lat:99,fx:1,fz:0,s:0,v:0,state:'gone',wait:2+i*11,honkT:0,dir:i%2?-1:1,half:1.4,lane:1.9,speed:6+i*0.7,cart:true,headY:1.7})}):[];
const walkers=[];'''
c = R(c, "\nconst walkers=[];", "\n" + CARTS)

# vehicles: carts beep and don't nag; bus waits a little longer; the player's cart gets shoved, not the dog
c = R(c, "if(S.t-v.honkT>4){v.honkT=S.t;sfx.honk();if(v!==taxi)toast(", "if(S.t-v.honkT>4){v.honkT=S.t;v.cart?sfx.beep():sfx.honk();if(v!==taxi&&!v.cart)toast(")
c = R(c, "v.state='dwell';v.dwell=v.mini?4.5:7;", "v.state='dwell';v.dwell=v.mini?4.5:12;if(v===bus&&S.started&&!dog.cart&&Math.hypot(dog.x-PL.stop[0],dog.z-PL.stop[1])<30)toast('The bus to '+OTHERNAME+' is here! '+(mobile?'Tap':'Press X or tap')+' Board bus to hop on.');")
c = R(c, "dog.z=v.z+lz*s*1.9+v.fz*v.along;S.happy=Math.max(0,S.happy-3)}}",
         "dog.z=v.z+lz*s*1.9+v.fz*v.along;S.happy=Math.max(0,S.happy-3);if(dog.cart){dog.cart.x=dog.x;dog.cart.z=dog.z;dog.cart.v=0}}}")
c = R(c, "updateVehicle(bus,dt);updateVehicle(taxi,dt);updateVehicle(mini,dt);", "updateVehicle(bus,dt);updateVehicle(taxi,dt);updateVehicle(mini,dt);for(const v of aiCarts)updateVehicle(v,dt);")
c = R(c, "if(mini.g.visible)dot(mini.x,mini.z,'#1f7a4a',3.5,true);", "if(mini.g.visible)dot(mini.x,mini.z,'#1f7a4a',3.5,true);for(const k of carts)dot(k.x,k.z,'#f6f4ee',2.6,true);for(const k of aiCarts)if(k.g.visible)dot(k.x,k.z,'#f6f4ee',2.6,true);")

# input
c = R(c, "if(keys[k])return;keys[k]=true;if(!S.started)return;", "if(keys[k])return;keys[k]=true;if(!S.started||S.leaving)return;")
c = R(c, "else if(k==='t')steal();", "else if(k==='t')steal();else if(k==='x')doCtx();")
c = R(c, "bind('#aSteal',()=>steal());", "bind('#aSteal',()=>steal());bind('#aCtx',()=>doCtx());")

# actions
c = R(c, "||(dog.bellyT>0)||dog.shakeT>0;", "||(dog.bellyT>0)||dog.shakeT>0||!!dog.cart||!!S.leaving;")
c = R(c, "function toggleSniff(){if(dog.swimming)", "function toggleSniff(){if(dog.cart)return;if(dog.swimming)")
ACTIONS = r'''function doSit(){'''
CTX = r'''// context action: board the bus, hop on or off a golf cart
function nearCart(){if(dog.cart||!S.started||busy()||dog.swimming)return null;let b=null,bd=2.8;for(const k of carts){const d=Math.hypot(k.x-dog.x,k.z-dog.z);if(d<bd){bd=d;b=k}}return b}
function ctxAction(){if(!S.started||S.leaving)return null;
  if(dog.cart)return Math.abs(dog.cart.v)<1.2?{l:'Hop off',f:hopOff}:null;
  if(bus.state==='dwell'&&!dog.swimming&&!busy()&&Math.min(Math.hypot(bus.x-dog.x,bus.z-dog.z),Math.hypot(PL.stop[0]-dog.x,PL.stop[1]-dog.z))<10)return {l:'Board bus',f:boardBus};
  const k=nearCart();return k?{l:'Hop on',f:()=>hopOn(k)}:null}
function doCtx(){const a=ctxAction();if(a)a.f()}
function hopOn(k){dropBall();dog.sniff=false;$('#vignette').classList.remove('on');dog.cart=k;k.v=0;dog.camDist=cam.dist;cam.dist=Math.max(cam.dist,7.5);sfx.beep();
  if(!S.cartHint){S.cartHint=true;toast(mobile?'Beep beep! Push the stick up to drive, sideways to steer, down to brake and reverse.':'Beep beep! W / ↑ to drive, S / ↓ to brake and reverse, A D / ← → to steer.');toast('Stop the cart, then tap Hop off'+(mobile?'':' (or press X)')+' to get out.')}else toast('Beep beep!')}
function hopOff(){const k=dog.cart;if(!k)return;const lx=Math.cos(k.h),lz=-Math.sin(k.h);let x=k.x+lx*1.6,z=k.z+lz*1.6;if(bldAt(x,z)||gridH(x,z)<0.2){x=k.x-lx*1.6;z=k.z-lz*1.6}
  dog.cart=null;k.v=0;dog.x=x;dog.z=z;dog.y=groundAt(x,z);dog.posture='stand';dog.heading=k.h;cam.dist=dog.camDist||5.5;D.root.rotation.x=0}
function boardBus(){S.leaving=true;dropBall();standUp();dog.sniff=false;$('#vignette').classList.remove('on');dog.speed=0;sfx.ding();bus.dwell=Math.max(bus.dwell,3);
  fade(true,'Taking the bus to '+OTHERNAME+'…');setTimeout(()=>{if(!dead)switchLevel(OTHER,snapshot())},900)}
// driving: W/S throttle and reverse, A/D steer; the joystick does both. Bumps off buildings, stops at the water.
function rideCart(dt){const k=dog.cart;let th=0,st=0;
  if(!S.leaving){if(keys.w||keys.arrowup)th+=1;if(keys.s||keys.arrowdown)th-=1;if(keys.d||keys.arrowright)st+=1;if(keys.a||keys.arrowleft)st-=1;if(joy.mag>0.12){th=-joy.y;st=joy.x}}
  const want=th>0.05?th*6.5:th<-0.05?th*2.5:0;
  if(Math.abs(th)<=0.05)k.v=Math.abs(k.v)<0.15?0:k.v-Math.sign(k.v)*3*dt;
  else if(Math.sign(want)!==Math.sign(k.v)&&Math.abs(k.v)>0.1)k.v-=Math.sign(k.v)*8*dt;
  else k.v+=clamp(want-k.v,-4*dt,2.6*dt);
  k.h-=st*1.5*dt*clamp(k.v/2.5,-1,1);
  const fx=Math.sin(k.h),fz=Math.cos(k.h),dir=k.v<0?-1:1;let nx=k.x+fx*k.v*dt,nz=k.z+fz*k.v*dt;
  const px=nx+fx*1.4*dir,pz=nz+fz*1.4*dir;
  if(k.v!==0&&(gridH(px,pz)<0.3||CLS[cellIdx(px,pz)]===4)){nx=k.x;nz=k.z;k.v=0;if(S.t-(k.waterT||-99)>6){k.waterT=S.t;toast('The cart stops at the water\'s edge. Golf carts can\'t swim!')}}
  else if(k.v!==0&&(gridH(px,pz)-gridH(k.x,k.z))/1.4>0.9){nx=k.x;nz=k.z;k.v=0;if(S.t-(k.steepT||-99)>6){k.steepT=S.t;toast('Too steep for a golf cart.')}}
  let hit=false;for(const o of [0.6,-0.6]){const qx=nx+fx*o,qz=nz+fz*o;const [rx,rz]=pushOutB(qx,qz,0.75);if(Math.hypot(rx-qx,rz-qz)>0.02){hit=true;nx+=rx-qx;nz+=rz-qz}}
  if(hit){if(Math.abs(k.v)>1.8){sfx.bonk();say(DOGTALK,'Bonk!',0.9);S.happy=Math.max(0,S.happy-1)}k.v*=-0.25}
  for(const s of softColliders){const ex=nx-s[0],ez=nz-s[1],L=Math.hypot(ex,ez);if(L<s[2]+1.0&&L>1e-4){nx=s[0]+ex/L*(s[2]+1.0);nz=s[1]+ez/L*(s[2]+1.0);k.v*=0.5}}
  for(const o of carts){if(o===k)continue;const ex=nx-o.x,ez=nz-o.z,L=Math.hypot(ex,ez);if(L<2.0&&L>1e-4){nx=o.x+ex/L*2.0;nz=o.z+ez/L*2.0;k.v*=0.5}}
  k.x=clamp(nx,X0+20,X1-20);k.z=clamp(nz,Z0+20,Z1-20);k.dist+=Math.abs(k.v)*dt;if(k.dist>60)complete('cart');placeCart(k);
  k.g.updateMatrixWorld();const sp=k.g.localToWorld(v3.set(-0.15,0.78,0.22));dog.x=sp.x;dog.z=sp.z;dog.y=sp.y;dog.heading=k.h;dog.posture='sit';dog.speed=0;dog.sitT=0;dog.swimming=false;
  if(dog.barkT>0)dog.barkT-=dt;D.root.position.set(dog.x,dog.y,dog.z);D.root.rotation.set(-k.pitch,dog.heading,0)}
function doSit(){'''
c = R(c, ACTIONS, CTX)

# dog sim: ride the cart, freeze while leaving, bump into parked carts
c = R(c, "function updateDog(dt){dog.sitT=", "function updateDog(dt){if(dog.cart){rideCart(dt);return}dog.sitT=")
c = R(c, "if(S.started){if(keys.w||keys.arrowup)iy+=1;", "if(S.started&&!S.leaving){if(keys.w||keys.arrowup)iy+=1;")
c = R(c, "nz=c[1]+ez/L*(c[2]+0.4)}}dog.x=clamp(nx,X0+20,X1-20);",
         "nz=c[1]+ez/L*(c[2]+0.4)}}for(const k of carts){const ex=nx-k.x,ez=nz-k.z,L=Math.hypot(ex,ez);if(L<1.5&&L>1e-4){nx=k.x+ex/L*1.5;nz=k.z+ez/L*1.5}}dog.x=clamp(nx,X0+20,X1-20);")
c = R(c, "D.root.position.set(dog.x,dog.y+dog.roll*0.12,dog.z);D.root.rotation.y=dog.heading;", "D.root.position.set(dog.x,dog.y+dog.roll*0.12,dog.z);D.root.rotation.x=0;D.root.rotation.y=dog.heading;")

# big map travel leaves the cart where it is
c = R(c, "if(bbq.state==='chase')endChase(false);standUp();", "if(dog.cart){cam.dist=dog.camDist||cam.dist;dog.cart=null;D.root.rotation.x=0}if(bbq.state==='chase')endChase(false);standUp();")

# HUD: context button
c = R(c, "$('#aSteal').hidden=!(bbq.inRange||picnic.inRange);",
         "$('#aSteal').hidden=!(bbq.inRange||picnic.inRange);{const a=ctxAction(),b=$('#aCtx');b.hidden=!a;if(a&&b.dataset.l!==a.l){b.dataset.l=a.l;b.firstChild.textContent=a.l}}")

# camera follows the cart
c = R(c, "if(dog.speed>0.6&&S.t-cam.lastDrag>1.5)cam.yaw+=angDiff(cam.yaw,dog.heading)*dt*(0.7+dog.speed*0.05);",
         "const csp=dog.cart?Math.abs(dog.cart.v)*1.3:dog.speed;if(csp>0.6&&S.t-cam.lastDrag>1.5)cam.yaw+=angDiff(cam.yaw,dog.heading)*dt*(0.7+csp*0.05);")
# engine hum while driving
c = R(c, "engF=42+bus.v*3}", "engF=42+bus.v*3}if(dog.cart){eng=Math.max(eng,0.03+Math.abs(dog.cart.v)*0.012);engF=60+Math.abs(dog.cart.v)*14}")

# quality survives level changes (silent)
c = R(c, "function lowerQuality(){", "function lowerQuality(silent){")
c = R(c, "sun.castShadow=false;toast('Switched to lighter graphics so the game runs smoothly.')}", "sun.castShadow=false;if(!silent)toast('Switched to lighter graphics so the game runs smoothly.')}")
c = R(c, "camera.updateProjectionMatrix();toast('Switched to the lightest graphics mode.')}", "camera.updateProjectionMatrix();if(!silent)toast('Switched to the lightest graphics mode.')}")

# frame loop can be cancelled
c = R(c, "let frameNo=0,perfT=0,", "let rafId=0,dead=false,frameNo=0,perfT=0,")
c = R(c, "function frame(now){if(lost)return;", "function frame(now){if(lost||dead)return;")
c = R(c, "requestAnimationFrame(frame);try{step(dt);", "rafId=requestAnimationFrame(frame);try{step(dt);")

# boot / snapshot / start / destroy
b0 = c.index('// ================= Boot =================')
b1 = c.index('})();', b0)
BOOT = r'''// ================= Boot =================
function snapshot(){return {level:WD.level,x:dog.x,z:dog.z,heading:dog.heading,hour:S.hour,day:S.day,hunger:S.hunger,energy:S.energy,happy:S.happy,points:S.points,name:S.name,todos:S.todos,fetchN:S.fetchN,digN:S.digN,found:S.found,started:S.started,
  stash:S.stash,stashN:S.stashN,stashDay:S.stashDay,patsDay:S.patsDay,swum:S.swum,carryHint:S.carryHint,sniffHinted:S.sniffHinted,cartHint:S.cartHint,quality,runLock}}
function start(){S.started=true;$('#start').hidden=true;sfx.init();renderTodos();
  if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name+'! No cars here: people zip around in golf carts.');toast('Find a parked golf cart and hop on, or catch the bus back to Ha Yeung.')}
  else{toast('Welcome home, '+S.name+'! Your food bowl is by the red front door.');toast('Uphill west is the bus stop on Clear Water Bay Road. The beach is about 500 m north-east. Check the map.')}}
function destroy(){dead=true;cancelAnimationFrame(rafId);AC.abort();clearTimeout(arcTimer);
  scene.traverse(o=>{if(o.geometry)o.geometry.dispose();const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[];for(const m of ms){for(const k in m){const t=m[k];if(t&&t.isTexture)t.dispose()}m.dispose()}});
  renderer.renderLists.dispose();renderer.dispose();try{renderer.forceContextLoss()}catch(e){}renderer.domElement.remove();
  $('#bubbles').textContent='';$('#pops').textContent='';toastEl.classList.remove('show');$('#chaseHud').hidden=true;$('#vignette').classList.remove('on');bigEl.hidden=true;
  $('#aSteal').hidden=true;$('#aCtx').hidden=true;knob.style.transform='';$('#arcade').className='';sfx.set(0,0,48)}
function boot(data,arrive){data=data||{};if(data.name)S.name=data.name;
  for(const k of ['hour','day','hunger','energy','happy','points','todos','fetchN','digN','found','stash','stashN','stashDay','patsDay','swum','carryHint','sniffHinted','cartHint'])if(data[k]!==undefined&&data[k]!==null)S[k]=data[k];
  if(!Array.isArray(S.stash))S.stash=[];S.stash.forEach((type,i)=>{if(ITYPES[type])stashPlace(addItem(type,BED.x,BED.z),i+1)});
  runLock=!!data.runLock;$('#aRun').classList.toggle('on',runLock);
  while(typeof data.quality==='number'&&quality>Math.max(0,data.quality))lowerQuality(true);
  if(arrive){// step out a few metres past the shelter and look back at the bus
    dog.x=PL.stop[0]+STOP.fx*6;dog.z=PL.stop[1]+STOP.fz*6;if(bldAt(dog.x,dog.z)||gridH(dog.x,dog.z)<0.3){dog.x=PL.stop[0];dog.z=PL.stop[1]}dog.heading=Math.atan2(-STOP.fx,-STOP.fz);dog.y=groundAt(dog.x,dog.z);
    bus.state='dwell';bus.dwell=6;bus.stopped=true;bus.v=0;bus.s=PL.stop_s;bus.g.visible=true;placeVehicle(bus)}
  else if(typeof data.x==='number'){dog.x=data.x;dog.z=data.z;dog.heading=data.heading||0;dog.y=groundAt(dog.x,dog.z)}
  cam.yaw=dog.heading;$('#nameLbl').textContent=S.name;$('#dogName').value=S.name;$('#plZh').textContent=WD.nameZh;$('#plName').textContent=WD.name;$('#map').setAttribute('aria-label',WD.name+' map');
  if(!arrive&&(innerWidth<700||innerHeight<820))$('#todoBox').open=false;
  renderTodos();updateHud();drawMap();camera.position.set(dog.x-Math.sin(dog.heading)*6,dog.y+3,dog.z-Math.cos(dog.heading)*6);
  const sb=$('#startBtn');
  if(!arrive){$('#startBtn').addEventListener('click',()=>{const n=$('#dogName').value.trim();S.name=n||'Mango';$('#nameLbl').textContent=S.name;start()});
    $('#dogName').addEventListener('keydown',e=>{if(e.key==='Enter')$('#startBtn').click()});sb.disabled=true;sb.textContent='Loading the village…'}
  setTimeout(()=>{if(dead)return;try{const hidden=[];scene.traverse(o=>{if(!o.visible){hidden.push(o);o.visible=true}});renderer.compile(scene,camera);renderer.shadowMap.needsUpdate=true;renderer.render(scene,camera);hidden.forEach(o=>o.visible=false)}catch(e){}
    if(arrive){S.started=true;$('#start').hidden=true;renderTodos();setTimeout(()=>fade(false),250);
      toast(WD.level==='db'?'Welcome to Discovery Bay! No cars here, just golf carts. Find a parked one (white dots on the map) and hop on.':'Back home in Ha Yeung. Your bed and bowl are by the red front door.');complete('bus')}
    else{sb.disabled=false;sb.textContent='Start the day';if(data.started)start()}},60);
  rafId=requestAnimationFrame(frame)}
boot(BOOT,ARRIVE);
return {snapshot,destroy};
}
try{if(window.claude&&window.claude.hot&&typeof window.claude.hot.snapshot==='function')window.claude.hot.snapshot(()=>LV?LV.snapshot():{})}catch(e){}
function first(data){data=data||{};LV=buildLevel(data.level==='db'?'db':'hy',data,false)}
const H0=window.claude&&window.claude.hot;if(H0&&typeof H0.ready==='function')H0.ready(first);else first((H0&&H0.data)||{});
'''
c = c[:b0] + BOOT + c[b1:]

db = json.load(open(G + 'data/discovery-bay/world.json', encoding='utf-8'))
dbs = json.dumps(db, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
out = head + hy + '</script>\n<script type="application/json" id="worldDataDB">' + dbs + c
open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(out)
print('ok', len(out))
