#!/usr/bin/env python3
# Jump out of a flying creation, free fall, open a paraglider, land.
import sys
G='/home/user/investing-tech/games/ha-yeung-dog-days/'
s=open(G+'index.html',encoding='utf-8').read();assert 'updatePara' not in s
def R(o,n):
    global s;assert s.count(o)==1,o[:100];s=s.replace(o,n)
PARA=r'''// jumping out of a flying machine: free fall, then a paraglider
let canopy=null;
function makeCanopy(){const g=new THREE.Group();const cols=[0xe8473c,0xf2c230,0x2d6fa5,0xf4f4f0,0x2f8f5a];
  for(let i=0;i<9;i++){const a=(i-4)*0.17;const m=new THREE.Mesh(new THREE.BoxGeometry(0.72,0.12,1.5),new THREE.MeshLambertMaterial({color:cols[i%5],side:THREE.DoubleSide}));m.position.set(Math.sin(a)*3.4,Math.cos(a)*3.4-3.4+4.2,0);m.rotation.z=-a;m.castShadow=true;g.add(m)}
  const lm=new THREE.LineBasicMaterial({color:0x444444});for(const sx of [-2.9,-1.2,1.2,2.9]){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([0,0.6,0,sx,4.1-Math.abs(sx)*0.18,0],3));g.add(new THREE.Line(geo,lm))}
  g.visible=false;scene.add(g);return g}
function jumpOut(){const k=dog.cart;if(!k)return;dog.cart=null;k.drop=true;dog.para={y:dog.y,vy:3,open:false,f:Math.min(12,k.v*0.5)};dog.heading=k.h;dog.posture='stand';D.root.rotation.set(0,dog.heading,0);
  arcade('ジャンプ!','JUMP!','run');sfx.arcadeStart();toast(mobile?'Tap Open chute to open your paraglider!':'Press X or Space to open your paraglider!')}
function openChute(){const P=dog.para;if(!P||P.open)return;P.open=true;if(!canopy)canopy=makeCanopy();canopy.visible=true;sfx.ding();popScore('PARAGLIDER!')}
function updatePara(dt){const P=dog.para;let th=0,st=0;
  if(keys.w||keys.arrowup)th+=1;if(keys.s||keys.arrowdown)th-=1;if(keys.d||keys.arrowright)st+=1;if(keys.a||keys.arrowleft)st-=1;if(joy.mag>0.12){th=-joy.y;st=joy.x}
  dog.heading-=st*(P.open?1.1:1.8)*dt;
  if(P.open){P.vy=lerp(P.vy,th<-0.05?-6:-2.6,Math.min(1,dt*2.5));P.f=lerp(P.f,th>0.05?11:th<-0.05?4:7,Math.min(1,dt*1.5))}
  else{P.vy=Math.max(-38,P.vy-9.8*dt);P.f=lerp(P.f,2+Math.max(0,th)*4,Math.min(1,dt*0.6))}
  let nx=dog.x+Math.sin(dog.heading)*P.f*dt,nz=dog.z+Math.cos(dog.heading)*P.f*dt;const b=bldAt(nx,nz);if(b&&P.y<b.top+0.3)[nx,nz]=pushOutB(nx,nz,0.6);
  dog.x=clamp(nx,X0+20,X1-20);dog.z=clamp(nz,Z0+20,Z1-20);P.y+=P.vy*dt;const water=gridH(dog.x,dog.z)<-0.5,gnd=water?-0.45:groundAt(dog.x,dog.z);
  if(P.y<=gnd){dog.para=null;if(canopy)canopy.visible=false;dog.y=gnd;cam.dist=dog.camDist||5.5;
    if(water){toast('Splash! A soft sea landing.');sfx.splash()}
    else if(P.open&&P.vy>-7){arcade('ナイス!','NICE LANDING','win');sfx.win();S.points+=100;popScore('+100');complete('para')}
    else{arcade('ドーン!','BONK!','lose');sfx.bonk();say(DOGTALK,'@#%! …I\'m okay!',2);S.happy=Math.max(0,S.happy-10);for(let i=0;i<12;i++)glow.emit(dog.x,dog.y+1,dog.z,(Math.random()-0.5)*3,2+Math.random()*2,(Math.random()-0.5)*3,0.8,C_GOLD,6)}
    D.root.position.set(dog.x,dog.y,dog.z);return}
  dog.y=P.y;dog.speed=Math.min(P.f,5);dog.posture=P.open?'sit':'stand';dog.swimming=false;if(dog.barkT>0)dog.barkT-=dt;
  D.root.position.set(dog.x,dog.y,dog.z);D.root.rotation.set(P.open?0:-0.35,dog.heading,P.open?-st*0.2:Math.sin(S.t*6)*0.15);
  cam.dist+=(Math.max(dog.camDist||5.5,P.open?9:7)-cam.dist)*Math.min(1,dt*2);
  if(canopy&&P.open){canopy.position.set(dog.x,dog.y+0.4,dog.z);canopy.rotation.set(0,dog.heading+Math.PI/2,st*0.25)}}
// an empty plane glides down by itself and parks where it lands
function dropUpd(k,dt){k.alt=Math.max(0,k.alt-(k.alt>1?3.5:1)*dt);k.v=Math.max(0,k.v-(k.alt>0.2?1:6)*dt);const fx=Math.sin(k.h),fz=Math.cos(k.h);const nx=k.x+fx*k.v*dt,nz=k.z+fz*k.v*dt;const b=bldAt(nx+fx*1.5,nz+fz*1.5);
  if(b&&Math.max(groundAt(nx,nz),0)+k.alt<b.top+0.5)k.v=0;else{k.x=clamp(nx,X0+20,X1-20);k.z=clamp(nz,Z0+20,Z1-20)}
  k.y=Math.max(groundAt(k.x,k.z),0)+k.alt;k.g.rotation.order='YXZ';k.g.position.set(k.x,k.y,k.z);k.g.rotation.set(0,k.h-Math.PI/2,k.alt>0.5?-0.12:0);if(k.alt<=0&&k.v<=0){k.drop=false;k.v=0}}
function rideFly(dt){'''
R("function rideFly(dt){",PARA)
R("function updateDog(dt){if(dog.cart){rideCart(dt);return}","function updateDog(dt){if(dog.cart){rideCart(dt);return}if(dog.para){updatePara(dt);return}")
R("if(dog.cart)return Math.abs(dog.cart.v)<1.2&&","if(dog.cart&&dog.cart.fly&&dog.cart.alt>4)return {l:'Jump!',f:jumpOut};if(dog.para)return dog.para.open?null:{l:'Open chute',f:openChute};\n  if(dog.cart)return Math.abs(dog.cart.v)<1.2&&")
R("||!!dog.cart||!!S.leaving;","||!!dog.cart||!!dog.para||!!S.leaving;")
R("function doBark(){if(dog.napping)return;","function doBark(){if(dog.para&&!dog.para.open){openChute();return}if(dog.napping)return;")
R("if(dog.cart){cam.dist=dog.camDist||cam.dist;dog.cart=null;D.root.rotation.x=0}","if(dog.cart){cam.dist=dog.camDist||cam.dist;dog.cart=null;D.root.rotation.x=0}if(dog.para){dog.para=null;if(canopy)canopy.visible=false}")
R("['booth','Try your luck at a player\\'s game booth']]","['booth','Try your luck at a player\\'s game booth'],['para','Jump out of a flying machine and paraglide down']]")
R("function genUpd(dt){genListen();","function genUpd(dt){genListen();for(const r of rides)if(r.drop&&dog.cart!==r)dropUpd(r,dt);")
open(sys.argv[1] if len(sys.argv)>1 else G+'index.html','w',encoding='utf-8').write(s);print('ok')
