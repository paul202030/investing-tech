#!/usr/bin/env python3
# Multiplayer (light): friends' dogs via the artifact `room` capability (presence only, nothing stored).
import sys
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'MP.dogs' not in src, 'already transformed'
k = src.rfind('<script>'); head, c = src[:k], src[k:]

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

c = R(c, "let LV=null;\n", "let LV=null;\n// friends playing at the same time (room presence); the game works the same without it\nlet ROOM=null;try{if(window.claude&&typeof window.claude.use==='function')window.claude.use('room').then(r=>{ROOM=r}).catch(()=>{})}catch(e){}\n")

MP = r'''const villagers=[];const dbUpd=DBX?dbDecor(DBX):null;
// ================= Multiplayer: friends' dogs (presence ~10 times a second, nothing stored) =================
const MP={peers:[],dogs:new Map(),unsub:null,sendT:0,barkN:0};
function mpUpd(dt){if(!ROOM)return;
  if(!MP.unsub){MP.unsub=()=>{};try{MP.unsub=ROOM.onPeers(ch=>{MP.peers=ch.peers||[];for(const p of ch.joined||[]){const q=p.presence||{};if(!p.isMe&&q.lv===WD.level&&S.started)toast(String(q.n||'A friend').slice(0,14)+'\'s dog is here too!')}})||(()=>{})}catch(e){}}
  MP.sendT-=dt;if(MP.sendT<=0&&S.started){MP.sendT=0.1;try{const r=ROOM.presence({lv:WD.level,x:+dog.x.toFixed(2),z:+dog.z.toFixed(2),y:+dog.y.toFixed(2),h:+dog.heading.toFixed(3),s:dog.cart?'cart':dog.swimming?'swim':dog.posture,n:S.name,b:MP.barkN});if(r&&r.catch)r.catch(()=>{})}catch(e){}}
  const seen=new Set();
  for(const p of MP.peers){if(p.isMe)continue;const q=p.presence||{};if(q.lv!==WD.level||!isFinite(q.x)||!isFinite(q.z))continue;seen.add(p.peer);
    let o=MP.dogs.get(p.peer);if(!o){const D2=makeDog();scene.add(D2.root);o={D:D2,g:D2.root,headY:1.25,x:q.x,z:q.z,y:isFinite(q.y)?q.y:groundAt(q.x,q.z),h:q.h||0,ph:0,b:q.b,tagT:0,cart:null};MP.dogs.set(p.peer,o)}
    const px=o.x,pz=o.z,kk=Math.min(1,dt*10);o.x+=(q.x-o.x)*kk;o.z+=(q.z-o.z)*kk;o.y+=((isFinite(q.y)?q.y:groundAt(o.x,o.z))-o.y)*kk;o.h+=angDiff(o.h,q.h||0)*kk;
    const sp=Math.hypot(o.x-px,o.z-pz)/Math.max(dt,1e-3),st=q.s,sit=(st==='sit'||st==='cart')?1:0,lie=st==='lie'?1:0;o.ph+=dt*Math.min(sp*3,24);
    if(st==='cart'){if(!o.cart)o.cart=Object.assign(makeCart(0xf2f0e8),{v:0,pitch:0});o.cart.g.visible=true;o.cart.h=o.h;o.cart.x=o.x+Math.sin(o.h)*0.15+Math.cos(o.h)*0.22;o.cart.z=o.z+Math.cos(o.h)*0.15-Math.sin(o.h)*0.22;placeCart(o.cart)}else if(o.cart)o.cart.g.visible=false;
    const Dd=o.D,a=Math.sin(o.ph)*Math.min(1,sp/2.5)*0.6*(st==='cart'?0:1);Dd.root.position.set(o.x,o.y,o.z);Dd.root.rotation.set(0,o.h,0);
    Dd.legs.forEach((L,i)=>{const s=(i===0||i===3)?a:-a;if(L.front){L.up.rotation.x=s+sit*0.55-lie*1.45;L.kn.rotation.x=lie*0.1}else{L.up.rotation.x=s-sit*1.0-lie*1.3;L.kn.rotation.x=sit*1.7+lie*1.5}});
    Dd.hip.position.y=0.56-sit*0.3-lie*0.36;Dd.hip.rotation.x=-sit*0.55;Dd.neck.rotation.x=0.5+lie*0.7;Dd.head.rotation.x=-Dd.neck.rotation.x-Dd.hip.rotation.x+0.5+lie*0.15;
    Dd.tail.rotation.x=lerp(-1.15,-1.55,Math.max(sit,lie));Dd.tail.rotation.z=Math.sin(S.t*12)*0.5;
    o.tagT-=dt;if(o.tagT<=0){o.tagT=0.8;if(q.b!==o.b){o.b=q.b;say(o,'Woof! Woof!',1.2);if(Math.hypot(o.x-dog.x,o.z-dog.z)<30)sfx.bark()}else say(o,'🐾 '+String(q.n||'Friend').slice(0,14),1.0)}}
  for(const [id,o] of MP.dogs)if(!seen.has(id)){scene.remove(o.D.root);if(o.cart)scene.remove(o.cart.g);MP.dogs.delete(id)}}'''
c = R(c, "const villagers=[];const dbUpd=DBX?dbDecor(DBX):null;", MP)
c = R(c, "if(dbUpd)dbUpd(dt);updateItems(dt);", "if(dbUpd)dbUpd(dt);mpUpd(dt);updateItems(dt);")
c = R(c, "function doBark(){if(dog.napping)return;", "function doBark(){if(dog.napping)return;MP.barkN++;")
c = R(c, "if(police&&police.g.visible)dot(police.x,police.z,'#1d4ea0',4.5,true);", "if(police&&police.g.visible)dot(police.x,police.z,'#1d4ea0',4.5,true);for(const o of MP.dogs.values())dot(o.x,o.z,'#ffd27a',3.5,true);")
c = R(c, "function destroy(){dead=true;", "function destroy(){dead=true;try{if(MP.unsub)MP.unsub()}catch(e){}")

open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok')
