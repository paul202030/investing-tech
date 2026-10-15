#!/usr/bin/env python3
# Third level: Discovery Bay North (data/discovery-bay-north/world.json), bus destination picker, DB-wide rules via WD.dbish.
import sys,json
G='/home/user/investing-tech/games/ha-yeung-dog-days/'
s=open(G+'index.html',encoding='utf-8').read();assert 'worldDataDBN' not in s
def R(o,n,cnt=1):
    global s;assert s.count(o)==cnt,(s.count(o),o[:100]);s=s.replace(o,n)
# embed the world
i=s.index('id="worldDataDB">');j=s.index('</script>',i)+len('</script>')
dbn=json.dumps(json.load(open(G+'data/discovery-bay-north/world.json')),separators=(',',':'),ensure_ascii=False).replace('</','<\\/')
s=s[:j]+'\n<script type="application/json" id="worldDataDBN">'+dbn+'</script>'+s[j:]
# bus picker markup
R('<div id="arcade" aria-hidden="true">','<div id="busBox" class="lost" hidden><div class="mapCard"><div class="mapHead"><b>Where to? 🚌</b><button id="busClose" type="button">Close</button></div><div id="busBtns"></div></div></div>\n<div id="arcade" aria-hidden="true">')
R('#boothBtns{display:flex;gap:8px;flex-wrap:wrap}','#boothBtns,#busBtns{display:flex;gap:8px;flex-wrap:wrap}\n#busBox{z-index:6}\n#busBtns button{font-family:var(--display);font-weight:800;font-size:17px;border:none;border-radius:10px;padding:12px 16px;background:var(--green);color:#fff;cursor:pointer}')
k=s.rfind('<script>');head,c=s[:k],s[k:]
def C(o,n,cnt=1):
    global c;assert c.count(o)==cnt,(c.count(o),o[:100]);c=c.replace(o,n)
C("const LEVELS={hy:'worldData',db:'worldDataDB'};","const LEVELS={hy:'worldData',db:'worldDataDB',dbn:'worldDataDBN'};")
C("const OTHER=WD.level==='db'?'hy':'db',OTHERNAME=OTHER==='db'?'Discovery Bay':'Ha Yeung';",
  "const LNAME={hy:'Ha Yeung',db:'Discovery Bay',dbn:'Discovery Bay North'},DESTS={hy:['db'],db:['hy','dbn'],dbn:['db']}[WD.level]||['hy'],OTHER=DESTS[0],OTHERNAME=DESTS.map(d=>LNAME[d]).join(' / ');WD.dbish=WD.level==='db'||WD.level==='dbn';")
C("LV=buildLevel(data.level==='db'?'db':'hy',data,false)","LV=buildLevel(LEVELS[data.level]?data.level:'hy',data,false)")
# DB-wide rules
C("WD.level==='db'?0xdcb775:0xe2cf9e","WD.dbish?0xdcb775:0xe2cf9e")
C("const SMAT={};\nif(WD.level==='db'){","const SMAT={};\nif(WD.dbish){")
C("if(WD.level==='db'){taxi.wait=Infinity;mini.wait=Infinity}","if(WD.dbish){taxi.wait=Infinity;mini.wait=Infinity}")
C("const aiCarts=WD.level==='db'?","const aiCarts=WD.dbish?")
C("const police=WD.level==='db'?","const police=WD.dbish?")
C("function misCan(){const db=WD.level==='db';","function misCan(){const db=WD.dbish;")
C("const DBX=WD.level==='db'?dbPrep():null;","const DBX=WD.dbish?dbPrep():null;")
C("(WD.level==='db'?'runs the café at the plaza'","(WD.dbish?'runs the café at the plaza'")
# site-specific DB parts stay in DB
C("function dbPrep(){const X={village:[]};","function dbPrep(){const X={village:[]};const SITE=WD.level==='db';")
C("  // the piazza: one level terrace","  if(SITE){\n  // the piazza: one level terrace")
C("  for(const p of DECK)NOTREE.push([p[0],p[1],7]);","  for(const p of DECK)NOTREE.push([p[0],p[1],7]);}")
C("let pier=null,pd=1e9;for(const b of WD.bld){","let pier=null,pd=1e9;if(SITE)for(const b of WD.bld){")
C("  const cove=[395,235];const cand=[];","  const cove=[395,235];const cand=[];if(SITE)")
C("function dbDecor(X){const ups=[];","function dbDecor(X){const ups=[];const SITE=WD.level==='db';")
C("  drape((x,z)=>(x>-22","  if(SITE)drape((x,z)=>(x>-22")
C("  drape((x,z)=>segDist(x,z,DECK)","  if(SITE)drape((x,z)=>segDist(x,z,DECK)")
C("  wallSign(PIAZ.x,PIAZ.z+12,","  if(!SITE)wallSign(PL.door[0],PL.door[1],'愉景北商場  DB NORTH PLAZA','#f6efdf','#2d6fa5',12,4.2);\n  if(SITE)wallSign(PIAZ.x,PIAZ.z+12,")
C("  wallSign(64,-96,","  if(SITE)wallSign(64,-96,")
C("py=gridH(PIAZ.x,PIAZ.z);{const f=","py=gridH(PIAZ.x,PIAZ.z);if(SITE){const f=")
C("  ups.push(dt=>{if(Math.hypot(dog.x-PIAZ.x","  if(SITE)ups.push(dt=>{if(Math.hypot(dog.x-PIAZ.x")
C("  for(let i=0;i<10;i++){const a=i/10*Math.PI*2+0.3;","  if(SITE)for(let i=0;i<10;i++){const a=i/10*Math.PI*2+0.3;")
C("  for(let i=0;i<DECK.length-1;i++){const a=DECK[i],b=DECK[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);let nx","  if(SITE)for(let i=0;i<DECK.length-1;i++){const a=DECK[i],b=DECK[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);let nx")
C("  {const rail=[],boll=[],tables=[];let acc=0;","  if(SITE){const rail=[],boll=[],tables=[];let acc=0;")
C("if(DBX){PLACES.push(['Plaza'","if(DBX&&WD.level==='db'){PLACES.push(['Plaza'")
# bus: destination picker
C("function boardBus(){","function boardBus(){if(DESTS.length>1){busPick();return}rideBus(DESTS[0])}\nfunction busPick(){const el=$('#busBtns');el.textContent='';for(const d of DESTS){const b=document.createElement('button');b.type='button';b.textContent='🚌 '+LNAME[d];b.addEventListener('click',()=>{$('#busBox').hidden=true;rideBus(d)});el.appendChild(b)}$('#busBox').hidden=false}\nfunction rideBus(dest){")
C("'Taking the bus to '+OTHERNAME+'…');setTimeout(()=>{if(!dead)switchLevel(OTHER,snapshot())},900)}","'Taking the bus to '+LNAME[dest]+'…');setTimeout(()=>{if(!dead)switchLevel(dest,snapshot())},900)}")
C("function destroy(){dead=true;","function destroy(){dead=true;$('#busBox').hidden=true;")
C("const bBox=$('#boothBox');","$('#busClose').addEventListener('click',()=>{$('#busBox').hidden=true});\nconst bBox=$('#boothBox');")
# welcome toasts and a to-do
C("  if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name","  if(WD.level==='dbn'){toast('Welcome to Discovery Bay North, '+S.name+'! North Plaza is by the water and Sam Pak Wan beach is up the coast.');toast('Golf carts are parked around. The bus goes back to Discovery Bay.')}\n  else if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name")
C("toast(WD.level==='db'?'Welcome to Discovery Bay!","toast(WD.level==='dbn'?'Welcome to Discovery Bay North! North Plaza is right by the water; Sam Pak Wan beach is up the coast.':WD.level==='db'?'Welcome to Discovery Bay!")
C("complete('bus')}","complete('bus');if(WD.level==='dbn')complete('north')}")
C("['para','Jump out of a flying machine and paraglide down']]","['para','Jump out of a flying machine and paraglide down'],['north','Take the bus to Discovery Bay North']]")
open(sys.argv[1] if len(sys.argv)>1 else G+'index.html','w',encoding='utf-8').write(head+c);print('ok')
