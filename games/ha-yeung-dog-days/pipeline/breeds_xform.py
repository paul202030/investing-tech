#!/usr/bin/env python3
"""Ha Yeung Dog Days, unit 1/5: playable border terrier and Lantau street dog (唐狗).

  python3 pipeline/breeds_xform.py

- makeDog(breed,o): breed table (BREEDS / BREED_IDS), wire coat, fold or prick ears, pink collar, leash point,
  lite + shared-material options (o.lite, o.mc, o.c, o.collar) for cheap NPC dogs in later units.
- Shared per-level dog resources (DLEG, COLLAR_G, dogMat cache) next to SPH.
- Start card radios, breed validation (save data, __BOOT, multiplayer), voice pitch, camera, speech bubbles,
  mouth points, breed-aware lines and the terrier / 唐狗 perks.
Exact str.replace edits; each anchor must occur exactly once in its part and in the whole file. Refuses to run twice.
"""
import os, re, subprocess, sys, tempfile

G = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
P = G + 'index.html'
src = open(P, encoding='utf-8').read()
MARK = 'const BREED_IDS='
assert MARK not in src, 'breeds_xform already applied'

EDITS = []  # (part, old, new)
def E(part, old, new):
    EDITS.append((part, old, new))

# ---------------------------------------------------------------- A. shared per-level dog resources
E('js', "const SPH=new THREE.SphereGeometry(1,14,10);",
  "const SPH=new THREE.SphereGeometry(1,14,10);\n"
  "const DLEG=[new THREE.CylinderGeometry(0.068,0.056,0.3,8),new THREE.CylinderGeometry(0.09,0.056,0.3,8),new THREE.CylinderGeometry(0.05,0.044,0.24,8)],COLLAR_G=new THREE.TorusGeometry(0.165,0.026,6,16),DOGMATS=new Map();\n"
  "function dogMat(c,basic){const key=(basic?'b':'l')+c;let m=DOGMATS.get(key);if(!m){m=basic?new THREE.MeshBasicMaterial({color:c}):mat(c);m.userData.shared=true;DOGMATS.set(key,m)}return m}")

# ---------------------------------------------------------------- B. breed table
BREED_TABLE = (
  "const BREED_IDS=['golden','bichon','terrier','lantau'];\n"
  "const BREEDS={\n"
  "  golden:{k:1,c:[0xd59a42,0xecc488,0xf4d9a6,0xb8792e],nose:0.31,mouthZ:0.27,tailUp:0,pitch:1,coat:'feather',ears:'drop',collar:0,name:'golden retriever',sh:'golden',fb:'golden furball',bark:'Woof! Woof!',pat:['Look at that golden fur!'],pic:'Golden retriever! So fluffy!'},\n"
  "  bichon:{k:0.62,c:[0xf6f2ea,0xffffff,0xfbf7ef,0xece5d8],nose:0.19,mouthZ:0.17,tailUp:0.9,pitch:1.2,coat:'feather',ears:'drop',collar:0,name:'bichon frise',sh:'bichon',fb:'little cotton ball',bark:'Woof! Woof!',pat:['Like a little cloud!'],pic:'Ay, parang bulak! Like cotton!'},\n"
  # border terrier: tan grizzle body, tan legs, wiry tufts, dark grizzle ears/saddle; hot-pink collar
  "  terrier:{k:0.62,c:[0xa8784e,0xc99d6e,0x8a6a4c,0x3b3530],nose:0.25,mouthZ:0.21,tailUp:0.6,pitch:1.45,coat:'wire',ears:'fold',collar:0xff4fa3,name:'border terrier',sh:'terrier',fb:'scruffy little terrier',bark:'Yap! Yap!',pat:['Look at that little beard!','Scruffy otter face! 好可愛!'],pic:'Ay, a little terrier! Ang cute!'},\n"
  # Lantau street dog: fawn, cream chest/socks, black mask (furD), prick ears with the vet's ear-tip nick, sickle tail
  "  lantau:{k:0.84,c:[0xc68a4a,0xf0dcc0,0xe2b886,0x2a1f18],nose:0.29,mouthZ:0.25,tailUp:1.15,pitch:0.82,coat:'short',ears:'prick',collar:0,name:'Lantau street dog (唐狗)',sh:'唐狗',fb:'cheeky 唐狗',bark:'Wuff! Wuff!',pat:['唐狗 are the best dogs!','Good village dog! 好乖!'],pic:'Village doggy! Come, come!'}};\n"
  "function breedInfo(b){if(b===undefined)b=S.breed;return BREEDS[BREED_IDS.includes(b)?b:'golden']}\n"
  "function breedHello(){if(S.breed==='terrier')toast('Border terriers were bred to dig: you dig faster, smell treasure from further away and catch the cat quicker. Yap!');"
  "else if(S.breed==='lantau')toast('You are a free Lantau street dog (唐狗). That little nick in your ear means a kind vet looked after you.')}\n")
E('js', "function makeDog(breed){", BREED_TABLE + "function makeDog(breed){")

# ---------------------------------------------------------------- C. makeDog(breed,o)
# C1 header
E('js', "function makeDog(breed){const B=breed==='bichon',K=B?0.62:1;",
  "function makeDog(breed,o){o=o||{};const id=BREED_IDS.includes(breed)?breed:'golden',BR=BREEDS[id],B=id==='bichon',T=id==='terrier',L=id==='lantau',K=BR.k,C=o.c||BR.c,lite=!!o.lite,feather=BR.coat==='feather'&&!lite,M=o.mc?(c=>dogMat(c)):mat;")
# C2 materials
E('js', "const fur=mat(B?0xf6f2ea:0xd59a42),furL=mat(B?0xffffff:0xecc488),furF=mat(B?0xfbf7ef:0xf4d9a6),furD=mat(B?0xece5d8:0xb8792e),dark=mat(0x16100c),eyeM=mat(0x3b2414),pink=mat(0xd0706e),shine=new THREE.MeshBasicMaterial({color:0xffffff});",
  "const fur=M(C[0]),furL=M(C[1]),furF=M(C[2]),furD=M(C[3]),dark=M(0x16100c),eyeM=M(0x3b2414),pink=M(0xd0706e),shine=o.mc?dogMat(0xffffff,true):new THREE.MeshBasicMaterial({color:0xffffff});")
# C3 lean barrel for the village dog
E('js', "sph(fur,0.25,0.26,0.46,0,0.04,0.34,hip);",
  "sph(fur,L?0.21:0.25,L?0.23:0.26,L?0.44:0.46,0,0.04,0.34,hip);")
# C4 feathering only on feathered coats (not lite)
E('js', "for(let i=0;i<5;i++)sph(furF,0.075,", "if(feather)for(let i=0;i<5;i++)sph(furF,0.075,")
E('js', "for(const s of [1,-1])sph(furL,0.1,0.15,0.12,0.13*s,-0.07,-0.12,hip);",
  "if(feather)for(const s of [1,-1])sph(furL,0.1,0.15,0.12,0.13*s,-0.07,-0.12,hip);")
# C5 muzzle chain (bichon branch kept as is)
TERRIER_HEAD = ("else if(T){sph(fur,0.165,0.12,0.15,0,0.05,-0.01,head);sph(furL,0.085,0.075,0.11,0,-0.03,0.12,head);sph(furD,0.06,0.05,0.05,0,-0.02,0.19,head);"
  "sph(furF,0.065,0.055,0.06,0,-0.09,0.15,head);"
  "for(const s of [1,-1]){sph(furF,0.035,0.03,0.035,0.05*s,-0.05,0.18,head);sph(furF,0.04,0.022,0.035,0.06*s,0.11,0.12,head)}"
  "sph(furD,0.235,0.17,0.43,0,0.14,0.3,hip);"
  "if(!lite)for(let i=0;i<3;i++)sph(furF,0.05,0.035,0.055,(i%2?0.07:-0.07),0.285,0.14+i*0.17,hip)}")
LANTAU_HEAD = "else if(L){sph(furL,0.072,0.066,0.155,0,-0.02,0.145,head);sph(furD,0.074,0.058,0.085,0,-0.012,0.215,head)}"
E('js', "else sph(furL,0.088,0.078,0.17,0,-0.02,0.15,head);",
  TERRIER_HEAD + LANTAU_HEAD + "else sph(furL,0.088,0.078,0.17,0,-0.02,0.15,head);")
# C6 nose
E('js', "sph(dark,0.045,0.038,0.035,0,0.02,B?0.19:0.31,head);", "sph(dark,0.045,0.038,0.035,0,0.02,BR.nose,head);")
# C7 no eye shine on lite rigs
E('js', "const h=sph(shine,0.007,0.007,0.005,0.006*s,0.009,0.017,e);h.castShadow=false;",
  "if(!lite){const h=sph(shine,0.007,0.007,0.005,0.006*s,0.009,0.017,e);h.castShadow=false}")
# C8 shorter terrier jaw
E('js', "sph(furL,0.072,0.03,0.13,0,-0.005,0.1,jaw);const tongue=sph(pink,0.045,0.012,0.085,0,0.012,0.16,jaw);",
  "sph(furL,0.072,0.03,T?0.085:0.13,0,-0.005,T?0.06:0.1,jaw);const tongue=sph(pink,0.045,0.012,0.085,0,0.012,T?0.1:0.16,jaw);")
# C9 ears: fold (terrier), prick with the ear-tip nick (lantau), drop (golden, bichon)
E('js', "sph(furD,0.042,0.14,0.1,0.025*s,-0.1,0.02,e);sph(fur,0.036,0.07,0.085,0.03*s,-0.21,0.02,e);e.rotation.z=0.18*s;ears.push(e)}",
  "if(T){const eb=new THREE.Group();eb.position.set(0.04*s,0.04,0.04);eb.rotation.set(-0.9,0.7*s,-0.2*s);e.add(eb);sph(furD,0.045,0.07,0.018,0,-0.055,0,eb)}"
  "else if(L){const eb=new THREE.Group();eb.position.set(0.005*s,0.02,0);eb.rotation.z=-0.15*s;e.add(eb);const em=sph(fur,0.045,0.11,0.028,0,0.09,0,eb);sph(furL,0.022,0.07,0.012,0,0.08,0.014,eb);if(s===1){em.scale.y=0.092;em.position.y=0.082}}"
  "else{sph(furD,0.042,0.14,0.1,0.025*s,-0.1,0.02,e);sph(fur,0.036,0.07,0.085,0.03*s,-0.21,0.02,e)}"
  "e.rotation.z=0.18*s;ears.push(e)}")
# C10 legs on shared geometry (same 0.56 hip-unit length), feathering only on feathered coats
E('js', "cyl(fur,front?0.068:0.09,0.056,0.3,0,-0.14,0,up);",
  "{const lm=new THREE.Mesh(DLEG[front?0:1],fur);lm.position.y=-0.14;lm.castShadow=true;up.add(lm)}")
E('js', "if(front)sph(furF,0.035,0.13,0.05,0,-0.17,-0.06,up);else sph(furF,0.045,0.12,0.05,0,-0.12,-0.08,up);",
  "if(feather){if(front)sph(furF,0.035,0.13,0.05,0,-0.17,-0.06,up);else sph(furF,0.045,0.12,0.05,0,-0.12,-0.08,up)}")
E('js', "cyl(furL,0.05,0.044,0.24,0,-0.11,0,kn);",
  "{const lm=new THREE.Mesh(DLEG[2],furL);lm.position.y=-0.11;lm.castShadow=true;kn.add(lm)}")
# C11 tail: terrier carrot, lantau sickle curl, plume only on feathered coats
E('js', "for(let i=0;i<5;i++){const g=new THREE.Group();g.position.y=i?0.1:0;g.rotation.x=i?0.08:0;p.add(g);sph(fur,0.042-i*0.004,0.07,0.042-i*0.004,0,0.05,0,g);sph(furF,0.032+i*0.006,0.068,0.05+i*0.012,0,0.05,-0.035-i*0.008,g);tsegs.push(g);p=g}",
  "for(let i=0;i<5;i++){const g=new THREE.Group();g.position.y=i?(T?0.065:0.1):0;g.rotation.x=i?(L?0.38:0.08):0;p.add(g);"
  "if(T)sph(i>=3?furD:fur,0.05-i*0.007,0.06,0.05-i*0.007,0,0.04,0,g);else sph(fur,0.042-i*0.004,0.07,0.042-i*0.004,0,0.05,0,g);"
  "if(feather)sph(furF,0.032+i*0.006,0.068,0.05+i*0.012,0,0.05,-0.035-i*0.008,g);tsegs.push(g);p=g}")
# C12 collar + tag (terrier pink by default, o.collar overrides, 0 = none) and the leash clip point at the back of the collar
E('js', "sph(fur,0.15,0.24,0.16,0,0.12,0,neck);sph(furL,0.145,0.2,0.13,0,0.03,0.07,neck);",
  "sph(fur,0.15,0.24,0.16,0,0.12,0,neck);sph(furL,0.145,0.2,0.13,0,0.03,0.07,neck);"
  "const cc=o.collar!==undefined?o.collar:BR.collar;if(cc){const cm=new THREE.Mesh(COLLAR_G,o.mc?dogMat(cc):mat(cc,{emissive:0x3a0d22}));cm.position.set(0,0.11,0.02);cm.rotation.x=Math.PI/2;cm.castShadow=true;neck.add(cm);"
  "sph(o.mc?dogMat(0xe0b040):mat(0xe0b040),0.03,0.035,0.012,0,0.06,0.205,neck)}"
  "const leashPt=new THREE.Object3D();leashPt.position.set(0,0.11,-0.17);neck.add(leashPt);")
# C13 lite: no shadows; richer return
E('js', "return {root,hip,neck,head,jaw,tongue,eyes,ears,legs,tail,tsegs,k:K,tailUp:B?0.9:0,breed:B?'bichon':'golden'}}",
  "if(lite)root.traverse(m=>{if(m.isMesh)m.castShadow=false});"
  "return {root,hip,neck,head,jaw,tongue,eyes,ears,legs,tail,tsegs,k:K,tailUp:BR.tailUp,breed:id,leashPt,pitch:BR.pitch,mouthZ:BR.mouthZ,prick:L,mats:{fur,furL}}}")

# ---------------------------------------------------------------- D. prick ears perk forward on bark and sniff
E('js', "D.ears.forEach((e,i)=>{e.rotation.x=-flap*0.9+Math.sin(dog.phase*2)*0.15*flap;e.rotation.z=(i?-1:1)*(0.18+P.bark*0.2)});",
  "D.ears.forEach((e,i)=>{if(D.prick){e.rotation.x=P.sniff*0.35+P.bark*0.25+Math.sin(dog.phase*2)*0.04*flap;e.rotation.z=(i?-1:1)*0.05}"
  "else{e.rotation.x=-flap*0.9+Math.sin(dog.phase*2)*0.15*flap;e.rotation.z=(i?-1:1)*(0.18+P.bark*0.2)}});")

# ---------------------------------------------------------------- E. breed plumbing
E('js', "breed:(BOOT&&BOOT.breed)||'golden'", "breed:BREED_IDS.includes(BOOT&&BOOT.breed)?BOOT.breed:'golden'")
E('js', "if(!Array.isArray(S.stash))S.stash=[];", "if(!BREED_IDS.includes(S.breed))S.breed='golden';if(!Array.isArray(S.stash))S.stash=[];")
E('js', "$('#dogName').value=S.name;", "$('#dogName').value=S.name;{const r=document.querySelector('input[name=breed][value='+S.breed+']');if(r)r.checked=true}")
E('js', "const br=(document.querySelector('input[name=breed]:checked')||{}).value==='bichon'?'bichon':'golden';",
  "const v=(document.querySelector('input[name=breed]:checked')||{}).value,br=BREED_IDS.includes(v)?v:'golden';")
E('js', "scene.remove(r);", "scene.remove(r);r.traverse(m=>{if(m.isMesh&&m.material&&!m.material.userData.shared)m.material.dispose()});")

# ---------------------------------------------------------------- F. voice, camera, speech, mouth
E('js', "bark(){if(!ac)return;const base=290*(0.92+Math.random()*0.16);", "bark(p){if(!ac)return;const base=290*(p||1)*(0.92+Math.random()*0.16);")
E('js', "dog.barkT=0.45;sfx.bark();", "dog.barkT=0.45;sfx.bark(D.pitch);")
E('js', "bbq.inRange=false;sfx.bark();", "bbq.inRange=false;sfx.bark(D.pitch);")  # the steal bark is the player's dog too
E('js', "say(DOGTALK,'Woof! Woof!',1.2);dropBall();", "say(DOGTALK,breedInfo().bark,1.2);dropBall();")
E('js', "const DOGTALK={headY:1.0,get g(){return D.root}};", "const DOGTALK={get headY(){return 0.45+0.55*D.k},get g(){return D.root}};")
E('js', "const tgt=v3.set(dog.x,dog.y+0.75,dog.z);", "const tgt=v3.set(dog.x,dog.y+0.75*(0.55+0.45*D.k),dog.z);")
E('js', "D.head.localToWorld(v3.set(0,-0.08,0.27));it.x=v3.x;", "D.head.localToWorld(v3.set(0,-0.08,D.mouthZ));it.x=v3.x;")
E('js', "D.head.localToWorld(v3.set(0,-0.07,0.27));ball.x=v3.x;", "D.head.localToWorld(v3.set(0,-0.07,D.mouthZ));ball.x=v3.x;")
E('js', "to=D.head.localToWorld(v3.set(0,-0.08,0.27)).clone()", "to=D.head.localToWorld(v3.set(0,-0.08,D.mouthZ)).clone()")

# ---------------------------------------------------------------- G. breed-aware text
E('js', "(S.breed==='bichon'?'bichon frise':'golden retriever')", "(breedInfo().name)")
E('js', "browser game where you play a golden retriever in '+WD.name+'", "browser game where you play a '+breedInfo().name+' in '+WD.name+'")
E('js', "'Hello, fluffy!','Look at that golden fur!'];", "'Hello, fluffy!'];")
E('js', "say(p,pick(belly?BELLY:PAT),2.6);", "say(p,pick(belly?BELLY:PAT.concat(breedInfo().pat)),2.6);")
E('js', "'Hahaha! The golden got your food again!'", "'Hahaha! The '+breedInfo().sh+' got your food again!'")
E('js', "'Come back, you golden furball!'", "'Come back, you '+breedInfo().fb+'!'")
E('js', "'Ay, ang cute! Come here, doggy!','Golden retriever! So fluffy!',", "'Ay, ang cute! Come here, doggy!',breedInfo().pic,")
E('js', "else{toast('Welcome home, '+S.name+'! Your food bowl is by the red front door.');",
  "else{toast('Welcome home, '+S.name+'! Your food bowl is by the red front door.');breedHello();")
E('js', "else if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name+'! No cars here: people zip around in golf carts.');",
  "else if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name+'! No cars here: people zip around in golf carts.');breedHello();")

# ---------------------------------------------------------------- H. perks
E('js', "dog.action='dig';dog.actionT=1.6;", "dog.action='dig';dog.actionT=S.breed==='terrier'?1.05:1.6;")
E('js', "Math.hypot(s.x-dog.x,s.z-dog.z)<2.2);", "Math.hypot(s.x-dog.x,s.z-dog.z)<(S.breed==='terrier'?3:2.2));")
E('js', "s.s.visible=sn&&d<60;", "s.s.visible=sn&&d<(S.breed==='terrier'?80:60);")
E('js', "if(cat.chaseT>1.4)complete('cat')", "if(cat.chaseT>(S.breed==='terrier'?1.0:1.4))complete('cat')")
E('js', "dog.swimming?1.8:", "dog.swimming?(S.breed==='lantau'?2.3:1.8):")
E('js', "S.hunger=clamp(S.hunger-dt*(dog.swimming?0.25:0.16),0,100);", "S.hunger=clamp(S.hunger-dt*(dog.swimming?0.25:0.16)*(S.breed==='lantau'?0.8:1),0,100);")

# ---------------------------------------------------------------- I. multiplayer
E('js', "const D2=makeDog(q.br);", "const D2=makeDog(q.br,{lite:true,mc:true});")
E('js', "Dd.tail.rotation.x=lerp(-1.15,-1.55,Math.max(sit,lie));", "Dd.tail.rotation.x=lerp(-1.15,-1.55,Math.max(sit,lie))+Dd.tailUp;")
E('js', "say(o,'Woof! Woof!',1.2);if(Math.hypot(o.x-dog.x,o.z-dog.z)<30)sfx.bark()",
  "say(o,breedInfo(o.D.breed).bark,1.2);if(Math.hypot(o.x-dog.x,o.z-dog.z)<30)sfx.bark(o.D.pitch)")

# ---------------------------------------------------------------- J. start card (HTML / CSS)
E('head', '<label><input type="radio" name="breed" value="bichon"> Bichon frise</label></div></div>',
  '<label><input type="radio" name="breed" value="bichon"> Bichon frise</label>'
  '<label><input type="radio" name="breed" value="terrier"> Border terrier 🎀</label>'
  '<label><input type="radio" name="breed" value="lantau"> Lantau street dog 唐狗</label></div></div>')
E('head', ".breeds{display:flex;gap:14px;", ".breeds{display:flex;flex-wrap:wrap;gap:6px 14px;")
E('head', "<p>You're a golden retriever living in Ha Yeung village, Clear Water Bay.",
  "<p>You're a dog living in Ha Yeung village, Clear Water Bay: a golden retriever, a fluffy bichon, a scruffy border terrier with a pink collar, or a free Lantau street dog (唐狗).")

# ---------------------------------------------------------------- apply
for part, old, new in EDITS:
    k = src.rfind('<script>')
    head, js = src[:k], src[k:]
    seg = head if part == 'head' else js
    assert seg.count(old) == 1, (part, seg.count(old), old[:90])
    assert src.count(old) == 1, ('file', src.count(old), old[:90])
    seg = seg.replace(old, new, 1)
    src = seg + js if part == 'head' else head + seg
assert src.count(MARK) == 1
open(P, 'w', encoding='utf-8').write(src)

k = src.rfind('<script>')
body = src[src.index('>', k) + 1:src.rindex('</script>')]
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(body)
r = subprocess.run(['node', '--check', f.name], capture_output=True, text=True)
os.unlink(f.name)
if r.returncode:
    print(r.stderr)
    sys.exit('node --check FAILED')
print('breeds_xform: %d edits applied, node --check OK' % len(EDITS))
