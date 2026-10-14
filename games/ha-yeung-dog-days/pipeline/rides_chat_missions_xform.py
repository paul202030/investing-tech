#!/usr/bin/env python3
# Rideable/flying/talking creations, wider effects, NPC chat, Auntie's Claude-written missions, bichon frise.
import sys
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'rideFly' not in src, 'already transformed'
k = src.rfind('<script>'); head, c = src[:k], src[k:]

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

# ---------------- head
CSS = '''#chatBox,#missionBox{z-index:6}
#chatLog{max-height:38vh;overflow:auto;display:grid;gap:6px;font-size:14px;line-height:1.35}
#chatLog .me{justify-self:end;background:#ffe9b8;border-radius:10px;padding:5px 9px;max-width:85%}
#chatLog .them{justify-self:start;background:#fffdf6;border:1px solid rgba(28,38,38,.12);border-radius:10px;padding:5px 9px;max-width:85%}
#chatIn{font:inherit;font-size:16px;padding:10px;border:2px solid rgba(28,38,38,.2);border-radius:8px;background:#fffdf6;color:var(--ink)}
#chatRow{display:grid;grid-template-columns:1fr auto;gap:8px}
#chatSend{font-family:var(--display);font-weight:800;border:none;border-radius:10px;padding:0 16px;background:var(--green);color:#fff;cursor:pointer}
#missionHud{position:fixed;left:50%;top:calc(110px + env(safe-area-inset-top,0px));transform:translateX(-50%);z-index:3;background:#1a1a2e;border:3px solid #ffe53b;box-shadow:4px 4px 0 #e8173c;padding:7px 12px;color:#fff;pointer-events:none;max-width:min(460px,calc(100vw - 32px));text-align:center}
#missionHud[hidden]{display:none!important}
#missionHud .mT{font-family:'Press Start 2P',monospace;font-size:11px;color:#ffe53b}
#missionHud .mS{font-family:var(--body);font-size:14px;margin-top:4px}
.breeds{display:flex;gap:14px;font-weight:400;color:var(--ink);font-size:14px}
</style>'''
head = R(head, '</style>', CSS)
head = R(head, '<label class="nameRow" for="dogName">', '<div class="nameRow">Breed<div class="breeds"><label><input type="radio" name="breed" value="golden" checked> Golden retriever</label><label><input type="radio" name="breed" value="bichon"> Bichon frise</label></div></div>\n    <label class="nameRow" for="dogName">')
head = R(head, '<div id="arcade" aria-hidden="true">', '''<div id="chatBox" class="lost" hidden><div class="mapCard"><div class="mapHead"><b id="chatTitle">Chat</b><button id="chatClose" type="button">Close</button></div>
<div id="chatLog" aria-live="polite"></div><div id="chatRow"><input id="chatIn" maxlength="140" placeholder="What does your dog say?" autocomplete="off"><button id="chatSend" type="button">Send</button></div>
<p class="small" id="chatNote">Replies come from Claude, using your own Claude account.</p></div></div>
<div id="missionHud" hidden><div class="mT"></div><div class="mS"></div></div>
<div id="arcade" aria-hidden="true">''')
head = R(head, '<p class="small">Describe one thing to add to this village. Claude builds it using your own Claude account, and it stays here for every player to find.</p>',
         '<p class="small">Describe anything to add to this village: something to carry, something to drive or fly, or a character to talk to. Claude builds it using your own Claude account, and it stays here for every player to find.</p>')
head = R(head, '<button type="button" class="chip">a lucky golden cat</button>', '<button type="button" class="chip">a little red plane I can fly</button><button type="button" class="chip">a gossiping pigeon who knows everyone</button>')

# ---------------- bichon frise
c = R(c, "function makeDog(){\n  const fur=mat(0xd59a42),furL=mat(0xecc488),furF=mat(0xf4d9a6),furD=mat(0xb8792e),",
         "function makeDog(breed){const B=breed==='bichon',K=B?0.62:1;\n  const fur=mat(B?0xf6f2ea:0xd59a42),furL=mat(B?0xffffff:0xecc488),furF=mat(B?0xfbf7ef:0xf4d9a6),furD=mat(B?0xece5d8:0xb8792e),")
c = R(c, "const hip=new THREE.Group();hip.position.set(0,0.56,-0.36);root.add(hip);", "const hip=new THREE.Group();hip.position.set(0,0.56*K,-0.36*K);hip.scale.setScalar(K);root.add(hip);")
c = R(c, "  sph(furL,0.088,0.078,0.17,0,-0.02,0.15,head);         // long muzzle", "  if(B){sph(furL,0.08,0.07,0.09,0,-0.02,0.1,head);sph(furL,0.17,0.17,0.13,0,0.07,-0.03,head);sph(fur,0.3,0.3,0.5,0,0.05,0.32,hip)}else sph(furL,0.088,0.078,0.17,0,-0.02,0.15,head);         // muzzle (bichon: short, with a pom-pom head and fluffy body)")
c = R(c, "  sph(dark,0.045,0.038,0.035,0,0.02,0.31,head);         // nose", "  sph(dark,0.045,0.038,0.035,0,0.02,B?0.19:0.31,head);         // nose")
c = R(c, "  return {root,hip,neck,head,jaw,tongue,eyes,ears,legs,tail,tsegs}}", "  return {root,hip,neck,head,jaw,tongue,eyes,ears,legs,tail,tsegs,k:K,tailUp:B?0.9:0,breed:B?'bichon':'golden'}}")
c = R(c, "const D=makeDog();scene.add(D.root);", "let D=makeDog(BOOT&&BOOT.breed);scene.add(D.root);")
c = R(c, "D.hip.position.y=0.56-P.sit*0.3-P.lie*0.36-P.swim*0.05+bob+Math.sin(S.t*(dog.napping?1.5:3))*0.006;", "D.hip.position.y=(0.56-P.sit*0.3-P.lie*0.36-P.swim*0.05+bob+Math.sin(S.t*(dog.napping?1.5:3))*0.006)*D.k;")
c = R(c, "D.tail.rotation.x=lerp(-1.15,-1.55,Math.max(P.sit,P.lie,P.swim));", "D.tail.rotation.x=lerp(-1.15,-1.55,Math.max(P.sit,P.lie,P.swim))+D.tailUp;")
c = R(c, "const D2=makeDog();", "const D2=makeDog(q.br);")
c = R(c, "Dd.hip.position.y=0.56-sit*0.3-lie*0.36;", "Dd.hip.position.y=(0.56-sit*0.3-lie*0.36)*Dd.k;")
c = R(c, "s:dog.cart?'cart':dog.swimming?'swim':dog.posture,n:S.name,", "s:dog.cart?'cart':dog.swimming?'swim':dog.posture,n:S.name,br:S.breed,")
c = R(c, "const S={stash:[],started:false,", "const S={stash:[],breed:(BOOT&&BOOT.breed)||'golden',started:false,")
c = R(c, "quality,runLock}}", "quality,runLock,breed:S.breed}}")
c = R(c, "'cartHint','villageHint'])", "'cartHint','villageHint','breed'])")
c = R(c, "$('#startBtn').addEventListener('click',()=>{const n=$('#dogName').value.trim();",
         "$('#startBtn').addEventListener('click',()=>{const br=(document.querySelector('input[name=breed]:checked')||{}).value==='bichon'?'bichon':'golden';if(br!==D.breed){const r=D.root;scene.remove(r);D=makeDog(br);D.root.position.copy(r.position);D.root.rotation.copy(r.rotation);scene.add(D.root)}S.breed=br;const n=$('#dogName').value.trim();")

# ---------------- rideable creations
c = R(c, "const carts=PL.carts.map((p,i)=>Object.assign(makeCart(CART_COLS[i%6]),{x:p[0],z:p[1],h:p[2],v:0,y:0,pitch:0,dist:0}));carts.forEach(placeCart);",
         "const carts=PL.carts.map((p,i)=>Object.assign(makeCart(CART_COLS[i%6]),{x:p[0],z:p[1],h:p[2],v:0,y:0,pitch:0,dist:0}));carts.forEach(placeCart);const rides=[];")
c = R(c, "for(const k of carts){const d=Math.hypot(k.x-dog.x,k.z-dog.z);if(d<bd)", "for(const k of carts.concat(rides)){const d=Math.hypot(k.x-dog.x,k.z-dog.z);if(d<bd)")
c = R(c, "for(const k of carts){const ex=nx-k.x", "for(const k of carts.concat(rides)){const ex=nx-k.x")
c = R(c, "function rideCart(dt){const k=dog.cart;let th=0,st=0;", "function rideCart(dt){const k=dog.cart;if(k.fly)return rideFly(dt);let th=0,st=0;")
c = R(c, "k.g.updateMatrixWorld();const sp=k.g.localToWorld(v3.set(-0.15,0.78,0.22));", "k.g.updateMatrixWorld();const se=k.seat||{x:-0.15,y:0.78,z:0.22};const sp=k.g.localToWorld(v3.set(se.x,se.y,se.z));")
c = R(c, "if(dog.cart)return Math.abs(dog.cart.v)<1.2?{l:'Hop off',f:hopOff}:null;", "if(dog.cart)return Math.abs(dog.cart.v)<1.2&&!(dog.cart.alt>0.6)&&gridH(dog.cart.x,dog.cart.z)>0.2?{l:'Hop off',f:hopOff}:null;")
c = R(c, "if(S.started&&dog.cart&&Math.abs(dog.cart.v)>5)", "if(S.started&&dog.cart&&!dog.cart.fly&&Math.abs(dog.cart.v)>5)")
c = R(c, "function hopOn(k){", "function hopOn(k){if(k.gen)toast((k.fly?'Hold W to take off and climb, let go to glide, S to dive and land, A / D to steer, Shift for turbo. ':'')+'✨ '+k.gen.name+', made by '+k.by+'.');")
c = R(c, "dog.cart?Math.round(Math.abs(dog.cart.v)*3.6)+' km/h'", "dog.cart?Math.round(Math.abs(dog.cart.v)*3.6)+' km/h'+(dog.cart.fly?' · '+Math.round(dog.cart.alt)+' m up':'')")

# wider creation spec: ride, talk, more effects
s0 = c.index("const GSH=['box','sphere','cyl','cone']"); s1 = c.index("function genMake(spec,g){")
SPEC = r'''const GSH=['box','sphere','cyl','cone'],GMOVE=['none','bounce','float','spin'],GFX=['none','giant','tiny','zoom','rain','party','fireworks','teleport','night','day'],GRIDE=['none','drive','fly'];
function gStr(v,n){return typeof v==='string'?v.replace(/[\u0000-\u001f<>]/g,'').trim().slice(0,n):''}
function cleanSpec(s){if(!s||typeof s!=='object')return null;const num=(v,a,b,d)=>{v=+v;return isFinite(v)?clamp(v,a,b):d};
  const ride=GRIDE.includes(s.ride)?s.ride:'none',talk=gStr(s.talk,240),big=ride!=='none'||!!talk,XR=big?2.2:0.9,SR=big?4:1.6,YR=big?3:1.7;
  const parts=(Array.isArray(s.parts)?s.parts:[]).slice(0,18).map(p=>p&&GSH.includes(p.s)&&/^#[0-9a-fA-F]{6}$/.test(p.c)?{s:p.s,c:p.c,x:num(p.x,-XR,XR,0),y:num(p.y,0,YR,0.2),z:num(p.z,-XR,XR,0),
    sx:num(p.sx,0.02,SR,0.2),sy:num(p.sy,0.02,SR,0.2),sz:num(p.sz,0.02,SR,0.2),rx:num(p.rx,-180,180,0),ry:num(p.ry,-180,180,0),rz:num(p.rz,-180,180,0)}:null).filter(Boolean);
  if(!parts.length)return null;const name=gStr(s.name,28)||'Mystery thing';const st=s.seat&&typeof s.seat==='object'?s.seat:{};
  return {name,zh:gStr(s.zh,8),label:gStr(s.label,40)||('a '+name),line:gStr(s.line,90),move:GMOVE.includes(s.move)?s.move:'none',effect:GFX.includes(s.effect)?s.effect:'none',ride,talk:ride==='none'?talk:'',
    hello:gStr(s.hello,90),seat:{x:num(st.x,-XR,XR,0),y:num(st.y,0.2,YR,0.8),z:num(st.z,-XR,XR,0)},parts}}
'''
c = c[:s0] + SPEC + c[s1:]
c = R(c, "GEN.ids.add(id);\n  const x=clamp(+d.x,X0+20,X1-20),z=clamp(+d.z,Z0+20,Z1-20);",
         "GEN.ids.add(id);\n  const x=clamp(+d.x,X0+20,X1-20),z=clamp(+d.z,Z0+20,Z1-20);if(spec.ride!=='none'||spec.talk){genThing(spec,x,z,gStr(d.by,14)||'someone');return null}")

THING = r'''const genFolk=[];
// vehicles and characters made by players: driven like a golf cart, flown, or talked to
function genThing(spec,x,z,by){const g=new THREE.Group();genMake(spec,g);scene.add(g);let top=0.5;for(const p of spec.parts)top=Math.max(top,p.y+p.sy/2);
  if(spec.ride!=='none'){const v={g,body:g,x,z,h:Math.random()*6.28,v:0,y:0,pitch:0,dist:0,alt:0,gen:spec,by,fly:spec.ride==='fly',seat:spec.seat,tag:{g,headY:top+0.5},tagT:Math.random()};placeCart(v);rides.push(v);GEN.items.push(v);return v}
  const f={g,gen:spec,by,headY:top+0.3,x,z,tag:{g,headY:top+0.4},tagT:Math.random(),folk:true,ph:Math.random()*6,patCool:0,arms:[{rotation:{x:0}},{rotation:{x:0}}],legs:[]};
  g.position.set(x,groundAt(x,z),z);g.rotation.y=Math.random()*6.28;softColliders.push([x,z,Math.min(1.6,Math.max(0.5,top*0.4))]);genFolk.push(f);GEN.items.push(f);return f}
function rideFly(dt){const k=dog.cart;let th=0,st=0;
  if(!S.leaving){if(keys.w||keys.arrowup)th+=1;if(keys.s||keys.arrowdown)th-=1;if(keys.d||keys.arrowright)st+=1;if(keys.a||keys.arrowleft)st-=1;if(joy.mag>0.12){th=-joy.y;st=joy.x}}
  const turbo=keys.shift||runLock||joy.mag>0.95,top=turbo?40:28;
  if(th>0.05)k.v=Math.min(top,k.v+(turbo?10:7)*th*dt);else if(th<-0.05)k.v=Math.max(0,k.v-10*dt);else if(k.alt<0.3)k.v=Math.max(0,k.v-5*dt);else k.v=Math.max(8,k.v-1*dt);
  let climb=th>0.05&&k.v>10?4.5:th<-0.05?-6:-1.5;if(k.alt<=0.01&&climb<0)climb=0;k.alt=clamp(k.alt+climb*dt,0,140);
  k.h-=st*1.4*dt*(k.alt>0.5?1:clamp(k.v/3,0,1));const fx=Math.sin(k.h),fz=Math.cos(k.h);const n=Math.max(1,Math.ceil(k.v*dt/0.8));
  for(let i=0;i<n;i++){let nx=k.x+fx*k.v*dt/n,nz=k.z+fz*k.v*dt/n;const b=bldAt(nx+fx*1.5,nz+fz*1.5);const base=Math.max(groundAt(nx,nz),0);
    if(b&&base+k.alt<b.top+0.5){sfx.bonk();say(DOGTALK,'Bonk!',0.9);k.v*=0.3;k.alt+=1.5;break}k.x=clamp(nx,X0+20,X1-20);k.z=clamp(nz,Z0+20,Z1-20)}
  k.dist+=k.v*dt;const base=Math.max(groundAt(k.x,k.z),0);k.y=base+k.alt;const pit=k.alt>0.3?clamp(climb/12,-0.4,0.4):0;
  k.g.rotation.order='YXZ';k.g.position.set(k.x,k.y,k.z);k.g.rotation.set(k.alt>0.5?st*0.45:0,k.h-Math.PI/2,pit);k.pitch=pit;
  cam.dist+=(Math.max(dog.camDist||5.5,9+k.v*0.15)-cam.dist)*Math.min(1,dt*1.5);
  k.g.updateMatrixWorld();const se=k.seat||{x:0,y:0.8,z:0};const sp=k.g.localToWorld(v3.set(se.x,se.y,se.z));dog.x=sp.x;dog.z=sp.z;dog.y=sp.y;dog.heading=k.h;dog.posture='sit';dog.speed=0;dog.sitT=0;dog.swimming=false;
  if(dog.barkT>0)dog.barkT-=dt;D.root.position.set(dog.x,dog.y,dog.z);D.root.rotation.set(-pit,dog.heading,0);if(k.alt>20)complete('fly')}
'''
c = R(c, "function genListen(){", THING + "function genListen(){")
# effects
c = R(c, "  else if(s.effect==='party'){", "  else if(s.effect==='fireworks'){arcade('はなび!','FIREWORKS!','clear');sfx.tada();for(let b=0;b<6;b++){const cx=dog.x+(Math.random()-0.5)*30,cz=dog.z+(Math.random()-0.5)*30,cy=dog.y+18+Math.random()*12,col=new THREE.Color().setHSL(Math.random(),0.9,0.6);for(let i=0;i<26;i++){const a=Math.random()*6.28,e=Math.random()*3.14-1.57,sp=5+Math.random()*4;glow.emit(cx,cy,cz,Math.cos(a)*Math.cos(e)*sp,Math.sin(e)*sp,Math.sin(a)*Math.cos(e)*sp,1.6,col,2)}}}\n  else if(s.effect==='teleport'){const pl=pick(PLACES);setTimeout(()=>{if(!dead){dropItem();travelTo(pl[1],pl[2])}},600);arcade('ワープ!','WARP!','run')}\n  else if(s.effect==='night'||s.effect==='day'){S.hour=s.effect==='night'?21.5:12;toast(s.effect==='night'?'Suddenly it\\'s evening!':'Suddenly it\\'s midday!')}\n  else if(s.effect==='party'){")
# tags & idle anim for vehicles and characters; folk greet
c = R(c, "      it.tagT-=dt;if(it.tagT<=0){it.tagT=1;if(Math.hypot(it.x-dog.x,it.z-dog.z)<16)say(it.tag,'✨ '+it.T.gen.name,1.1)}}}}",
         "      it.tagT-=dt;if(it.tagT<=0){it.tagT=1;if(Math.hypot(it.x-dog.x,it.z-dog.z)<16)say(it.tag,'✨ '+it.T.gen.name,1.1)}}\n    else if((it.fly!==undefined||it.folk)&&dog.cart!==it){it.tagT-=dt;if(it.tagT<=0){it.tagT=1;const d=Math.hypot(it.x-dog.x,it.z-dog.z);if(d<16)say(it.tag,(it.folk&&d<5&&it.gen.hello&&!it.greeted?(it.greeted=true,it.gen.hello):'✨ '+it.gen.name),it.folk&&d<5?3:1.1)}if(it.folk&&it.gen.move!=='none'){it.ph+=dt;if(it.gen.move==='spin')it.g.rotation.y+=dt;else it.g.position.y=groundAt(it.x,it.z)+(it.gen.move==='float'?0.4+Math.sin(it.ph*1.5)*0.15:Math.abs(Math.sin(it.ph*3))*0.25)}}}}")
c = R(c, "Each part: {\"s\": \"box\"|\"sphere\"|\"cyl\"|\"cone\"", "Each part: {\"s\": \"box\"|\"sphere\"|\"cyl\"|\"cone\"")  # sanity
c = R(c, "'effect = what happens to the dog that picks it up: giant or tiny dog for 20 s, zoom = super speed for 15 s, rain = copies fall from the sky, party = everyone nearby cheers. Choose what fits the idea; \"none\" is fine.\\n'+",
         "'effect = what happens to the dog that picks it up: giant or tiny dog for 20 s, zoom = super speed for 15 s, rain = copies fall from the sky, party = everyone nearby cheers, fireworks, teleport = whisks the dog somewhere else in the village, night or day = changes the time. Choose what fits; \"none\" is fine.\\n'+\n  'If the idea is a vehicle, add \"ride\": \"drive\" (cars, boats on wheels, scooters) or \"fly\" (planes, flying carpets, dragons), build it up to 4 m long with its FRONT pointing towards +x, and add \"seat\": {\"x\",\"y\",\"z\"} = where the dog sits on top of it. '+\n  'If the idea is a creature or person to talk to, add \"talk\": \"its personality in one or two sentences\" and \"hello\": \"what it says when the dog walks up (max 80 chars)\", up to 3 m tall. Otherwise leave ride and talk out: it is a small object the dog can carry.\\n'+")
c = R(c, "'The whole object must fit inside 1.6 x 1.6 x 1.6 m. Use bright, friendly colours.'}", "'Small carryable objects must fit inside 1.6 x 1.6 x 1.6 m; vehicles and characters inside 4 x 3 x 4 m. Use 3 to 18 parts and bright, friendly colours.'}")

# ---------------- chat + missions
CHAT = r'''// ================= Chat with people, and Auntie Wong's missions (both written by Claude on the player's own account) =================
const PERSONAS=()=>[[granny,'Granny Chan','婆婆','an 82-year-old village grandmother on a red plastic stool; adores the dog, worries it is too thin, tells little stories about the old village days and mixes simple Cantonese words into her English'],
  [auntie,'Auntie Wong','黃姨',(WD.level==='db'?'runs the café at the plaza':'runs the little village store')+'; bossy, loving, loves gossip and dim sum, gives the dog cheeky missions'],
  [fisher,'Uncle Lam','林伯','the quiet fisherman by the water; dry jokes, patient, talks about fish, tides and the old days'],
  [bbq.uncle,'BBQ Uncle','燒烤叔','grills giant tomahawk steaks for his friends and is still a bit salty that the dog keeps stealing them'],
  [kid,'Ming','明仔','a 9-year-old boy who lives for playing fetch on the beach']].concat(villagers.map(v=>[v,'Ate Joy','','a cheerful Filipina helper enjoying her day off with friends by the water; mixes Tagalog and English'])).concat(genFolk.map(f=>[f,f.gen.name,f.gen.zh,f.gen.talk+' (created by a player called '+f.by+')']));
const CH={who:null,log:new Map(),busy:false,treatAt:new Map()};const chBox=$('#chatBox'),chLog=$('#chatLog'),chIn=$('#chatIn');
function chatTarget(){let best=null,bd=3.6;for(const pr of PERSONAS()){const p=pr[0];if(!p||!p.g||!p.g.visible)continue;const pp=p.g.position;const d=Math.hypot(pp.x-dog.x,pp.z-dog.z);if(d<bd){bd=d;best=pr}}return best}
function chatLine(cls,t){const d=document.createElement('div');d.className=cls;d.textContent=t;chLog.appendChild(d);chLog.scrollTop=chLog.scrollHeight}
function openChat(pr){CH.who=pr;$('#chatTitle').textContent='Chat with '+pr[1]+(pr[2]?' '+pr[2]:'');chLog.textContent='';for(const [cl,t] of (CH.log.get(pr[1])||[]))chatLine(cl,t);
  $('#chatNote').textContent=SAMP?'Replies come from Claude, using your own Claude account.':'Chatting needs Claude: open the game signed in to claude.ai.';chBox.hidden=false;setTimeout(()=>chIn.focus(),50)}
function closeChat(){chBox.hidden=true;chIn.blur()}
async function sendChat(){const msg=gStr(chIn.value,140),pr=CH.who;if(!msg||!pr||CH.busy)return;if(!SAMP){$('#chatNote').textContent='Chatting needs Claude: open the game signed in to claude.ai.';return}
  chIn.value='';chatLine('me',msg);const log=CH.log.get(pr[1])||[];log.push(['me',msg]);CH.log.set(pr[1],log);CH.busy=true;$('#chatSend').disabled=true;$('#chatNote').textContent=pr[1]+' is thinking…';
  const hist=log.slice(-9,-1).map(([cl,t])=>(cl==='me'?'Dog: ':pr[1]+': ')+t).join('\n');const h=Math.floor(S.hour),m=Math.floor((S.hour-h)*60);
  const prompt='You are '+pr[1]+', '+pr[3]+', in '+WD.name+', Hong Kong, inside a cute browser game. A dog called '+S.name+' (a '+(S.breed==='bichon'?'bichon frise':'golden retriever')+') is talking to you, and you understand dogs perfectly. It is '+String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+'.'+
    (dog.item?' The dog is carrying '+dog.item.T.label+'.':'')+' Stay in character, be warm and funny, 1-2 short sentences (max 160 characters). Keep it wholesome; no real brands or real people.\n'+(hist?'Conversation so far:\n'+hist+'\n':'')+'Dog: "'+msg.replace(/"/g,"'")+'"\n'+
    'Reply with ONLY JSON: {"reply": "...", "action": "none" | "treat" | "pat"} (treat = you give the dog a small snack, only now and then; pat = you pat the dog).';
  try{const r=await SAMP.json(prompt,{modelTier:'quick',cache:false});const reply=gStr(r&&r.reply,200)||'…';chatLine('them',reply);log.push(['them',reply]);if(log.length>16)log.splice(0,log.length-16);say(pr[0],reply,5);
    const act=r&&r.action;if(act==='treat'&&!busy()&&!dog.cart&&(S.t-(CH.treatAt.get(pr[1])||-1e9))>120){CH.treatAt.set(pr[1],S.t);serveTart();hearts(8)}else if(act==='pat'){hearts(10);S.happy=Math.min(100,S.happy+8);pr[0].patT=2}
    if(pr[0]===granny)complete('chat');$('#chatNote').textContent='Replies come from Claude, using your own Claude account.'}
  catch(e){const code=e&&e.code;$('#chatNote').textContent=code==='not_granted'?'Claude wasn\'t allowed, so they can\'t answer.':code==='rate_limited'?'Your Claude account is busy or out of messages. Try again later.':'They didn\'t hear you. Try again.'}
  finally{CH.busy=false;$('#chatSend').disabled=false}}
$('#chatClose').addEventListener('click',closeChat);$('#chatSend').addEventListener('click',()=>sendChat());chIn.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();sendChat()}else if(e.key==='Escape')closeChat()});
chBox.addEventListener('pointerdown',e=>{if(e.target===chBox)closeChat()});
// missions
const MIS={cur:null,busy:false,recent:[]};const misMk=mkMarker(0xffe53b,3.2);const misHud=$('#missionHud');
const MIS_ITEMS=['stick','stone','shell','cone','branch'];
function misPeople(){return {'granny chan':granny,'auntie wong':auntie,'uncle lam':fisher,'fisherman':fisher,'ming':kid,'bbq uncle':bbq.uncle}}
function misTarget(name){name=String(name||'').toLowerCase().trim();if(!name)return null;const pp=misPeople();if(pp[name])return {p:pp[name],name};for(const pl of PLACES){const k=pl[0].toLowerCase();if(k===name||k.split(' · ')[0]===name)return {x:pl[1],z:pl[2],name:pl[0]}}return null}
function misPos(t){return t.p?[t.p.g.position.x,t.p.g.position.z]:[t.x,t.z]}
function misNear(t,r){const p=misPos(t);return Math.hypot(p[0]-dog.x,p[1]-dog.z)<r}
function misClean(m){if(!m||!Array.isArray(m.steps))return null;const db=WD.level==='db',steps=[];
  for(const s of m.steps.slice(0,3)){if(!s)continue;const text=gStr(s.text,70);let st=null;
    if(s.type==='goto'){const t=misTarget(s.to);if(t)st={type:'goto',t}}else if(s.type==='drive'&&db&&carts.length){const t=misTarget(s.to);if(t&&!t.p)st={type:'drive',t}}
    else if(s.type==='deliver'&&MIS_ITEMS.includes(s.item)){const t=misTarget(s.to);if(t)st={type:'deliver',item:s.item,t}}
    else if(s.type==='bark'||s.type==='sit'){const t=misTarget(s.type==='bark'?s.at:s.by);if(t&&t.p)st={type:s.type,t}}
    else if(s.type==='dig')st={type:'dig'};else if(s.type==='steal'&&(s.from==='bbq'||s.from==='picnic'))st={type:'steal',from:s.from};else if(s.type==='police'&&db&&police)st={type:'police'};
    if(st){st.text=text||st.type;steps.push(st)}}
  if(!steps.length)return null;return {title:gStr(m.title,30)||'A little job',brief:gStr(m.brief,160),win:gStr(m.win,110),lose:gStr(m.lose,110),time:clamp(+m.time||120,60,300),reward:Math.round(clamp(+m.reward||300,100,800)),steps}}
async function askMission(){if(MIS.cur||MIS.busy)return;if(!SAMP){say(auntie,'Aiya, I need Claude to think of a job for you. Sign in to claude.ai first!',4);return}
  MIS.busy=true;say(auntie,pick(['Wait ah, let me think…','Hmm… I have just the job for you.','Come, come, listen to Auntie…']),3);
  const db=WD.level==='db',places=PLACES.map(p=>p[0]).join(', '),people='Granny Chan, Auntie Wong, Uncle Lam, Ming, BBQ Uncle';
  const prompt='You are Auntie Wong, a bossy but loving Chinese auntie in '+WD.name+', Hong Kong, who gives a dog called '+S.name+' cheeky GTA-style missions in a cute browser game. Funny and harmless: no real violence, nothing gross, no real brands or real people.\n'+
    'Write ONE mission as JSON only: {"title": "max 30 chars", "brief": "what Auntie says to start it, max 140 chars, may mix in a few Cantonese words", "time": seconds 60-240, "reward": 100-800, "steps": [1 to 3 steps in order], "win": "what she says on success, max 100 chars", "lose": "what she says on failure, max 100 chars"}\n'+
    'Each step is one of:\n {"type":"goto","to":PLACE,"text":...}\n {"type":"deliver","item":"stick"|"stone"|"shell"|"cone"|"branch","to":PLACE or PERSON,"text":...} (the dog finds that item lying around and carries it there)\n {"type":"bark","at":PERSON,"text":...}\n {"type":"sit","by":PERSON,"text":...}\n {"type":"dig","text":...} (dig up a buried treasure; sniffing helps)\n {"type":"steal","from":"bbq"|"picnic","text":...} (snatch food and get away)\n'+
    (db?' {"type":"drive","to":PLACE,"text":...} (in a golf cart)\n {"type":"police","text":...} (outrun a police car in a golf cart)\n':'')+
    'PLACE is exactly one of: '+places+'. PERSON is exactly one of: '+people+'. "text" is the short instruction shown on screen (max 60 chars).\n'+(MIS.recent.length?'Make it different from these recent missions: '+MIS.recent.join('; ')+'.\n':'')+'Be creative, mix the step types, and give it a story.';
  try{const m=misClean(await SAMP.json(prompt,{modelTier:'quick',cache:false}));if(!m)throw {code:'bad_shape'};MIS.cur=Object.assign(m,{i:0,t:m.time,stepAt:S.t});MIS.recent.push(m.title);if(MIS.recent.length>5)MIS.recent.shift();
    arcade('ミッション開始!','MISSION START','run');sfx.arcadeStart();say(auntie,m.brief||m.title,6);toast('Mission: '+m.title+'. '+m.steps[0].text)}
  catch(e){const code=e&&e.code;say(auntie,code==='not_granted'?'No Claude, no mission. Next time, ah!':code==='rate_limited'?'Auntie\'s brain is tired today (your Claude account is out of messages). Later!':'Aiya, I forgot what I wanted. Ask me again!',4)}
  finally{MIS.busy=false}}
function misNext(){const m=MIS.cur;m.i++;m.stepAt=S.t;sfx.ding();popScore('OK!');if(m.i>=m.steps.length){S.points+=m.reward;popScore('+'+m.reward);arcade('ミッションクリア!','MISSION CLEAR','win');sfx.win();shake();complete('mission');say(auntie,m.win||'好嘢! Good dog!',5);toast('Mission complete: '+m.title+' (+'+m.reward+')');MIS.cur=null}else toast('Next: '+m.steps[m.i].text)}
function misEv(name){const m=MIS.cur;if(!m)return;const s=m.steps[m.i];if((s.type==='steal'&&name==='steal_'+s.from)||(s.type==='police'&&name==='police')||(s.type==='dig'&&name==='dig')||(s.type==='bark'&&name==='bark'&&misNear(s.t,8)))misNext()}
function misUpd(dt){const m=MIS.cur;if(!m){misHud.hidden=true;misMk.visible=false;return}m.t-=dt;
  if(m.t<=0){arcade('しっぱい…','FAILED','lose');sfx.lose();toast('Mission failed: '+m.title+'. '+(m.lose||'Auntie sighs.'));say(auntie,m.lose||'Aiya…',4);MIS.cur=null;return}
  const s=m.steps[m.i];if(s.type==='goto'&&misNear(s.t,8))misNext();else if(s.type==='drive'&&dog.cart&&misNear(s.t,12))misNext();
  else if(s.type==='deliver'&&dog.item&&dog.item.type===s.item&&misNear(s.t,2.6)){const it=dog.item;dog.item=null;scene.remove(it.g);items.splice(items.indexOf(it),1);hearts(6);misNext()}
  else if(s.type==='sit'&&dog.posture==='sit'&&misNear(s.t,3.2)&&dog.sitT>1.5)misNext();
  if(!MIS.cur){misHud.hidden=true;misMk.visible=false;return}
  const cs=MIS.cur.steps[MIS.cur.i];misHud.hidden=false;const tt=Math.max(0,Math.ceil(MIS.cur.t));misHud.querySelector('.mT').textContent='MISSION '+(MIS.cur.i+1)+'/'+MIS.cur.steps.length+'  '+Math.floor(tt/60)+':'+String(tt%60).padStart(2,'0');misHud.querySelector('.mS').textContent=cs.text+(cs.type==='deliver'?' ('+cs.item+')':'');
  if(cs.t){const p=misPos(cs.t);misMk.visible=true;misMk.position.set(p[0],groundAt(p[0],p[1])+3.2+Math.sin(S.t*4)*0.3,p[1])}else misMk.visible=false}
'''
c = R(c, "function genListen(){", CHAT + "function genListen(){")
c = R(c, "if(dbUpd)dbUpd(dt);mpUpd(dt);genUpd(dt);", "if(dbUpd)dbUpd(dt);mpUpd(dt);genUpd(dt);misUpd(dt);")
c = R(c, "function destroy(){dead=true;", "function destroy(){dead=true;chBox.hidden=true;misHud.hidden=true;")
c = R(c, "S.digN++;", "S.digN++;misEv('dig');")
c = R(c, "complete('police');", "complete('police');misEv('police');")
c = R(c, "complete(site==='picnic'?'picnic':'bbq');", "complete(site==='picnic'?'picnic':'bbq');misEv('steal_'+(site==='picnic'?'picnic':'bbq'));")
c = R(c, "function doBark(){if(dog.napping)return;MP.barkN++;", "function doBark(){if(dog.napping)return;MP.barkN++;misEv('bark');")
# context: Mission with Auntie, Chat with anyone else
c = R(c, "  const k=nearCart();return k?{l:'Hop on',f:()=>hopOn(k)}:null}",
         "  const k=nearCart();if(k)return {l:'Hop on',f:()=>hopOn(k)};if(dog.swimming||busy())return null;\n  if(!MIS.cur&&!MIS.busy&&auntie.g.visible&&Math.hypot(auntie.g.position.x-dog.x,auntie.g.position.z-dog.z)<3.6)return {l:'Mission',f:askMission};\n  const pr=chatTarget();return pr?{l:'Chat',f:()=>openChat(pr)}:null}")
c = R(c, "['create','Create something new for the village (✨ Create)']]", "['create','Create something new for the village (✨ Create)'],['chat','Have a chat with Granny Chan'],['mission','Finish a mission for Auntie Wong'],['fly','Fly something a player created']]")
# map dot for mission target
c = R(c, "for(const o of MP.dogs.values())dot(o.x,o.z,'#ffd27a',3.5,true);", "for(const o of MP.dogs.values())dot(o.x,o.z,'#ffd27a',3.5,true);if(MIS.cur&&MIS.cur.steps[MIS.cur.i].t){const p=misPos(MIS.cur.steps[MIS.cur.i].t);dot(p[0],p[1],'#ffe53b',5,true)}")

open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok')
