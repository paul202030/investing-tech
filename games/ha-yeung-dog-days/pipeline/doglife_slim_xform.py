#!/usr/bin/env python3
"""Ha Yeung Dog Days, unit 2-5 (slim): pink lead walkies with Jie Jie Rose, zoomies, NPC dog friends,
Lantau street dogs, nose cam.

  python3 pipeline/doglife_slim_xform.py

- Rose + chunky pink lead (10 shared cylinder segments), L key / Lead button, treats, tug, auto-unclip when swimming.
- Zoomies (Z key / Zoom button, post-swim zoomies), loops score, flop down afterwards.
- NPC dog engine (lite rigs, distance-culled, no per-frame allocation) and friends Biscuit, Mochi, Bobo: nose-to-tail
  sniff hello, up to 2 follow you (S.pack, S.pals), mirror sit/lie, bark back, warp when far.
- Street dogs Wong Choi, Siu Hak, Fa Fa (Discovery Bay cove village) and Lucky (Ha Yeung store): shy, trust grows
  while you are calm and close, then greet and escort within their patch.
- Nose cam (V): first person at dog height, second press adds dog-colour filter.
Exact str.replace edits; every old snippet must occur exactly once in its part and in the whole file.
Refuses to run twice. Always re-apply from a pre-change copy of index.html.
"""
import os, re, subprocess, sys, tempfile

G = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
P = G + 'index.html'
src = open(P, encoding='utf-8').read()
MARK = 'const WALK={'
assert MARK not in src, 'doglife_slim_xform already applied'
k = src.rfind('<script>')
head, js = src[:k], src[k:]

EDITS = []
def E(part, old, new):
    EDITS.append((part, old, new))

# ================================================================ HTML / CSS (head part)
E('head', '<button class="act" id="aSit" type="button">Sit<small>C</small></button>',
  '<button class="act" id="aSit" type="button">Sit<small>C</small></button>'
  '<button class="act" id="aLeash" type="button">Lead<small>L</small></button>'
  '<button class="act" id="aZoom" type="button">Zoom<small>Z</small></button>')
E('head', '<button id="createBtn" type="button">✨ Create</button>',
  '<button id="createBtn" type="button">✨ Create</button><button id="noseBtn" type="button">👃 Nose cam</button>')
E('head', '#createBtn{', '#createBtn,#noseBtn{')
E('head', '#boothRes{font-family:var(--display);font-weight:800;font-size:18px;min-height:1.3em;margin:0}',
  '#boothRes{font-family:var(--display);font-weight:800;font-size:18px;min-height:1.3em;margin:0}\n'
  '.act.dim{opacity:.45}\n#game.dogvis canvas{filter:saturate(.45) sepia(.3) hue-rotate(-15deg) brightness(1.05)}\n'
  '@media (max-height:660px){.act{width:52px;height:52px;font-size:12px}#actions{grid-template-columns:repeat(2,52px);gap:8px}#aRun{width:112px;height:38px!important}#aCtx,#aSteal{width:128px;height:48px!important;font-size:18px}}')
E('head', '<kbd>X</kbd><span>Board the bus at the stop; hop on or off a golf cart (W to drive, hold Shift for turbo)</span>',
  '<kbd>X</kbd><span>Board the bus at the stop; hop on or off a golf cart (W to drive, hold Shift for turbo)</span>\n'
  '      <kbd>L</kbd><span>Pink lead on/off: walkies with Jie Jie Rose. Sit by her for treats. Border terriers start on the lead</span>\n'
  '      <kbd>Z</kbd><span>Zoomies!</span>\n'
  '      <kbd>V</kbd><span>Nose cam: the world at dog height. Press again for dog colours</span>')
E('head', 'Run, Bark, Sniff, Dig, Sit', 'Run, Bark, Sniff, Dig, Sit, Lead, Zoom')
E('head', 'X bus / golf cart · drag to look</div>', 'X bus / golf cart · L lead · Z zoomies · V nose cam · drag to look</div>')

# ================================================================ state, save data, to-dos
E('js', 'energyHintT:0', 'energyHintT:0,leash:false,walkM:0,leashHint:false,pals:{},pack:[],trust:{},trusted:{}')
E('js', 'villageHint:S.villageHint,',
  'villageHint:S.villageHint,leash:S.leash,walkM:S.walkM,leashHint:S.leashHint,pals:S.pals,pack:S.pack,trust:S.trust,trusted:S.trusted,')
E('js', "'cartHint','villageHint',", "'cartHint','villageHint','leash','walkM','leashHint','pals','pack','trust','trusted',")
E('js', 'if(!Array.isArray(S.stash))S.stash=[];',
  "S.leash=!!S.leash&&S.breed!=='lantau';S.walkM=+S.walkM||0;S.leashHint=!!S.leashHint;"
  "if(!Array.isArray(S.pack))S.pack=[];S.pack=S.pack.filter(x=>typeof x==='string').slice(0,2);"
  "for(const k of ['pals','trust','trusted'])if(!S[k]||typeof S[k]!=='object'||Array.isArray(S[k]))S[k]={};"
  "if(!Array.isArray(S.stash))S.stash=[];")
E('js', 'S.swum=false;S.napHome=0;', 'S.swum=false;S.napHome=0;S.walkM=0;')
E('js', "['north','Walk or drive to Discovery Bay North']]",
  "['walkies','Go walkies: 200 m on the pink lead or with a dog pal'],['friend','Sniff hello to a dog friend'],"
  "['streetdog','Win a village street dog’s trust (walk slowly, sit nearby)'],['north','Walk or drive to Discovery Bay North']]")
E('js', "if(k==='stash'&&!S.todos[k])t+=' · '+(S.stashDay||0)+'/3';",
  "if(k==='stash'&&!S.todos[k])t+=' · '+(S.stashDay||0)+'/3';if(k==='walkies'&&!S.todos[k])t+=' · '+Math.floor(S.walkM||0)+'/200 m';")
E('js', 'S.breed=br;', "S.breed=br;S.leash=br==='terrier';")

# ================================================================ sounds
E('js', "tada(){[523,659,784,1047].forEach((f,i)=>tone('triangle',f,f,0.3,0.12,i*0.09));tone('sine',1568,1568,0.5,0.06,0.36)},",
  "tada(){[523,659,784,1047].forEach((f,i)=>tone('triangle',f,f,0.3,0.12,i*0.09));tone('sine',1568,1568,0.5,0.06,0.36)},\n"
  "    clip(){tone('square',1800,1200,0.05,0.05);tone('square',1400,900,0.05,0.04,0.06)},\n"
  "    sniff(){burst(1800,3,0.06,0.06);burst(1700,3,0.06,0.06,0.13);burst(1900,3,0.05,0.05,0.26)},")

# ================================================================ per-frame, people, personas, minimap, hooks
E('js', 'dust.update(dt);glow.update(dt)}', 'updateWalkies(dt);updateNpcDogs(dt);dust.update(dt);glow.update(dt)}')
E('js', 'function people(){return [auntie,fisher,kid].concat(', 'function people(){return [auntie,fisher,kid,ROSE].concat(')
E('js', 'const PERSONAS=()=>[',
  "const PERSONAS=()=>[[ROSE,'Jie Jie Rose','姐姐','the family helper who takes the dog on walkies every day; warm, teasing, mixes English, Tagalog (Ay!, Ingat!) and a little Cantonese'],")
E('js', "for(const o of MP.dogs.values())dot(o.x,o.z,'#ffd27a',3.5,true);",
  "for(const o of MP.dogs.values())dot(o.x,o.z,'#ffd27a',3.5,true);"
  "for(const o of npcDogs)if(o.g.visible)dot(o.x,o.z,o.kind==='stray'?'#c68a4e':'#ff8fc8',3,false);"
  "if(ROSE.g.visible)dot(ROSE.g.position.x,ROSE.g.position.z,'#ff4fa3',3,true);")
E('js', 'for(const c of crabs)if(Math.hypot(c.x-dog.x,c.z-dog.z)<7)c.flee=2;',
  'for(const c of crabs)if(Math.hypot(c.x-dog.x,c.z-dog.z)<7)c.flee=2;barkNpcs();')
E('js', 'hearts(belly?14:7);',
  "hearts(belly?14:7);for(const o of npcDogs)if(o.st==='follow'&&Math.hypot(o.x-dog.x,o.z-dog.z)<4)npcHearts(o,5);"
  "if(S.leash&&p!==ROSE&&ROSE.g.visible&&Math.random()<0.5)say(ROSE,'Friendly one, can pat!',2.2);")
E('js', 'Math.hypot(BED.x-dog.x,BED.z-dog.z)<1.4?7:3.5)', 'Math.hypot(BED.x-dog.x,BED.z-dog.z)<1.4?7:3.5)*(NPCD.pile?1.5:1)')
E('js', 'function steal(){', "function steal(){if(S.leash&&(bbq.inRange||picnic.inRange)){S.leash=false;say(ROSE,'Sorry po! Sorry!',2)}")
E('js', 'if(dog.para){updatePara(dt);return}',
  'if(dog.para){updatePara(dt);return}\n'
  '  if(dog.zoomQ>0){dog.zoomQ-=dt;if(dog.zoomQ<=0&&!busy()&&!dog.swimming)startZoomies(6,true)}')

# ================================================================ zoomies + lead speed cap
E('js', '*Math.min(1,mag*1.25)*(dog.zoomT>0?1.8:1)}',
  '*Math.min(1,mag*1.25)*(dog.zoomT>0?1.8:1)}\n'
  '  if(dog.frapT>0){dog.frapT-=dt;if(dog.swimming)dog.frapT=0;\n'
  '    if(mag<=0.1&&!busy()){dog.heading+=dt*2.6*dog.zoomDir;target=9}\n'
  '    dog.loopA+=Math.abs(angDiff(dog.lastH,dog.heading));dog.lastH=dog.heading;\n'
  "    if(dog.loopA>=6.2832){dog.loopA-=6.2832;dog.loops++;S.points+=5;popScore('LOOP ×'+dog.loops+'!')}\n"
  "    if(dog.speed>2&&Math.random()<dt*18){const sf=surface(dog.x,dog.z);if(sf==='sand'||sf==='grass')dust.emit(dog.x-Math.sin(dog.heading)*0.3,dog.y+0.1,dog.z-Math.cos(dog.heading)*0.3,(Math.random()-0.5)*1.5,1+Math.random(),(Math.random()-0.5)*1.5,0.6,sf==='sand'?C_SAND:C_DIRT,9.8)}\n"
  '    if(dog.frapT<=0)endZoomies()}\n'
  '  if(S.leash&&target>6.5)target=6.5;')
E('js', 'const run=(keys.shift||runLock||joy.mag>0.88)&&!dog.sniff&&!dog.swimming;',
  'const run=((keys.shift||runLock||joy.mag>0.88)&&!dog.sniff||dog.frapT>0)&&!dog.swimming;')
E('js', 'else if(was&&dog.swimT>1){dog.shakeT=1.2;dog.swimT=0;sfx.splash()}',
  "else if(was&&dog.swimT>1){dog.shakeT=1.2;dog.swimT=0;sfx.splash();if(S.breed==='terrier'||Math.random()<0.5)dog.zoomQ=1.3}")
E('js', 'cam.yaw+=angDiff(cam.yaw,dog.heading)*dt*(0.7+csp*0.05);',
  'cam.yaw+=angDiff(cam.yaw,dog.heading)*dt*(0.7+csp*0.05)*(dog.frapT>0?0.35:1);')
E('js', 'D.tsegs.forEach((s,i)=>{if(i)s.rotation.z=Math.sin(S.t*ws-i*0.6)*wa*0.4})',
  'D.tsegs.forEach((s,i)=>{if(i)s.rotation.z=Math.sin(S.t*ws-i*0.6)*wa*0.4});if(dog.frapT>0){D.hip.rotation.x+=0.12;D.tail.rotation.x-=0.6}')

# ================================================================ keys, binds, hud
E('js', "else if(k==='x')doCtx();", "else if(k==='x')doCtx();else if(k==='l')toggleLeash();else if(k==='z')doZoom();else if(k==='v')toggleNose();")
E('js', "bind('#aCtx',()=>doCtx());", "bind('#aCtx',()=>doCtx());bind('#aLeash',()=>toggleLeash());bind('#aZoom',()=>doZoom());bind('#noseBtn',()=>toggleNose());")
E('js', "$('#aSit').firstChild.textContent=dog.posture==='stand'?'Sit':dog.posture==='sit'?'Lie':'Up';",
  "$('#aSit').firstChild.textContent=dog.posture==='stand'?'Sit':dog.posture==='sit'?'Lie':'Up';\n"
  "  {const b=$('#aLeash');b.firstChild.textContent=S.breed==='lantau'?'Free!':S.leash?'Unclip':'Lead';b.classList.toggle('on',!!S.leash);$('#aZoom').classList.toggle('dim',WALK.zoomCool>0||S.energy<20)}")

# ================================================================ nose cam
E('js', 'const cam={yaw:0,pitch:0.32,dist:5.5,lastDrag:-10};',
  'const cam={yaw:0,pitch:0.32,dist:5.5,lastDrag:-10,mode:0,eyeYaw:0,eyePitch:0.02};const NOSE_V=new THREE.Vector3();')
E('js', 'function updateCamera(dt){',
  'function updateCamera(dt){\n'
  '  if(cam.mode>0&&!dog.cart&&!dog.para&&!S.leaving){if(camera.fov!==72){camera.fov=72;camera.updateProjectionMatrix()}D.root.updateMatrixWorld(true);D.head.getWorldPosition(NOSE_V);'
  'if(dog.speed>0.6)cam.eyeYaw*=1-Math.min(1,dt*2);const yw=dog.heading+cam.eyeYaw,cp=Math.cos(cam.eyePitch),bob=Math.sin(dog.phase*2)*0.015*Math.min(1,dog.speed/3);'
  'camera.position.set(NOSE_V.x+Math.sin(yw)*0.2*D.k,Math.max(NOSE_V.y+0.05*D.k+bob,groundAt(NOSE_V.x,NOSE_V.z)+0.12),NOSE_V.z+Math.cos(yw)*0.2*D.k);'
  'camera.lookAt(camera.position.x+Math.sin(yw)*cp,camera.position.y+Math.sin(cam.eyePitch),camera.position.z+Math.cos(yw)*cp);D.head.visible=false;return}\n'
  '  D.head.visible=true;if(camera.fov!==58){camera.fov=58;camera.updateProjectionMatrix()}')
E('js', 'cam.yaw-=(e.clientX-drag.x)*0.006;cam.pitch=clamp(cam.pitch+(e.clientY-drag.y)*0.004,0.05,1.3);',
  'if(cam.mode>0){cam.eyeYaw=clamp(cam.eyeYaw-(e.clientX-drag.x)*0.006,-1.2,1.2);cam.eyePitch=clamp(cam.eyePitch-(e.clientY-drag.y)*0.004,-0.5,0.6)}'
  'else{cam.yaw-=(e.clientX-drag.x)*0.006;cam.pitch=clamp(cam.pitch+(e.clientY-drag.y)*0.004,0.05,1.3)}')
E('js', 'if(v3.z>1||far||!b.obj.g.visible){', 'if(v3.z>1||far||!b.obj.g.visible||(b.obj===DOGTALK&&cam.mode>0&&!dog.cart&&!dog.para)){')
E('js', 'function lowerQuality(silent){if(quality===0)return;quality--;',
  "function lowerQuality(silent){if(quality===0)return;quality--;$('#game').classList.remove('dogvis');if(cam.mode===2)cam.mode=1;")
E('js', "$('#aSteal').hidden=true;$('#aCtx').hidden=true;knob.style.transform='';$('#arcade').className='';sfx.set(0,0,48)}",
  "$('#aSteal').hidden=true;$('#aCtx').hidden=true;knob.style.transform='';$('#arcade').className='';$('#game').classList.remove('dogvis');sfx.set(0,0,48)}")

# ================================================================ Discovery Bay gather spot capture (for the street dogs)
E('js', '{const g=new THREE.Group();g.position.set(gx,gridH(gx,gz),gz);scene.add(g);const white=mat(0xf4f4f0);',
  'X.gx=gx;X.gz=gz;{const g=new THREE.Group();g.position.set(gx,gridH(gx,gz),gz);scene.add(g);const white=mat(0xf4f4f0);')

# ================================================================ big build-time section
SECTION = r"""// ================= Dog Days: pink lead walkies, zoomies, dog friends, street dogs, nose cam =================
const ROSE=makePerson({shirt:0xf59ac0,pants:0x34405e,hair:0x1a1614,skin:0xc8956c});ROSE.g.visible=false;ROSE.g.rotation.order='YXZ';
const LEASH={geo:new THREE.CylinderGeometry(0.03,0.03,1,6),mat:mat(0xff4fa3,{emissive:0x5a0f33}),segs:[],P:[],A:new THREE.Vector3(),B:new THREE.Vector3(),M:new THREE.Vector3(),UP:new THREE.Vector3(0,1,0)};
for(let i=0;i<11;i++)LEASH.P.push(new THREE.Vector3());
for(let i=0;i<10;i++){const m=new THREE.Mesh(LEASH.geo,LEASH.mat);m.visible=false;m.frustumCulled=false;m.castShadow=false;scene.add(m);LEASH.segs.push(m)}
const WALK={dragT:0,tugShown:false,talkT:3,treatT:10,wait:false,offT:0,reachT:0,zoomCool:0,sniffPrev:false,lastM:0};
const npcDogs=[];
const NPCD={barkCd:0,init:false,day:-1,pile:false,pileDay:-1,lastBark:-9,tip:false,mk:null,mkD:99};
const FSLOT=[[1.6,0.8],[1.6,-0.8],[2.8,0],[3.6,0.5]],SIDES=[1,-1];
const BLOB_G=new THREE.CircleGeometry(0.45,12);BLOB_G.rotateX(-Math.PI/2);
const BLOB_M=new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:0.22,depthWrite:false});
const TRUSTMK=mkMarker(0xff7ab6,0.6);
const fname=o=>o.name.replace(/\s*[^\x00-\x7f].*$/,'');

// ---------- Rose and the pink lead
function hideLeash(){for(const m of LEASH.segs)m.visible=false}
function spawnRose(){const h=dog.heading;let x=dog.x-Math.sin(h)*2,z=dog.z-Math.cos(h)*2;const q=pushOutB(x,z,0.35);x=q[0];z=q[1];
  if(bldAt(x,z)||gridH(x,z)<0.3){x=dog.x;z=dog.z}
  ROSE.g.position.set(x,groundAt(x,z),z);ROSE.g.visible=true;ROSE.g.rotation.x=0;
  for(let i=0;i<8;i++)dust.emit(x+(Math.random()-0.5)*0.8,ROSE.g.position.y+0.2,z+(Math.random()-0.5)*0.8,(Math.random()-0.5)*1.5,0.6+Math.random(),(Math.random()-0.5)*1.5,0.8,C_SAND,4);
  say(ROSE,'Walkies time, '+S.name+'!',2.4)}
function toggleLeash(){
  if(S.breed==='lantau'){toast('Village dogs go where they like. No lead for you!');return}
  if(dog.cart||dog.para||dog.swimming){toast('Not now!');return}
  S.leash=!S.leash;WALK.wait=false;
  if(S.leash){arcade('おさんぽ!','WALKIES!','clear');sfx.clip();WALK.tugShown=false;WALK.dragT=0;
    if(!S.leashHint){S.leashHint=true;toast('On the lead you trot instead of sprint. Sit next to Rose for treats.')}}
  else{say(ROSE,'Off you go! Come back ha!',2.4);sfx.clip();WALK.offT=0}}
function walkAdd(dt){S.walkM+=dog.speed*dt;const m=Math.floor(S.walkM/20);if(m!==WALK.lastM){WALK.lastM=m;renderTodos()}if(S.walkM>=200)complete('walkies')}
function updateWalkies(dt){
  WALK.zoomCool-=dt;WALK.reachT-=dt;const rp=ROSE.g.position;
  if(dog.frapT>0&&(dog.cart||dog.para))dog.frapT=0;
  if(!S.started||S.leaving||S.breed==='lantau'){if(S.breed==='lantau')S.leash=false;ROSE.g.visible=false;hideLeash();return}
  if(S.leash&&(dog.cart||dog.para||dog.swimming)){S.leash=false;WALK.wait=!!dog.swimming&&!dog.cart&&!dog.para;WALK.offT=0;
    if(ROSE.g.visible)say(ROSE,dog.swimming?'Swim ah? Ok lang, I wait here!':'Ingat! Be careful!',2.4)}
  if(WALK.wait&&!dog.swimming&&!dog.cart&&!dog.para&&ROSE.g.visible&&Math.hypot(rp.x-dog.x,rp.z-dog.z)<2.6){
    S.leash=true;WALK.wait=false;WALK.tugShown=false;WALK.dragT=0;say(ROSE,'Good dog, come.',2);sfx.clip()}
  let d=Math.hypot(dog.x-rp.x,dog.z-rp.z);
  if(S.leash){
    if(!ROSE.g.visible||d>8){spawnRose();d=Math.hypot(dog.x-rp.x,dog.z-rp.z)}
    const Lmax=3.0,ox=rp.x,oz=rp.z;let dragged=false;
    if(d>Lmax){dragged=true;const k=Lmax/d;rp.x=dog.x-(dog.x-ox)*k;rp.z=dog.z-(dog.z-oz)*k}
    else if(d>1.8){if(!dog.sniff){const st=Math.min(1.5*dt,d-1.8);rp.x+=(dog.x-ox)/d*st;rp.z+=(dog.z-oz)/d*st}else if(!WALK.sniffPrev)say(ROSE,'OK, sniff sniff…',1.8)}
    WALK.sniffPrev=dog.sniff;
    const pp=pushOutB(rp.x,rp.z,0.35);let px=pp[0],pz=pp[1];if(gridH(px,pz)<-0.3){px=ox;pz=oz}
    rp.x=px;rp.z=pz;rp.y=groundAt(px,pz);
    const osp=Math.hypot(px-ox,pz-oz)/Math.max(dt,1e-3);d=Math.hypot(dog.x-px,dog.z-pz);
    facePerson(ROSE,dog.x,dog.z,dt);animPerson(ROSE,Math.min(osp/1.4,3.2),dt);
    const drag=osp>2.4;ROSE.arms[1].rotation.x=drag?-1.45:-0.55;ROSE.g.rotation.x+=((drag?-0.22:0)-ROSE.g.rotation.x)*Math.min(1,dt*6);
    if(WALK.reachT>0||ROSE.patT>0)ROSE.arms[0].rotation.x=-1.0+Math.sin(S.t*12)*0.3;
    if(dragged)WALK.dragT+=dt;else WALK.dragT=Math.max(0,WALK.dragT-dt*2);
    if(WALK.dragT>1.2&&!WALK.tugShown){WALK.tugShown=true;arcade('グイグイ!','TUG!','run');shake();S.points+=5;popScore('PULL +5')}
    WALK.talkT-=dt;
    if(WALK.talkT<=0){if(dragged||WALK.dragT>0.3){WALK.talkT=4+Math.random()*2;say(ROSE,pick([S.name+'! 慢啲! Slow down!','Dahan-dahan lang! Gently!','Wahhh! Wait for me!']),2.2)}
      else{WALK.talkT=12+Math.random()*6;say(ROSE,pick(['Good dog, '+S.name+'.','So hot today ah.','Walkies, walkies!']),2.4)}}
    WALK.treatT-=dt;
    if(dog.posture==='sit'&&d<3&&WALK.treatT<=0){let road=false;for(let i=0;i<4;i++){const a=i*1.5708;if(RMASK[cellIdx(dog.x+Math.cos(a)*3,dog.z+Math.sin(a)*3)]===1){road=true;break}}
      WALK.treatT=40;S.hunger=Math.min(100,S.hunger+(road?16:8));S.happy=Math.min(100,S.happy+6);S.points+=road?20:10;hearts(8);
      popScore(road?'GOOD WAIT! +20':'TREAT +10');say(ROSE,road?'Good wait at the road, '+S.name+'! 乖!':'Good sit, '+S.name+'! Treat!',2.6);WALK.reachT=1}
    walkAdd(dt)}
  else if(ROSE.g.visible){
    if(d>60)ROSE.g.visible=false;
    else{facePerson(ROSE,dog.x,dog.z,dt);animPerson(ROSE,0,dt);ROSE.g.rotation.x+=(0-ROSE.g.rotation.x)*Math.min(1,dt*6);ROSE.arms[1].rotation.x=-0.55;
      WALK.offT+=dt;if(WALK.offT<3)ROSE.arms[0].rotation.x=-1.0+Math.sin(S.t*8)*0.4}}
  if(S.leash&&ROSE.g.visible){
    const A=LEASH.A,B=LEASH.B,P=LEASH.P;
    D.root.updateMatrixWorld(true);D.leashPt.getWorldPosition(A);
    ROSE.g.updateMatrixWorld(true);ROSE.arms[1].localToWorld(B.set(0,-0.7,0.08));
    const slack=Math.max(0,3.2-A.distanceTo(B));
    for(let i=0;i<=10;i++){const t=i/10;P[i].lerpVectors(A,B,t);P[i].y=Math.max(P[i].y-slack*1.1*4*t*(1-t),groundAt(P[i].x,P[i].z)+0.03)}
    for(let j=0;j<10;j++){const m=LEASH.segs[j],a=P[j],b=P[j+1],L=a.distanceTo(b);if(L<1e-4){m.visible=false;continue}
      m.position.set((a.x+b.x)*0.5,(a.y+b.y)*0.5,(a.z+b.z)*0.5);m.scale.set(1,L,1);m.quaternion.setFromUnitVectors(LEASH.UP,LEASH.M.subVectors(b,a).normalize());m.visible=true}}
  else hideLeash()}

// ---------- Zoomies
function startZoomies(sec,free){if(dog.swimming||dog.cart||dog.para)return;standUp();dog.frapT=sec;dog.runT=2.2;dog.zoomDir=Math.random()<0.5?-1:1;dog.loopA=0;dog.loops=0;dog.lastH=dog.heading;
  if(!free){S.energy=Math.max(0,S.energy-10);WALK.zoomCool=30}
  arcade('ズーミー!','ZOOMIES!','run');sfx.arcadeStart();
  let best=null,bd=144;for(const p of people()){if(!p.g.visible)continue;const dd=(p.g.position.x-dog.x)**2+(p.g.position.z-dog.z)**2;if(dd<bd){bd=dd;best=p}}
  if(best)say(best,pick(['Hahaha! 發癲呀! Crazy dog!','Wah, so fast!','Zoomies! Hahaha!']),2.4)}
function endZoomies(){dog.frapT=0;dog.posture='lie';dog.lieT=-1.5;S.happy=Math.min(100,S.happy+12);say(DOGTALK,'Hah… hah… hah…',1.6);if(dog.loops>=3)popScore('ZOOMIE COMBO ×'+dog.loops+'!')}
function doZoom(){if(busy()||dog.swimming||dog.cart||dog.para||dog.frapT>0)return;
  if(WALK.zoomCool>0){toast('Catch your breath first!');return}
  if(S.energy<20){toast('Too tired for zoomies. Have a nap first!');return}
  startZoomies(6,false)}

// ---------- Nose cam
function toggleNose(){cam.mode=(cam.mode+1)%3;cam.eyeYaw=0;cam.eyePitch=0.02;$('#game').classList.toggle('dogvis',cam.mode===2);
  if(cam.mode===1){if(!cam.hinted){cam.hinted=true;toast('Nose cam: the world at dog height. Press V again for dog colours.')}else toast('Nose cam.')}
  else if(cam.mode===2)toast('Dog colours: dogs see blues and yellows best; reds look brownish.');else toast('Normal camera.')}

// ---------- NPC dog engine
function mkNpcDog(id,kind,name,breed,opt,hx,hz){
  const D2=makeDog(breed,{lite:true,mc:true,c:opt.c,collar:opt.collar});scene.add(D2.root);D2.root.visible=false;
  const bl=new THREE.Mesh(BLOB_G,BLOB_M);bl.position.y=0.03;bl.scale.setScalar(D2.k);bl.castShadow=false;D2.root.add(bl);
  const o={id,kind,name,breed:D2.breed,D:D2,g:D2.root,headY:0.45+0.6*D2.k,home:[hx,hz],x:hx,z:hz,y:groundAt(hx,hz),h:Math.random()*6.28,ph:0,wp:Math.random()*6,sit:0,lie:0,tSit:0,tLie:0,sniffP:0,sleep:false,bow:0,barkT:0,echoT:0,moved:0,
    st:'idle',t:Math.random()*4,tx:hx,tz:hz,gt:-1,ga:0,greeted:false,stuckT:0,waryT:0,backT:0,bk:0,hT:0,si:0,es:1,siesta:false,dayRoll:-1,sn:false};
  npcDogs.push(o);return o}
function poseDog2(o,sp,dt){
  const Dd=o.D,k=Dd.k,sit=o.sit,lie=o.lie;o.ph+=dt*Math.min(sp*3,24);const a=Math.sin(o.ph)*Math.min(1,sp/2.5)*0.6;
  for(let i=0;i<4;i++){const L=Dd.legs[i],s=(i===0||i===3)?a:-a;
    if(L.front){L.up.rotation.x=o.bow>0?-1.1:s+sit*0.55-lie*1.45;L.kn.rotation.x=lie*0.1}
    else{L.up.rotation.x=s-sit*1.0-lie*1.3;L.kn.rotation.x=sit*1.7+lie*1.5}}
  Dd.hip.position.y=(0.56-sit*0.3-lie*0.36)*k;Dd.hip.rotation.x=-sit*0.55+(o.bow>0?0.35:0);
  Dd.neck.rotation.x=0.5+lie*0.7+o.sniffP*1.2;Dd.head.rotation.x=-Dd.neck.rotation.x-Dd.hip.rotation.x+0.5+lie*0.15+o.sniffP*0.6;
  Dd.tail.rotation.x=lerp(-1.15,-1.55,Math.max(sit,lie))+Dd.tailUp;Dd.tail.rotation.z=Math.sin(S.t*(o.sleep?2:12)+o.wp)*(o.sleep?0.05:0.5);
  Dd.jaw.rotation.x=0.04+(o.barkT>0?0.5:sp>3.6?0.2+Math.sin(S.t*14)*0.06:0);Dd.tongue.visible=sp>3.6||o.barkT>0;
  const es=o.sleep?0.12:1;if(o.es!==es){o.es=es;for(const e of Dd.eyes)e.scale.y=es}}
function npcMove(o,tx,tz,spd,dt,canSwim){
  const dx=tx-o.x,dz=tz-o.z,d=Math.hypot(dx,dz);if(d<0.05)return 0;
  o.h+=angDiff(o.h,Math.atan2(dx,dz))*Math.min(1,dt*8);
  const step=Math.min(spd*dt,d),fx=Math.sin(o.h),fz=Math.cos(o.h),lim=canSwim?-6:0.3;let nx=o.x+fx*step,nz=o.z+fz*step;
  if(gridH(nx+fx*0.4,nz+fz*0.4)<lim){let ok=false;
    for(let i=0;i<2&&!ok;i++){const sg=SIDES[i],px=-fz*sg,pz=fx*sg;nx=o.x+px*step;nz=o.z+pz*step;if(gridH(nx+px*0.4,nz+pz*0.4)>=lim)ok=true}
    if(!ok)return 0}
  const q=pushOutB(nx,nz,0.35);nx=clamp(q[0],X0+20,X1-20);nz=clamp(q[1],Z0+20,Z1-20);
  const m=Math.hypot(nx-o.x,nz-o.z);o.x=nx;o.z=nz;return m}
function npcWarp(o,tx,tz){if(bldAt(tx,tz)||gridH(tx,tz)<-0.5){tx=dog.x;tz=dog.z}o.x=tx;o.z=tz;o.y=groundAt(tx,tz);o.stuckT=0}
function npcHearts(o,n){for(let i=0;i<n;i++)glow.emit(o.x+(Math.random()-0.5)*0.6,o.y+0.9*o.D.k+Math.random()*0.3,o.z+(Math.random()-0.5)*0.6,(Math.random()-0.5)*0.4,0.7+Math.random()*0.5,(Math.random()-0.5)*0.4,1.6,C_HEART,0)}
function npcBark(o){o.barkT=0.4;say(o,breedInfo(o.breed).bark.split(' ')[0],1);if(NPCD.barkCd<=0){NPCD.barkCd=0.7;sfx.bark(o.D.pitch)}}
function barkNpcs(){NPCD.lastBark=S.t;let i=0;
  for(const o of npcDogs){const dd=Math.hypot(o.x-dog.x,o.z-dog.z);
    if(o.st==='follow'&&dd<25){o.echoT=0.3+i*0.25;i++}
    else if(o.kind==='stray'){const key=WD.level+':'+o.id,tt=S.trust[key]||0;
      if(tt<1&&dd<8){S.trust[key]=Math.max(0,tt-0.12);o.waryT=2.5;o.backT=1.2}
      else if(tt>=1&&dd<25&&o.g.visible){o.echoT=0.3+i*0.25;i++}}}}
// nose-to-tail sniff hello; returns true when finished
function greetStep(o,d,dt){
  if(o.gt<0){const bx=dog.x-Math.sin(dog.heading)*0.9,bz=dog.z-Math.cos(dog.heading)*0.9;
    o.moved=npcMove(o,bx,bz,Math.min(7,d*2+2),dt,false);
    if(Math.hypot(o.x-bx,o.z-bz)<0.6||d<1.2){o.gt=0;o.ga=Math.atan2(o.x-dog.x,o.z-dog.z);say(o,'*sniff sniff*',1.6);sfx.sniff()}
    return false}
  o.gt+=dt;const ang=o.ga+o.gt*2.6;
  o.moved=npcMove(o,dog.x+Math.sin(ang)*0.85,dog.z+Math.cos(ang)*0.85,3.2,dt,false);o.sniffP=1;
  if(o.gt>=1.6){o.gt=-1;npcHearts(o,8);hearts(6);return true}
  return false}
function followStep(o,slot,dt){
  const h=dog.heading,sl=FSLOT[slot<0?0:slot>3?3:slot];let tx,tz;const flank=dog.napping&&slot<2;
  if(flank){const sd=slot?-0.7:0.7;tx=dog.x+Math.cos(h)*sd;tz=dog.z-Math.sin(h)*sd}
  else{tx=dog.x-Math.sin(h)*sl[0]+Math.cos(h)*sl[1];tz=dog.z-Math.cos(h)*sl[0]-Math.sin(h)*sl[1]}
  const d=Math.hypot(o.x-dog.x,o.z-dog.z);
  if(d>45||o.stuckT>2.5){npcWarp(o,tx,tz);o.moved=0;return}
  let gx=tx,gz=tz,spd;
  if(dog.frapT>0){gx=dog.x;gz=dog.z;spd=Math.min(Math.hypot(gx-o.x,gz-o.z)*2.5+2,14)}
  else spd=Math.min(Math.hypot(tx-o.x,tz-o.z)*2.5,Math.max(3,dog.speed*1.15),20);
  const dist=Math.hypot(gx-o.x,gz-o.z);
  if(d<0.9&&!flank){gx=o.x+(o.x-dog.x)*2;gz=o.z+(o.z-dog.z)*2;spd=2}
  const m=npcMove(o,gx,gz,spd,dt,o.kind==='friend');o.moved=m;
  if(dist>2.5&&m<spd*dt*0.2)o.stuckT+=dt;else o.stuckT=Math.max(0,o.stuckT-dt);
  const near=Math.hypot(tx-o.x,tz-o.z)<2.5;
  o.tSit=dog.posture==='sit'&&dog.sitT>0.45&&near?1:0;o.tLie=dog.posture==='lie'&&near?1:0;o.sleep=dog.napping&&o.lie>0.8;
  if(flank&&near)o.h+=angDiff(o.h,dog.heading)*Math.min(1,dt*6)}

// ---------- friends
function friendUpd(o,d,dt){
  const H=S.hour,out=H>=7&&H<21.5,st=o.st;
  o.g.visible=st==='follow'||st==='greet'||st==='gohome'||(out&&d<(quality<2?45:75));
  if(!o.g.visible)return;
  if(st==='idle'){
    o.t-=dt;
    if(o.t<=0){o.t=4+Math.random()*4;if(Math.random()<0.3){o.tLie=1;o.tx=o.x;o.tz=o.z}else{o.tLie=0;const p=groundSpot(o.home[0],o.home[1],8);if(p){o.tx=p[0];o.tz=p[1]}}}
    o.tSit=0;
    if(!o.tLie&&Math.hypot(o.tx-o.x,o.tz-o.z)>0.3)o.moved=npcMove(o,o.tx,o.tz,1.2,dt,false);
    if(out&&!o.greeted&&(d<6||(S.pals[o.id]&&d<30))){o.st='greet';o.gt=-1;o.tLie=0;if(S.pals[o.id])say(o,'Yap!',1)}}
  else if(st==='greet'){
    o.tSit=0;o.tLie=0;
    if(greetStep(o,d,dt)){o.greeted=true;
      if(!S.pals[o.id]){S.pals[o.id]={met:S.day};arcade('ともだち!','NEW FRIEND! '+fname(o),'clear');sfx.tada()}else popScore('くんくん! HELLO!');
      complete('friend');
      if(S.pack.length<2&&!S.pack.includes(o.id)){S.pack.push(o.id);o.st='follow';o.stuckT=0;toast(fname(o)+' joins your pack!')}else o.st='idle'}
    else if(d>45){o.st='idle';o.gt=-1}}
  else if(st==='follow'){
    const slot=S.pack.indexOf(o.id);
    if(slot<0){o.st='idle';return}
    if(H>=22||H<6){S.pack.splice(slot,1);say(o,'*yawn*',1.5);toast(fname(o)+' is sleepy and trots home. See you tomorrow!');o.st='gohome';return}
    followStep(o,slot,dt)}
  else if(st==='gohome'){
    o.tSit=0;o.tLie=0;o.moved=npcMove(o,o.home[0],o.home[1],3,dt,false);
    if(Math.hypot(o.x-o.home[0],o.z-o.home[1])<1.5||d>80){o.x=o.home[0];o.z=o.home[1];o.g.visible=false;o.st='idle'}}}
function initFriends(){
  if(!npcDogs.length)return;
  const H=S.hour,ok=H>=6&&H<22,pk=[];
  for(const id of S.pack)if(!pk.includes(id)&&npcDogs.some(o=>o.id===id&&o.kind==='friend'))pk.push(id);
  S.pack=ok?pk.slice(0,2):[];
  const names=[],h=dog.heading;
  S.pack.forEach((id,i)=>{const o=npcDogs.find(q=>q.id===id);o.st='follow';o.greeted=true;
    const sl=FSLOT[i];npcWarp(o,dog.x-Math.sin(h)*sl[0]+Math.cos(h)*sl[1],dog.z-Math.cos(h)*sl[0]-Math.sin(h)*sl[1]);o.g.visible=true;names.push(fname(o))});
  if(ARRIVE&&names.length)toast(names.join(' and ')+' hop'+(names.length>1?'':'s')+' off the bus with you!');
  if(S.breed==='terrier'&&!S.pals.biscuit&&H>=7&&H<21.5){const o=npcDogs.find(q=>q.id==='biscuit');
    if(o){npcWarp(o,dog.x+Math.sin(h)*3-Math.cos(h)*1.5,dog.z+Math.cos(h)*3+Math.sin(h)*1.5);o.st='greet';o.gt=-1;o.greeted=false;o.g.visible=true;say(o,'Yap! Yap!',1.6)}}}

// ---------- street dogs
function strayIdle(o,H,d,dt){
  const night=H>=21.8||H<5.2;
  if(o.dayRoll!==S.day){o.dayRoll=S.day;o.siesta=Math.random()<0.8}
  const hd=Math.hypot(o.x-o.home[0],o.z-o.home[1]),sies=H>=10&&H<16&&o.siesta;
  if(hd>20||night||sies){
    if(hd>2)o.moved=npcMove(o,o.home[0],o.home[1],hd>20?2.6:1.4,dt,false);
    else if(night)o.tSit=1;
    else if(sies){o.tLie=1;o.sleep=d>=4}
    return}
  o.t-=dt;
  if(o.t<=0){o.t=8+Math.random()*7;let p=null;for(let i=0;i<6&&!p;i++){const q=groundSpot(o.home[0],o.home[1],15);if(q&&RMASK[cellIdx(q[0],q[1])]!==1)p=q}if(p){o.tx=p[0];o.tz=p[1]}o.sn=Math.random()<0.5}
  if(Math.hypot(o.tx-o.x,o.tz-o.z)>0.4)o.moved=npcMove(o,o.tx,o.tz,1.4,dt,false);else if(o.sn)o.sniffP=0.5}
function strayUpd(o,d,dt){
  const key=WD.level+':'+o.id;let t=S.trust[key]||0;if(S.breed==='lantau'&&t<0.6)t=0.6;
  o.g.visible=o.st==='greet'||o.st==='escort'||d<(quality<2?45:75);
  if(!o.g.visible)return;
  o.tSit=0;o.tLie=0;o.sleep=false;
  const H=S.hour,dh=Math.hypot(dog.x-o.home[0],dog.z-o.home[1]);
  if(t<1&&dog.speed>3.6&&d<9){if(!(o.waryT>0))o.backT=1.2;o.waryT=2.5;t=Math.max(0,t-0.15*dt*(S.breed==='lantau'?0.5:1));
    if(!NPCD.tip){NPCD.tip=true;toast('Village dogs are shy of fast strangers. Walk up slowly, then sit or lie down nearby.')}}
  if(o.waryT>0&&t<1){
    o.waryT-=dt;const dx=o.x-dog.x,dz=o.z-dog.z,dd=Math.hypot(dx,dz)||1,h0=o.h;
    if(o.backT>0){o.backT-=dt;o.moved=npcMove(o,o.x+dx/dd*3,o.z+dz/dd*3,1.5,dt,false)}
    o.h=h0+angDiff(h0,Math.atan2(-dx,-dz))*Math.min(1,dt*6);
    o.bk-=dt;if(o.bk<=0){o.bk=1.2;npcBark(o)}}
  else{
    o.waryT=0;
    if(d<6&&dog.speed<1.3&&!dog.swimming&&t<1){
      t+=0.06*(dog.posture!=='stand'?2.5:1)*(S.breed==='lantau'?2:1)*dt;
      o.hT-=dt;if(o.hT<=0){o.hT=1.2;npcHearts(o,1)}
      if(d<NPCD.mkD){NPCD.mkD=d;NPCD.mk=o}}
    if(t>=1){
      if(dh<70&&d<30){
        if(!o.greeted){o.st='greet';
          if(greetStep(o,d,dt)){o.greeted=true;o.st='idle';
            if(!S.trusted[key]){S.trusted[key]=1;arcade('なかま!','VILLAGE FRIEND! '+fname(o),'clear');sfx.tada()}
            complete('streetdog')}}
        else{o.st='escort';followStep(o,Math.min(3,2+o.si),dt)}}
      else{
        if(o.gt>=0)o.gt=-1;
        if(o.st==='escort'&&dh>=70){say(o,'*sits down*',1.5);toast(fname(o)+' stays on the patch.')}
        if(o.st==='escort'||o.st==='greet')o.st='idle';
        strayIdle(o,H,d,dt)}}
    else if(t>=0.4&&d<6){
      if(d>1.4){const k=1.4/d;o.moved=npcMove(o,dog.x+(o.x-dog.x)*k,dog.z+(o.z-dog.z)*k,1.6,dt,false)}
      if(d<1.6){o.sniffP=1;o.h+=angDiff(o.h,Math.atan2(dog.x-o.x,dog.z-o.z))*Math.min(1,dt*6)}}
    else strayIdle(o,H,d,dt)}
  S.trust[key]=t<0?0:t>1?1:t}

// ---------- per-frame
function updateNpcDogs(dt){
  if(!S.started||S.leaving)return;
  if(!NPCD.init){NPCD.init=true;initFriends()}
  if(!npcDogs.length)return;
  if(NPCD.day!==S.day){NPCD.day=S.day;for(const o of npcDogs)o.greeted=false}
  NPCD.barkCd-=dt;NPCD.mk=null;NPCD.mkD=99;
  for(const o of npcDogs){
    const d=Math.hypot(o.x-dog.x,o.z-dog.z);
    if(o.barkT>0)o.barkT-=dt;if(o.bow>0)o.bow-=dt;
    if(o.echoT>0){o.echoT-=dt;if(o.echoT<=0)npcBark(o)}
    o.moved=0;o.sniffP=0;
    if(o.kind==='friend')friendUpd(o,d,dt);else if(o.kind==='stray')strayUpd(o,d,dt);
    if(!o.g.visible)continue;
    const gy=groundAt(o.x,o.z);o.y=gy<-0.5?-0.45+Math.sin(S.t*2.2+o.wp)*0.04:gy;
    const k=Math.min(1,dt*7);o.sit+=(o.tSit-o.sit)*k;o.lie+=(o.tLie-o.lie)*k;
    if(quality>0||d<25)poseDog2(o,o.moved/Math.max(dt,1e-3),dt);
    o.g.position.set(o.x,o.y,o.z);o.g.rotation.y=o.h}
  if(NPCD.mk){const o=NPCD.mk,t=S.trust[WD.level+':'+o.id]||0;TRUSTMK.visible=true;TRUSTMK.position.set(o.x,o.y+0.9*o.D.k+0.35,o.z);const s=0.4+t*0.8;TRUSTMK.scale.set(s,s,1)}else TRUSTMK.visible=false;
  let pile=false;
  if(dog.napping){for(const o of npcDogs)if(o.st==='follow'&&o.lie>0.8&&Math.hypot(o.x-dog.x,o.z-dog.z)<1.2){pile=true;break}}
  NPCD.pile=pile;
  if(pile&&NPCD.pileDay!==S.day){NPCD.pileDay=S.day;arcade('ぽかぽか!','PUPPY PILE!','clear');hearts(10)}
  if(S.pack.length&&!S.leash&&dog.speed>0.3&&!dog.cart&&!dog.para)walkAdd(dt)}

// ---------- build the dogs (once per level)
{
  const okH=p=>p&&!bldAt(p[0],p[1])&&gridH(p[0],p[1])>=0.3,vh=p=>okH(p)?p:(groundSpot(p[0],p[1],12)||p);
  if(WD.level==='hy'||WD.level==='db'){
    let hb,hm,hbo;
    if(WD.level==='db'){hb=[PIAZ.x+7,PIAZ.z+5];hm=groundSpot(PL.auntie[0]+3,PL.auntie[1],4)||[PL.auntie[0]+3,PL.auntie[1]];hbo=groundSpot(PL.beach[0],PL.beach[1],10)||PL.beach}
    else{hb=PL.perch[Math.min(5,PL.perch.length-1)];hm=[GR.x+1.5,GR.z+0.5];hbo=groundSpot(picnic.x,picnic.z,8)||[PL.kid[0]+4,PL.kid[1]]}
    hb=vh(hb);hm=vh(hm);hbo=vh(hbo);
    mkNpcDog('biscuit','friend','Biscuit','terrier',{c:[0x4a4a52,0xb98b5a,0x5e5e66,0x26262c],collar:0x5ab4ff},hb[0],hb[1]);
    mkNpcDog('mochi','friend','Mochi 麻糬','bichon',{collar:0xd8322b},hm[0],hm[1]);
    mkNpcDog('bobo','friend','Bobo 波波','golden',{c:[0xc98a3a,0xe6b878,0xf0d09a,0xa86a26],collar:0x2f8a55},hbo[0],hbo[1])}
  if(WD.level==='db'&&DBX&&DBX.gx!==undefined){
    const gx=DBX.gx,gz=DBX.gz,v0=DBX.village[0];let w=[v0.x,v0.z];
    {const dx=395-w[0],dz=235-w[1],L=Math.hypot(dx,dz)||1;w=[w[0]+dx/L*2.5,w[1]+dz/L*2.5]}
    if(!okH(w)||Math.hypot(w[0]-gx,w[1]-gz)>=24)w=groundSpot(gx,gz,12)||[gx-3,gz-3];
    const s=vh([gx+1.9,gz+0.6]),f=groundSpot(gx,gz,14)||[gx-4,gz+3];
    mkNpcDog('wongchoi','stray','Wong Choi 旺財','lantau',{},w[0],w[1]).si=0;
    mkNpcDog('siuhak','stray','Siu Hak 小黑','lantau',{c:[0x1e1b19,0xeae6dc,0x2e2824,0x15110e]},s[0],s[1]).si=1;
    mkNpcDog('fafa','stray','Fa Fa 花花','lantau',{c:[0xd9a066,0xfaf6ee,0xf2e2c8,0x6a4a2a]},f[0],f[1]).si=2}
  if(WD.level==='hy'){
    let p=null;for(let i=0;i<12&&!p;i++){const q=groundSpot(PL.auntie[0],PL.auntie[1],7);if(q&&RMASK[cellIdx(q[0],q[1])]!==1&&!bldAt(q[0],q[1]))p=q}
    p=p||PL.auntie;mkNpcDog('lucky','stray','Lucky 幸運','lantau',{c:[0xb07a40,0xeedcbc,0xd6aa76,0x2a1f18]},p[0],p[1]).si=0}
}

"""
E('js', '// ================= State, HUD =================', SECTION + '// ================= State, HUD =================')

# ---------------------------------------------------------------- apply
def cnt(s, a):
    return s.count(a)
for part, old, new in EDITS:
    seg = head if part == 'head' else js
    assert cnt(seg, old) == 1, ('part count', part, cnt(seg, old), old[:90])
    assert cnt(src, old) == 1, ('whole count', cnt(src, old), old[:90])
for part, old, new in EDITS:
    if part == 'head':
        head = head.replace(old, new, 1)
    else:
        js = js.replace(old, new, 1)
out = head + js
tmp = tempfile.mktemp(suffix='.js')
body = js[len('<script>'):js.rfind('</script>')]
open(tmp, 'w', encoding='utf-8').write(body)
r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
os.remove(tmp)
if r.returncode:
    print(r.stderr)
    sys.exit('node --check failed')
open(P, 'w', encoding='utf-8').write(out)
print('ok: %d edits, %+d bytes' % (len(EDITS), len(out) - len(src)))
