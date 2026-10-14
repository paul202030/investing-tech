#!/usr/bin/env python3
# Player creations: ideas -> Claude (on the player's own account) -> small objects shared with every player via db.
import sys
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'genCreate' not in src, 'already transformed'
k = src.rfind('<script>'); head, c = src[:k], src[k:]

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

CSS = '''#createBtn{font-family:var(--display);font-weight:800;font-size:14px;border:none;border-radius:18px;padding:7px 14px;background:var(--gold);color:var(--ink);cursor:pointer;pointer-events:auto;box-shadow:0 2px 10px rgba(0,0,0,.25)}
#createBox{z-index:6}
#createIdea{font:inherit;font-size:16px;padding:10px;border:2px solid rgba(28,38,38,.2);border-radius:8px;background:#fffdf6;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font:inherit;font-size:13px;border:1px solid rgba(28,38,38,.25);background:transparent;border-radius:14px;padding:4px 10px;cursor:pointer;color:var(--ink)}
#createGo{font-family:var(--display);font-weight:800;font-size:17px;border:none;border-radius:10px;padding:11px;background:var(--green);color:#fff;cursor:pointer}
#createGo:disabled{opacity:.6;cursor:progress}
#createMsg{min-height:1.2em;margin:0}
</style>'''
head = R(head, '</style>', CSS)
head = R(head, '<canvas id="map" width="150" height="136" aria-label="Village map"></canvas>',
         '<canvas id="map" width="150" height="136" aria-label="Village map"></canvas>\n    <button id="createBtn" type="button">✨ Create</button>')
head = R(head, '<div id="arcade" aria-hidden="true">', '''<div id="createBox" class="lost" hidden><div class="mapCard"><div class="mapHead"><b>Create something ✨</b><button id="createClose" type="button">Close</button></div>
<p class="small">Describe one thing to add to this village. Claude builds it using your own Claude account, and it stays here for every player to find.</p>
<input id="createIdea" maxlength="120" placeholder="e.g. a giant bouncing mango" autocomplete="off">
<div class="chips"><button type="button" class="chip">a flying siu mai</button><button type="button" class="chip">a tiny red taxi that makes you tiny</button><button type="button" class="chip">a disco egg tart</button><button type="button" class="chip">a lucky golden cat</button></div>
<button id="createGo" type="button">Make it</button><p id="createMsg" class="small" role="status" aria-live="polite"></p></div></div>
<div id="arcade" aria-hidden="true">''')
head = R(head, '<kbd>Q or tap the map</kbd>', '<kbd>N or ✨ Create</kbd><span>Describe a new thing for the village; Claude builds it and every player can find it</span>\n      <kbd>Q or tap the map</kbd>')

# capabilities resolved once, outside levels
c = R(c, "let ROOM=null;try{", "let DBCAP=null,SAMP=null;try{if(window.claude&&typeof window.claude.use==='function'){window.claude.use('db').then(r=>{DBCAP=r}).catch(()=>{});window.claude.use('sample').then(r=>{SAMP=r}).catch(()=>{})}}catch(e){}\nlet ROOM=null;try{")

GEN = r'''  for(const [id,o] of MP.dogs)if(!seen.has(id)){scene.remove(o.D.root);if(o.cart)scene.remove(o.cart.g);MP.dogs.delete(id)}}
// ================= Player creations: ideas built by Claude on the player's own account, shared through db =================
const GEN={ids:new Set(),items:[],unsub:null,busy:false,lastAt:0};
const GSH=['box','sphere','cyl','cone'],GMOVE=['none','bounce','float','spin'],GFX=['none','giant','tiny','zoom','rain','party'];
function gStr(v,n){return typeof v==='string'?v.replace(/[\u0000-\u001f<>]/g,'').trim().slice(0,n):''}
function cleanSpec(s){if(!s||typeof s!=='object')return null;const num=(v,a,b,d)=>{v=+v;return isFinite(v)?clamp(v,a,b):d};
  const parts=(Array.isArray(s.parts)?s.parts:[]).slice(0,14).map(p=>p&&GSH.includes(p.s)&&/^#[0-9a-fA-F]{6}$/.test(p.c)?{s:p.s,c:p.c,x:num(p.x,-0.9,0.9,0),y:num(p.y,0,1.7,0.2),z:num(p.z,-0.9,0.9,0),
    sx:num(p.sx,0.02,1.6,0.2),sy:num(p.sy,0.02,1.6,0.2),sz:num(p.sz,0.02,1.6,0.2),rx:num(p.rx,-180,180,0),ry:num(p.ry,-180,180,0),rz:num(p.rz,-180,180,0)}:null).filter(Boolean);
  if(!parts.length)return null;const name=gStr(s.name,28)||'Mystery thing';
  return {name,zh:gStr(s.zh,8),label:gStr(s.label,40)||('a '+name),line:gStr(s.line,90),move:GMOVE.includes(s.move)?s.move:'none',effect:GFX.includes(s.effect)?s.effect:'none',parts}}
function genMake(spec,g){for(const p of spec.parts){const ma=mat(new THREE.Color(p.c).getHex());let m;
    if(p.s==='box')m=new THREE.Mesh(new THREE.BoxGeometry(p.sx,p.sy,p.sz),ma);else if(p.s==='sphere'){m=new THREE.Mesh(SPH,ma);m.scale.set(p.sx/2,p.sy/2,p.sz/2)}
    else if(p.s==='cyl')m=new THREE.Mesh(new THREE.CylinderGeometry(p.sx/2,p.sx/2,p.sy,12),ma);else m=new THREE.Mesh(new THREE.ConeGeometry(p.sx/2,p.sy,12),ma);
    m.position.set(p.x,p.y,p.z);m.rotation.set(p.rx*Math.PI/180,p.ry*Math.PI/180,p.rz*Math.PI/180);m.castShadow=true;g.add(m)}}
function genType(id,spec){const key='gen_'+id;if(!ITYPES[key]){let md=0.2,top=0.2;for(const p of spec.parts){md=Math.max(md,Math.abs(p.x)+p.sx/2,Math.abs(p.z)+p.sz/2);top=Math.max(top,p.y+p.sy/2)}
    ITYPES[key]={label:spec.label,r:0.02,gen:spec,carryS:Math.min(1,0.5/Math.max(md,top/2)),top,make(g){genMake(spec,g)}}}return key}
function genSpawn(id,d,local){if(GEN.ids.has(id)||GEN.items.length>=70)return null;const spec=cleanSpec(d&&d.spec);if(!spec||d.lv!==WD.level||!isFinite(d.x)||!isFinite(d.z))return null;GEN.ids.add(id);
  const x=clamp(+d.x,X0+20,X1-20),z=clamp(+d.z,Z0+20,Z1-20);const it=addItem(genType(id,spec),x,z);it.by=gStr(d.by,14)||'someone';it.ph=Math.random()*6;it.tag={g:it.g,headY:it.T.top+0.35};it.tagT=Math.random();GEN.items.push(it);return it}
function genListen(){if(GEN.unsub||!DBCAP)return;GEN.unsub=()=>{};try{GEN.unsub=DBCAP.collection('creations').orderBy('t','desc').limit(200).onSnapshot(snap=>{for(const ch of snap.docChanges())if(ch.type==='added'){const d=ch.doc.data();if(d)genSpawn(ch.doc.id,d)}},()=>{})||(()=>{})}catch(e){}}
function genPickup(it){const s=it.T.gen;S.points+=10;toast('✨ '+s.name+(s.zh?' '+s.zh:'')+', made by '+it.by+'.');if(s.line)say(DOGTALK,s.line,3.2);
  if(it.fxAt&&S.t-it.fxAt<60)return;it.fxAt=S.t;
  if(s.effect==='giant'||s.effect==='tiny'){dog.scaleTo=s.effect==='giant'?2.2:0.45;dog.scaleT=20;sfx.tada()}
  else if(s.effect==='zoom'){dog.zoomT=15;arcade('はやい!','ZOOM!','run')}
  else if(s.effect==='party'){arcade('パーティー!','PARTY!','clear');sfx.tada();hearts(20);for(const p of people())if(personNear(p,25))p.patT=3}
  else if(s.effect==='rain'){let n=0;for(const o of items)if(o.rainCopy)n++;for(let i=0;i<10&&n<40;i++,n++){const a=Math.random()*6.28,r=2+Math.random()*7;const x=dog.x+Math.cos(a)*r,z=dog.z+Math.sin(a)*r;if(bldAt(x,z))continue;
      const o=addItem(it.type,x,z);o.rainCopy=true;o.by=it.by;o.state='fly';o.vx=0;o.vz=0;o.vy=0;o.y+=10+Math.random()*6;o.g.position.y=o.y}toast('It\'s raining '+s.name.toLowerCase()+'!')}}
function genUpd(dt){genListen();
  if(dog.scaleT>0){dog.scaleT-=dt;if(dog.scaleT<=0)dog.scaleTo=1}const sc=D.root.scale.x,tg=dog.scaleTo||1;if(Math.abs(sc-tg)>0.001)D.root.scale.setScalar(lerp(sc,tg,Math.min(1,dt*3)));if(dog.zoomT>0)dog.zoomT-=dt;
  for(const it of GEN.items){if(it.state==='ground'&&it.T.gen){const m=it.T.gen.move;it.ph+=dt;
      if(m==='bounce')it.g.position.y=it.y+Math.abs(Math.sin(it.ph*3))*0.4;else if(m==='float')it.g.position.y=it.y+0.5+Math.sin(it.ph*1.5)*0.15;if(m==='spin')it.g.rotation.y+=dt*1.6;
      it.tagT-=dt;if(it.tagT<=0){it.tagT=1;if(Math.hypot(it.x-dog.x,it.z-dog.z)<16)say(it.tag,'✨ '+it.T.gen.name,1.1)}}}}
function genPrompt(idea){return 'You design ONE small object for a cute, low-poly 3D browser game where you play a golden retriever in '+WD.name+', Hong Kong. Everyone who plays will see it, so keep it friendly, a little funny and not too weird: no violence, nothing gross or scary, no real brands or real people.\n'+
  'Player\'s idea: """'+idea.slice(0,120).replace(/"/g,"'")+'"""\n'+
  'Reply with ONLY a JSON object:\n{"name": "short name, max 28 chars", "zh": "optional Chinese name, max 8 chars", "label": "how the game mentions it, e.g. a giant bouncing mango (max 40 chars)", '+
  '"line": "one cheerful sentence the dog thinks when picking it up, max 80 chars", "move": "none" | "bounce" | "float" | "spin", '+
  '"effect": "none" | "giant" | "tiny" | "zoom" | "rain" | "party", "parts": [2 to 14 simple shapes that together look like the idea]}\n'+
  'effect = what happens to the dog that picks it up: giant or tiny dog for 20 s, zoom = super speed for 15 s, rain = copies fall from the sky, party = everyone nearby cheers. Choose what fits the idea; "none" is fine.\n'+
  'Each part: {"s": "box"|"sphere"|"cyl"|"cone", "c": "#rrggbb", "x","y","z": centre in metres (y is up; the object stands on y=0), "sx","sy","sz": size in metres (sphere, cyl and cone: sx = diameter, sy = height), "rx","ry","rz": optional rotation in degrees}. '+
  'The whole object must fit inside 1.6 x 1.6 x 1.6 m. Use bright, friendly colours.'}
const cBox=$('#createBox'),cMsg=$('#createMsg'),cIdea=$('#createIdea'),cGo=$('#createGo');
function openCreate(){if(!S.started||S.leaving)return;cBox.hidden=false;cMsg.textContent=SAMP?'':'Creating needs Claude: open the game signed in to claude.ai. You can still find what other players made.';setTimeout(()=>cIdea.focus(),50)}
function closeCreate(){cBox.hidden=true;cIdea.blur()}
async function genCreate(){const idea=gStr(cIdea.value,120);if(!idea){cMsg.textContent='Type an idea first.';return}if(!SAMP){cMsg.textContent='Creating needs Claude: open the game signed in to claude.ai.';return}
  if(GEN.busy)return;const wait=Math.ceil((GEN.lastAt+90000-Date.now())/1000);if(wait>0){cMsg.textContent='One creation every 90 seconds: try again in '+wait+' s.';return}
  GEN.busy=true;cGo.disabled=true;cMsg.textContent='Claude is building it… (the first time, Claude asks if this game may use your account)';
  try{const spec=cleanSpec(await SAMP.json(genPrompt(idea),{modelTier:'quick',cache:false}));if(!spec)throw {code:'bad_shape'};
    const id=Date.now().toString(36)+Math.random().toString(36).slice(2,7);const d={lv:WD.level,x:+(dog.x+Math.sin(dog.heading)*2.4).toFixed(2),z:+(dog.z+Math.cos(dog.heading)*2.4).toFixed(2),spec,by:S.name,t:Date.now()};
    genSpawn(id,d);GEN.lastAt=Date.now();arcade('できた!','CREATED!','clear');sfx.tada();S.points+=30;complete('create');
    let saved=false;if(DBCAP){try{await DBCAP.collection('creations').doc(id).set(d);saved=true}catch(e){}}
    cMsg.textContent=saved?spec.name+' is in the village now, for every player.':spec.name+' is here, but only for you this time (it couldn\'t be saved).';setTimeout(closeCreate,1600)}
  catch(e){const code=e&&e.code;cMsg.textContent=code==='not_granted'?'Claude wasn\'t allowed, so nothing was made.':code==='rate_limited'?'Your Claude account is busy or out of messages right now. Try again later.':'That idea didn\'t work out. Try describing it differently.'}
  finally{GEN.busy=false;cGo.disabled=false}}
$('#createBtn').addEventListener('click',()=>openCreate());$('#createClose').addEventListener('click',closeCreate);cGo.addEventListener('click',()=>genCreate());
cIdea.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();genCreate()}else if(e.key==='Escape')closeCreate()});
cBox.addEventListener('pointerdown',e=>{if(e.target===cBox)closeCreate()});for(const ch of cBox.querySelectorAll('.chip'))ch.addEventListener('click',()=>{cIdea.value=ch.textContent;cIdea.focus()});'''
c = R(c, "  for(const [id,o] of MP.dogs)if(!seen.has(id)){scene.remove(o.D.root);if(o.cart)scene.remove(o.cart.g);MP.dogs.delete(id)}}", GEN)
c = R(c, "if(dbUpd)dbUpd(dt);mpUpd(dt);", "if(dbUpd)dbUpd(dt);mpUpd(dt);genUpd(dt);")
c = R(c, "function destroy(){dead=true;", "function destroy(){dead=true;try{if(GEN.unsub)GEN.unsub()}catch(e){}cBox.hidden=true;")
# pickup, carry size, no stashing, zoom
c = R(c, "it.state='dog';dog.item=it;sfx.ding();", "it.state='dog';dog.item=it;sfx.ding();if(it.T.gen){it.g.scale.setScalar(it.T.carryS);genPickup(it)}")
c = R(c, "if(Math.hypot(BED.x-dog.x,BED.z-dog.z)<1.8){dog.item=null;", "if(!it.T.gen&&Math.hypot(BED.x-dog.x,BED.z-dog.z)<1.8){dog.item=null;")
c = R(c, "it.yaw=dog.heading+Math.PI/2;it.g.position.set(it.x,it.y,it.z);", "it.yaw=dog.heading+Math.PI/2;if(it.T.gen)it.g.scale.setScalar(1);it.g.position.set(it.x,it.y,it.z);")
c = R(c, "*Math.min(1,mag*1.25)}", "*Math.min(1,mag*1.25)*(dog.zoomT>0?1.8:1)}")
c = R(c, "else if(k==='x')doCtx();", "else if(k==='x')doCtx();else if(k==='n'){e.preventDefault();openCreate()}")
c = R(c, "['police','Outrun the police in a golf cart']]", "['police','Outrun the police in a golf cart'],['create','Create something new for the village (✨ Create)']]")

open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok')
