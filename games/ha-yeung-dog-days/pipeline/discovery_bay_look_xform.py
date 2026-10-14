#!/usr/bin/env python3
# Discovery Bay look: towers, villas with hip roofs, plaza, D'Deck, pier + ferry, palms, cove village,
# faster golf carts with turbo, police chases.
import sys
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'function dbPrep' not in src, 'already transformed'
k = src.rfind('<script>'); head, c = src[:k], src[k:]

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

head = R(head, '<kbd>X</kbd><span>Board the bus at the stop; hop on or off a golf cart</span>',
         '<kbd>X</kbd><span>Board the bus at the stop; hop on or off a golf cart (W to drive, hold Shift for turbo)</span>')

# ---------------------------------------------------------------- world prep (before buildings are indexed)
PREP = r'''// ================= Discovery Bay: building styles, plaza, promenade, pier jetty, cove village =================
const NOTREE=[];
function obb(p){let best=null;for(let i=0;i<p.length;i++){const a=p[i],c=p[(i+1)%p.length];let ux=c[0]-a[0],uz=c[1]-a[1];const L=Math.hypot(ux,uz);if(L<1e-3)continue;ux/=L;uz/=L;const vx=-uz,vz=ux;
    let s0=1e9,s1=-1e9,t0=1e9,t1=-1e9;for(const q of p){const s=q[0]*ux+q[1]*uz,t=q[0]*vx+q[1]*vz;s0=Math.min(s0,s);s1=Math.max(s1,s);t0=Math.min(t0,t);t1=Math.max(t1,t)}
    const ar=(s1-s0)*(t1-t0);if(!best||ar<best.ar)best={ar,ux,uz,vx,vz,s0,s1,t0,t1}}
  const b=best;let a=(b.s1-b.s0)/2,bb=(b.t1-b.t0)/2;const sc=(b.s0+b.s1)/2,tc=(b.t0+b.t1)/2;let ux=b.ux,uz=b.uz,vx=b.vx,vz=b.vz;const cx=ux*sc+vx*tc,cz=uz*sc+vz*tc;
  if(bb>a){[a,bb]=[bb,a];[ux,uz,vx,vz]=[vx,vz,-ux,-uz]}return {cx,cz,ux,uz,vx,vz,a,b:bb,ar:b.ar}}
function segDist(x,z,P){let best=1e9,y=0;for(let i=0;i<P.length-1;i++){const a=P[i],b=P[i+1],ex=b[0]-a[0],ez=b[1]-a[1];const t=clamp(((x-a[0])*ex+(z-a[1])*ez)/(ex*ex+ez*ez||1),0,1);const d=Math.hypot(x-a[0]-ex*t,z-a[1]-ez*t);if(d<best){best=d;y=t+i}}return [best,y]}
// D'Deck waterfront promenade, from the real shore footpath to the ferry pier
const DECK=[[-41,-90],[-33,-82],[-21,-87],[-10,-91],[2,-95],[14,-99],[25,-103],[31,-105],[42,-101],[54,-100],[65,-104],[77,-105],[90,-101],[102,-104]];
const PIAZ={x:10,z:-20,r:21,y:13};
const DBX=WD.level==='db'?dbPrep():null;
function dbPrep(){const X={village:[]};
  // weight-blend the height grid towards a target inside a region; region(x,z) -> [weight 0..1, target y, paved?]
  function shape(x0,x1,z0,z1,region){for(let j=Math.max(0,Math.floor((z0-Z0)/CELL));j<=Math.min(NZ-1,Math.ceil((z1-Z0)/CELL));j++)for(let i=Math.max(0,Math.floor((x0-X0)/CELL));i<=Math.min(NX-1,Math.ceil((x1-X0)/CELL));i++){
      const r=region(X0+i*CELL,Z0+j*CELL);if(!r||r[0]<=0)continue;const k=j*NX+i;HT[k]=lerp(HT[k],r[1],r[0]);if(r[2])CLS[k]=2}}
  // the piazza: one level terrace instead of the lumpy roof-top surface model
  shape(PIAZ.x-40,PIAZ.x+40,PIAZ.z-40,PIAZ.z+40,(x,z)=>{const d=Math.hypot(x-PIAZ.x,z-PIAZ.z);return d>PIAZ.r+9?null:[d<=PIAZ.r?1:1-smooth(PIAZ.r,PIAZ.r+9,d),PIAZ.y,d<=PIAZ.r]});
  // the rest of the open plaza between the mall wings, on the same level
  shape(-32,52,-50,38,(x,z)=>{const d=Math.hypot(Math.max(-22-x,0,x-42),Math.max(-40-z,0,z-28));return d>6?null:[d<=0?1:1-smooth(0,6,d),PIAZ.y,d<=0]});
  NOTREE.push([PIAZ.x,PIAZ.z,PIAZ.r+6],[10,10,26]);
  // D'Deck: a level promenade 1.7 m above the sea
  shape(-60,120,-125,-70,(x,z)=>{const [d]=segDist(x,z,DECK);return d>8?null:[d<=4.6?1:1-smooth(4.6,8,d),1.7,d<=4.6]});
  for(const p of DECK)NOTREE.push([p[0],p[1],7]);
  // styles: cross-shaped high-rises, villas (Beach Village, Headland) with pitched roofs, the ferry pier
  const fr=(x,z)=>{const s=Math.sin(x*12.9898+z*78.233)*43758.5453;return s-Math.floor(s)};
  let pier=null,pd=1e9;for(const b of WD.bld){const d=Math.hypot(b.cx-128,b.cz+110);if(b.a>1000&&d<pd&&d<40){pd=d;pier=b}}
  for(const b of WD.bld){const o=obb(b.p),rect=b.a/o.ar;
    if(b===pier){b.style='pier';b.h=6.5;b.f=2}
    else if(b.p.length>=10&&b.a>=340&&b.a<=700&&rect<0.75){b.style='tower';b.f=16+Math.floor(fr(b.cx,b.cz)*8);b.h=b.f*2.9+1.2}
    else if(b.a>=40&&b.a<=400){b.style='villa';b.f=Math.max(2,b.f)}
    else b.style='flat'}
  if(pier){shape(pier.cx-60,pier.cx+60,pier.cz-60,pier.cz+60,(x,z)=>{let inside=inPoly(pier.p,x,z);if(!inside)for(const [ox,oz] of [[2,0],[-2,0],[0,2],[0,-2]])if(inPoly(pier.p,x+ox,z+oz))inside=true;return inside?[1,Math.max(1.6,gridH(x,z)),true]:null});pier.b=1.6;X.pier=pier}
  // the village by the cove (south-east corner): three-storey village houses facing the water
  const cove=[395,235];const cand=[];
  for(let z=150;z<=262;z+=12)for(let x=252;x<=336;x+=12){const h=gridH(x,z),cl=CLS[cellIdx(x,z)];if(h<0.4||h>7||(cl!==0&&cl!==1))continue;
    let ok=true;for(const [ox,oz] of [[0,0],[5,0],[-5,0],[0,5],[0,-5],[5,5],[-5,-5],[5,-5],[-5,5]]){const id=cellIdx(x+ox,z+oz);if(RMASK[id]||CLS[id]===4||gridH(x+ox,z+oz)<0.3)ok=false}
    if(!ok)continue;for(const b of WD.bld)if(Math.hypot(b.cx-x,b.cz-z)<16)ok=false;if(ok)cand.push([x,z])}
  cand.sort((a,b)=>Math.hypot(a[0]-cove[0],a[1]-cove[1])-Math.hypot(b[0]-cove[0],b[1]-cove[1]));
  for(const [x,z] of cand){if(X.village.length>=9)break;if(X.village.some(v=>Math.hypot(v.x-x,v.z-z)<11.5))continue;
    const a=Math.atan2(cove[0]-x,cove[1]-z)+(fr(x,z)-0.5)*0.4;const base=Math.max(0.9,gridH(x,z)+0.2);
    shape(x-10,x+10,z-10,z+10,(px,pz)=>{const d=Math.max(Math.abs((px-x)*Math.cos(a)-(pz-z)*Math.sin(a)),Math.abs((px-x)*Math.sin(a)+(pz-z)*Math.cos(a)));return d>8?null:[d<=5.2?1:1-smooth(5.2,8,d),base,d<=5.2]});
    const ux=Math.cos(a),uz=-Math.sin(a),fx=Math.sin(a),fz=Math.cos(a),hs=4.1;
    const p=[[x+ux*hs+fx*hs,z+uz*hs+fz*hs],[x-ux*hs+fx*hs,z-uz*hs+fz*hs],[x-ux*hs-fx*hs,z-uz*hs-fz*hs],[x+ux*hs-fx*hs,z+uz*hs-fz*hs]];
    WD.bld.push({p,b:base,h:8.9,f:3,a:67,cx:x,cz:z,style:'vhouse'});X.village.push({x,z,a,base});NOTREE.push([x,z,7.5])}
  if(X.village.length){let sx=0,sz=0;for(const v of X.village){sx+=v.x;sz+=v.z}X.vc=[sx/X.village.length,sz/X.village.length]}
  // walls reach the ground (no floating edges after the reshaping above)
  for(const b of WD.bld){if(b.style==='vhouse'||b.style==='pier')continue;let m=1e9;for(const q of b.p)m=Math.min(m,gridH(q[0],q[1]));m=Math.max(m,-0.5);if(m<b.b){b.h+=b.b-m;b.b=m}}
  return X}
const BL=WD.bld;const BH=new Map();const BS=16;'''
c = R(c, 'const BL=WD.bld;const BH=new Map();const BS=16;', PREP)

c = R(c, 'const PAL=[0x6f9a48,0x3f6d34,0x9fae7c,0xe2cf9e,0x4f7f78,0x8a7f70]', "const PAL=[0x6f9a48,0x3f6d34,0x9fae7c,WD.level==='db'?0xdcb775:0xe2cf9e,0x4f7f78,0x8a7f70]")
c = R(c, 'if(avoid.some(a=>Math.hypot(x-a[0],z-a[1])<a[2]))continue;', 'if(avoid.some(a=>Math.hypot(x-a[0],z-a[1])<a[2])||NOTREE.some(a=>Math.hypot(x-a[0],z-a[1])<a[2]))continue;')

# ---------------------------------------------------------------- buildings with styles
b0 = c.index('const TINTS=['); b1 = c.index('// ================= Roads (real centrelines) =================')
BLD = r'''const TINTS=[0xf2efe6,0xeadab8,0xd5e3df,0xf1d8c6,0xdce6c6,0xe4def0,0xf3e3a8,0xffffff,0xe9e4da].map(h=>new THREE.Color(h));
const CC=a=>a.map(h=>new THREE.Color(h));
const DB_TINTS=CC([0xf3e6c4,0xf2dc9c,0xeec1a6,0xf6d7b8,0xf4f1ea,0xe9d3b5,0xdfe8d0]),TOWER_TINTS=CC([0xf6ecd0,0xf3df9e,0xf0cdb0,0xf7e7c6,0xeadfca,0xf2d7a0]),
  VILLA_TINTS=CC([0xf3e6c4,0xf1d2b0,0xe8dcc4,0xf6efe0,0xeec9a8,0xdfe2d6]),VH_TINTS=CC([0xffffff,0xf4d9df,0xdfeaf2,0xf2ead2,0xe3f0e0]),ROOF_TINTS=CC([0xb4553a,0xa34a33,0xc0663f,0x5b6a78,0x4f5d6b,0x8a5a3c]);
const LIT=[wallMat];function litMat(tex){tex.wrapS=tex.wrapT=THREE.RepeatWrapping;const m=new THREE.MeshLambertMaterial({map:tex,vertexColors:true,emissive:0xffc977,emissiveMap:litTex,emissiveIntensity:0});LIT.push(m);return m}
const SMAT={};
if(WD.level==='db'){
  // high-rise: cream bands, dark window strips, white balcony rails, salmon pilasters
  SMAT.tower=litMat(canvasTex(256,256,(x,w,h)=>{x.fillStyle='#f6f1e6';x.fillRect(0,0,w,h);for(let f=0;f<4;f++){const y0=f*64;x.fillStyle='#5a7482';for(let b=0;b<6;b++)x.fillRect(b*42+10,y0+18,22,22);x.fillStyle='#ffffff';x.fillRect(0,y0+46,w,4);x.fillStyle='rgba(0,0,0,.08)';x.fillRect(0,y0+62,w,2)}
    x.fillStyle='#d9a383';x.fillRect(0,0,10,h);x.fillRect(124,0,12,h)}));
  // villas: big windows with dark shutters
  SMAT.villa=litMat(canvasTex(256,256,(x,w,h)=>{x.fillStyle='#f6f1e6';x.fillRect(0,0,w,h);for(let f=0;f<4;f++)for(let b=0;b<3;b++){const x0=b*85+18,y0=f*64+12;x.fillStyle='#e9e3d4';x.fillRect(x0-4,y0-3,58,44);x.fillStyle='#41525c';x.fillRect(x0,y0,50,38);x.fillStyle='#5c3b2a';x.fillRect(x0-12,y0,9,38);x.fillRect(x0+53,y0,9,38)}}));
  // village houses: small mosaic tiles, aluminium windows with grilles
  SMAT.vhouse=litMat(canvasTex(256,256,(x,w,h)=>{x.fillStyle='#f7f5ef';x.fillRect(0,0,w,h);x.strokeStyle='rgba(0,0,0,.07)';x.lineWidth=1;for(let i=0;i<w;i+=8){x.beginPath();x.moveTo(i,0);x.lineTo(i,h);x.stroke();x.beginPath();x.moveTo(0,i);x.lineTo(w,i);x.stroke()}
    for(let f=0;f<4;f++)for(let b=0;b<2;b++){const x0=b*128+28,y0=f*64+14;x.fillStyle='#b8c2c6';x.fillRect(x0-3,y0-3,78,40);x.fillStyle='#4a6270';x.fillRect(x0,y0,72,34);x.strokeStyle='#d8dde0';x.lineWidth=2;for(let g=0;g<6;g++){x.beginPath();x.moveTo(x0+g*12+6,y0);x.lineTo(x0+g*12+6,y0+34);x.stroke()}}}));
  SMAT.pier=litMat(canvasTex(256,256,(x,w,h)=>{x.fillStyle='#f4f4f0';x.fillRect(0,0,w,h);for(let f=0;f<4;f++){x.fillStyle='#6f93a8';x.fillRect(0,f*64+10,w,34);x.fillStyle='#ffffff';for(let b=0;b<8;b++)x.fillRect(b*32,f*64+10,3,34)}}));
}
const roofVMat=new THREE.MeshLambertMaterial({vertexColors:true});
function hipRoof(p,y1,P,N,C){const o=obb(p);const A=o.a+0.45,B=o.b+0.45,Rr=Math.max(0,A-B),H=Math.max(1.2,B*0.62);const col=ROOF_TINTS[Math.floor(rnd()*ROOF_TINTS.length)];
  const pt=(s,t,y)=>[o.cx+o.ux*s+o.vx*t,y,o.cz+o.uz*s+o.vz*t];const ye=y1-0.05,yr=y1+H;
  const e1=pt(A,B,ye),e2=pt(-A,B,ye),e3=pt(-A,-B,ye),e4=pt(A,-B,ye),r1=pt(Rr,0,yr),r2=pt(-Rr,0,yr);const va=new THREE.Vector3(),vb=new THREE.Vector3();
  const tri=(a,b,c)=>{va.set(b[0]-a[0],b[1]-a[1],b[2]-a[2]);vb.set(c[0]-a[0],c[1]-a[1],c[2]-a[2]);va.cross(vb);if(va.y<0){const t=b;b=c;c=t;va.negate()}va.normalize();for(const q of [a,b,c]){P.push(q[0],q[1],q[2]);N.push(va.x,va.y,va.z);C.push(col.r,col.g,col.b)}};
  tri(e1,e2,r2);tri(e1,r2,r1);tri(e3,e4,r1);tri(e3,r1,r2);tri(e4,e1,r1);tri(e2,e3,r2);return yr}
(function(){
  const W=new Map(),rp=[],rn=[],hp=[],hn=[],hc=[];const getW=m=>{if(!W.has(m))W.set(m,{p:[],n:[],u:[],c:[]});return W.get(m)};
  for(const b of BL){const p=b.p,n=p.length;if(n<3)continue;
    let A=0;for(let i=0;i<n;i++){const a=p[i],c=p[(i+1)%n];A+=a[0]*c[1]-c[0]*a[1]}
    const ccw=A>0;const st=b.style||'def';const T=getW(SMAT[st]||wallMat);
    const tints=WD.level!=='db'?TINTS:st==='tower'?TOWER_TINTS:st==='villa'?VILLA_TINTS:st==='vhouse'?VH_TINTS:DB_TINTS;
    const y0=b.b,y1=b.b+b.h,vBase=y1-Math.max(1,b.f)*FLOOR;const tint=tints[Math.floor(rnd()*tints.length)];let u=rnd()*4;const us=st==='vhouse'?16:st==='tower'?18:24;
    for(let i=0;i<n;i++){const a=p[i],c=p[(i+1)%n];const dx=c[0]-a[0],dz=c[1]-a[1],L=Math.hypot(dx,dz);if(L<0.05)continue;
      let nx=dz/L,nz=-dx/L;if(!ccw){nx=-nx;nz=-nz}
      const u0=u/us,u1=(u+L)/us;u+=L;const v0=(y0-vBase)/(4*FLOOR),v1=(y1-vBase)/(4*FLOOR);
      const q=[[a[0],y0,a[1],u0,v0],[c[0],y0,c[1],u1,v0],[c[0],y1,c[1],u1,v1],[a[0],y1,a[1],u0,v1]];
      const flip=(-dz*nx+dx*nz)<0;const tris=flip?[[0,2,1],[0,3,2]]:[[0,1,2],[0,2,3]];
      for(const t of tris)for(const k of t){const v=q[k];T.p.push(v[0],v[1],v[2]);T.n.push(nx,0,nz);T.u.push(v[3],v[4]);T.c.push(tint.r,tint.g,tint.b)}}
    if(st==='villa'){b.top=hipRoof(p,y1,hp,hn,hc);continue}
    const contour=p.map(q=>new THREE.Vector2(q[0],q[1]));const faces=THREE.ShapeUtils.triangulateShape(contour,[]);
    for(const f of faces){let [i0,i1,i2]=f;const a=p[i0],c1=p[i1],c2=p[i2];const cr=(c1[1]-a[1])*(c2[0]-a[0])-(c1[0]-a[0])*(c2[1]-a[1]);if(cr<0){const t=i1;i1=i2;i2=t}
      for(const k of [i0,i1,i2]){rp.push(p[k][0],y1,p[k][1]);rn.push(0,1,0)}}}
  for(const [m,T] of W){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(T.p,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(T.n,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(T.u,2));g.setAttribute('color',new THREE.Float32BufferAttribute(T.c,3));
    const me=new THREE.Mesh(g,m);me.castShadow=me.receiveShadow=true;scene.add(me)}
  const rg=new THREE.BufferGeometry();rg.setAttribute('position',new THREE.Float32BufferAttribute(rp,3));rg.setAttribute('normal',new THREE.Float32BufferAttribute(rn,3));
  const rm=new THREE.Mesh(rg,roofMat);rm.castShadow=rm.receiveShadow=true;scene.add(rm);
  if(hp.length){const hg=new THREE.BufferGeometry();hg.setAttribute('position',new THREE.Float32BufferAttribute(hp,3));hg.setAttribute('normal',new THREE.Float32BufferAttribute(hn,3));hg.setAttribute('color',new THREE.Float32BufferAttribute(hc,3));
    const hm=new THREE.Mesh(hg,roofVMat);hm.castShadow=hm.receiveShadow=true;scene.add(hm)}
})();

'''
c = c[:b0] + BLD + c[b1:]
c = R(c, 'wallMat.emissiveIntensity=night*0.95;', 'for(const m of LIT)m.emissiveIntensity=night*0.95;')

# ---------------------------------------------------------------- golf carts: much faster, turbo, substeps
r0 = c.index('function rideCart(dt){'); r1 = c.index('function doSit(){')
RIDE = r'''function rideCart(dt){const k=dog.cart;let th=0,st=0;
  if(!S.leaving){if(keys.w||keys.arrowup)th+=1;if(keys.s||keys.arrowdown)th-=1;if(keys.d||keys.arrowright)st+=1;if(keys.a||keys.arrowleft)st-=1;if(joy.mag>0.12){th=-joy.y;st=joy.x}}
  const turbo=(keys.shift||runLock||joy.mag>0.95)&&th>0.05;const top=turbo?22:16;k.turbo=turbo;
  const want=th>0.05?th*top:th<-0.05?th*4:0;
  if(Math.abs(th)<=0.05)k.v=Math.abs(k.v)<0.2?0:k.v-Math.sign(k.v)*3.5*dt;
  else if(Math.sign(want)!==Math.sign(k.v)&&Math.abs(k.v)>0.1)k.v-=Math.sign(k.v)*12*dt;
  else k.v+=clamp(want-k.v,-6*dt,(turbo?9:7)*dt);
  k.h-=st*1.8/(1+Math.abs(k.v)/16)*dt*clamp(k.v/2.5,-1,1);
  const fx=Math.sin(k.h),fz=Math.cos(k.h);const n=Math.max(1,Math.ceil(Math.abs(k.v)*dt/0.5));let x=k.x,z=k.z;
  for(let i=0;i<n&&k.v!==0;i++){const dir=k.v<0?-1:1;let nx=x+fx*k.v*dt/n,nz=z+fz*k.v*dt/n;const pr=1.4+Math.abs(k.v)*0.05,px=nx+fx*pr*dir,pz=nz+fz*pr*dir;
    if(gridH(px,pz)<0.3||CLS[cellIdx(px,pz)]===4){k.v=0;if(S.t-(k.waterT||-99)>6){k.waterT=S.t;toast('The cart stops at the water\'s edge. Golf carts can\'t swim!')}break}
    if((gridH(px,pz)-gridH(x,z))/pr>0.9){k.v=0;if(S.t-(k.steepT||-99)>6){k.steepT=S.t;toast('Too steep for a golf cart.')}break}
    let hit=false;for(const o of [0.6,-0.6]){const qx=nx+fx*o,qz=nz+fz*o;const [rx,rz]=pushOutB(qx,qz,0.75);if(Math.hypot(rx-qx,rz-qz)>0.02){hit=true;nx+=rx-qx;nz+=rz-qz}}
    for(const s of softColliders){const ex=nx-s[0],ez=nz-s[1],L=Math.hypot(ex,ez);if(L<s[2]+1.0&&L>1e-4){nx=s[0]+ex/L*(s[2]+1.0);nz=s[1]+ez/L*(s[2]+1.0);k.v*=0.6}}
    for(const o of carts){if(o===k)continue;const ex=nx-o.x,ez=nz-o.z,L=Math.hypot(ex,ez);if(L<2.0&&L>1e-4){nx=o.x+ex/L*2.0;nz=o.z+ez/L*2.0;k.v*=0.6}}
    x=nx;z=nz;if(hit){if(Math.abs(k.v)>1.8){sfx.bonk();say(DOGTALK,'Bonk!',0.9);S.happy=Math.max(0,S.happy-1);if(Math.abs(k.v)>9)shake()}k.v*=-0.25;break}}
  k.x=clamp(x,X0+20,X1-20);k.z=clamp(z,Z0+20,Z1-20);k.dist+=Math.abs(k.v)*dt;if(k.dist>60)complete('cart');placeCart(k);
  cam.dist+=(Math.max(dog.camDist||5.5,7.5+Math.abs(k.v)*0.18)-cam.dist)*Math.min(1,dt*1.5);
  if(turbo&&Math.abs(k.v)>12&&Math.random()<dt*20)dust.emit(k.x-fx*1.3,k.y+0.3,k.z-fz*1.3,(Math.random()-0.5),0.8,(Math.random()-0.5),0.5,C_SAND,2);
  k.g.updateMatrixWorld();const sp=k.g.localToWorld(v3.set(-0.15,0.78,0.22));dog.x=sp.x;dog.z=sp.z;dog.y=sp.y;dog.heading=k.h;dog.posture='sit';dog.speed=0;dog.sitT=0;dog.swimming=false;
  if(dog.barkT>0)dog.barkT-=dt;D.root.position.set(dog.x,dog.y,dog.z);D.root.rotation.set(-k.pitch,dog.heading,0)}
'''
c = c[:r0] + RIDE + c[r1:]
c = R(c, "'Beep beep! W / ↑ to drive, S / ↓ to brake and reverse, A D / ← → to steer.'", "'Beep beep! W / ↑ to drive (hold Shift for turbo), S / ↓ to brake and reverse, A D / ← → to steer.'")
c = R(c, "'Beep beep! Push the stick up to drive, sideways to steer, down to brake and reverse.'", "'Beep beep! Push the stick up to drive (all the way for turbo), sideways to steer, down to brake and reverse.'")
c = R(c, "speed:6+i*0.7,cart:true", "speed:8+i*0.8,cart:true")
c = R(c, "$('#elev').textContent=Math.max(0,Math.round(dog.y))+' m'", "$('#elev').textContent=dog.cart?Math.round(Math.abs(dog.cart.v)*3.6)+' km/h':Math.max(0,Math.round(dog.y))+' m'")

# ---------------------------------------------------------------- police chase (Discovery Bay)
POL = r'''// ================= Police: now and then a patrol car spots a dog driving a golf cart =================
function makePolice(){const g=new THREE.Group(),body=new THREE.Group();g.add(body);const white=mat(0xf6f6f2),glass=mat(0x1f2b33),blk=mat(0x151515);
  const chk=canvasTex(256,32,(x)=>{for(let i=0;i<16;i++){x.fillStyle=i%2?'#f2c230':'#1d4ea0';x.fillRect(i*16,0,16,16);x.fillStyle=i%2?'#1d4ea0':'#f2c230';x.fillRect(i*16,16,16,16)}});
  box(white,4.6,0.85,1.8,0,0.7,0,body);box(white,2.5,0.65,1.65,-0.25,1.45,0,body);box(glass,2.52,0.45,1.67,-0.25,1.45,0,body);
  const band=new THREE.Mesh(new THREE.BoxGeometry(4.62,0.3,1.82),new THREE.MeshLambertMaterial({map:chk}));band.position.set(0,0.62,0);body.add(band);
  const txt=canvasTex(256,64,(x,w,h)=>{x.fillStyle='#ffffff';x.fillRect(0,0,w,h);x.fillStyle='#1d4ea0';x.font='bold 30px "Noto Sans TC",sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText('警察  POLICE',w/2,h/2+1)});
  for(const s of [1,-1]){const p=new THREE.Mesh(new THREE.PlaneGeometry(1.7,0.36),new THREE.MeshBasicMaterial({map:txt}));p.position.set(-0.1,0.95,0.91*s);if(s<0)p.rotation.y=Math.PI;body.add(p)}
  const rl=new THREE.MeshLambertMaterial({color:0xff3030,emissive:0xff0000,emissiveIntensity:0}),bl=new THREE.MeshLambertMaterial({color:0x3060ff,emissive:0x2050ff,emissiveIntensity:0});
  box(mat(0x222222),0.35,0.08,1.3,-0.25,1.8,0,body);box(rl,0.3,0.16,0.55,-0.25,1.9,0.33,body);box(bl,0.3,0.16,0.55,-0.25,1.9,-0.33,body);
  for(const x of [1.45,-1.45])for(const z of [-0.82,0.82]){const w=cyl(blk,0.34,0.34,0.22,x,0.34,z,body,12);w.rotation.x=Math.PI/2}
  scene.add(g);return {g,body,rl,bl}}
const police=WD.level==='db'?Object.assign(makePolice(),{state:'off',cool:40+Math.random()*50,t:0,x:0,z:0,h:0,v:0,headY:2.4,shoutT:0,sirenT:0,closeT:0}):null;if(police)police.g.visible=false;
const POLICE_LINES=['喂! 架車停低! Pull over!','Dog! Get out of the cart!','狗仔! 落車!! Get OUT of the cart!','This is the police. Paws OFF the wheel!','Is that… is that a DOG driving?!','Stop the vehicle, good boy!','Somebody call his owner!!'];
function spawnPolice(){const P=police,k=dog.cart;const fx=Math.sin(k.h),fz=Math.cos(k.h);let best=null,bs=-1e9;
  for(let s=0;s<=CWL;s+=8){const q=cwAt(s);const d=Math.hypot(q.x-dog.x,q.z-dog.z);if(d<50||d>95)continue;const behind=-((q.x-dog.x)*fx+(q.z-dog.z)*fz)/d;if(behind>bs){bs=behind;best=q}}
  if(!best){const x=dog.x-fx*60,z=dog.z-fz*60;if(gridH(x,z)>0.5&&!bldAt(x,z))best={x,z};else{P.cool=15;return}}
  Object.assign(P,{state:'chase',t:0,x:best.x,z:best.z,h:Math.atan2(dog.x-best.x,dog.z-best.z),v:6,shoutT:0.6,sirenT:0,closeT:0});P.g.visible=true;
  arcade('逃げろ!','POLICE!','run');shake();sfx.arcadeStart();toast('A police car spotted a DOG driving a golf cart! Lose them: get 90 m away or hold out for 30 seconds.')}
function endPolice(won){const P=police;P.state='leave';P.t=0;
  if(won){arcade('にげきった!','ESCAPED!!','win');sfx.win();shake();popScore('+500');S.points+=500;S.happy=Math.min(100,S.happy+15);complete('police');
    say(P,pick(['…He went that way. I think. Was it a he?','Lost him! Who\'s going to believe this report?']),3);toast('You lost the police! Somewhere an officer is writing a very confusing report.')}
  else{arcade('つかまった…','BUSTED!','lose');sfx.lose();if(dog.cart)hopOff();hearts(10);S.happy=Math.min(100,S.happy+5);
    say(P,pick(['Good boy… but no licence, no driving, okay?','Paws where I can see them! …Aww, who\'s a good boy?']),3.5);toast('Busted! The officer parks the cart and gives you a pat. Try again… next time.')}}
function moveCar(o,dt){const fx=Math.sin(o.h),fz=Math.cos(o.h);const n=Math.max(1,Math.ceil(Math.abs(o.v)*dt/0.5));let blocked=false;
  for(let i=0;i<n;i++){let nx=o.x+fx*o.v*dt/n,nz=o.z+fz*o.v*dt/n;const px=nx+fx*2.4,pz=nz+fz*2.4;if(gridH(px,pz)<0.3){blocked=true;o.v*=0.5;break}
    for(const off of [1.2,-1.2]){const qx=nx+fx*off,qz=nz+fz*off;const [rx,rz]=pushOutB(qx,qz,1.0);if(Math.hypot(rx-qx,rz-qz)>0.02){blocked=true;nx+=rx-qx;nz+=rz-qz}}
    o.x=clamp(nx,X0+15,X1-15);o.z=clamp(nz,Z0+15,Z1-15)}return blocked}
function updatePolice(dt){const P=police;
  if(P.state==='off'){if(S.started&&dog.cart&&Math.abs(dog.cart.v)>5){P.cool-=dt;if(P.cool<=0)spawnPolice()}return}
  P.t+=dt;const k=dog.cart;const dx=dog.x-P.x,dz=dog.z-P.z,d=Math.hypot(dx,dz);const fl=Math.floor(S.t*7)%2;P.rl.emissiveIntensity=fl?1.8:0.1;P.bl.emissiveIntensity=fl?0.1:1.8;
  if(P.state==='chase'){P.sirenT-=dt;if(P.sirenT<=0){P.sirenT=0.9;if(d<130)sfx.siren()}
    if(!k){P.state='leave';P.t=0;say(P,pick(['…Okay. Good boy. Who left this cart running?','Dog out of the vehicle. Case closed!']),3);toast('The police give up: without the cart you\'re just a very good dog.');return}
    const want=Math.atan2(dx,dz);P.h+=clamp(angDiff(P.h,want),-2.6*dt,2.6*dt);const aligned=Math.cos(angDiff(P.h,want));
    const top=(d>45?19.5:18)*(0.55+0.45*Math.max(0,aligned));P.v+=clamp(top-P.v,-14*dt,(P.t<1.5?4:8)*dt);
    if(moveCar(P,dt)){P.h+=2.2*dt*(Math.sin(P.t*0.7)>0?1:-1)}
    P.shoutT-=dt;if(P.shoutT<=0){P.shoutT=3.2;const line=pick(POLICE_LINES);if(d>30)toast('📢 '+line);else say(P,line,2.6)}
    if(d<3.6)P.closeT+=dt;else P.closeT=Math.max(0,P.closeT-dt*0.5);
    if(P.closeT>0.7&&P.t>2)endPolice(false);else if(d>90||P.t>30)endPolice(true)}
  else{P.v=Math.min(11,P.v+5*dt);const away=Math.atan2(P.x-dog.x,P.z-dog.z);if(P.t>2.5)P.h+=clamp(angDiff(P.h,away),-1.5*dt,1.5*dt);else P.v=Math.max(0,P.v-10*dt);moveCar(P,dt);
    if(P.t>9){P.state='off';P.g.visible=false;P.cool=80+Math.random()*100}}
  P.g.position.set(P.x,groundAt(P.x,P.z)+0.02,P.z);P.g.rotation.set(0,P.h-Math.PI/2,0)}
const walkers=[];'''
c = R(c, "\nconst walkers=[];", "\n" + POL)
c = R(c, "for(const v of aiCarts)updateVehicle(v,dt);", "for(const v of aiCarts)updateVehicle(v,dt);if(police)updatePolice(dt);")
c = R(c, "const ch=bbq.state==='chase'?[bbq.uncle,'UNCLE',24]:picnic.state==='chase'?[picnic.chaser,'ATE',16]:null;",
         "const ch=bbq.state==='chase'?[bbq.uncle,'UNCLE',24]:picnic.state==='chase'?[picnic.chaser,'ATE',16]:police&&police.state==='chase'?[police,'POLICE '+Math.max(0,Math.ceil(30-police.t))+'s',90]:null;")
c = R(c, "for(const k of aiCarts)if(k.g.visible)dot(k.x,k.z,'#f6f4ee',2.6,true);", "for(const k of aiCarts)if(k.g.visible)dot(k.x,k.z,'#f6f4ee',2.6,true);if(police&&police.g.visible)dot(police.x,police.z,'#1d4ea0',4.5,true);")
c = R(c, "['cart','Drive a golf cart in Discovery Bay']]", "['cart','Drive a golf cart in Discovery Bay'],['police','Outrun the police in a golf cart']]")
c = R(c, "beep(){tone('square',988,988,0.1,0.04);", "siren(){tone('square',960,700,0.42,0.022);tone('square',700,960,0.42,0.022,0.45)},horn(){tone('sawtooth',110,108,1.4,0.09);tone('sawtooth',165,163,1.4,0.05)},\n    beep(){tone('square',988,988,0.1,0.04);")

# ---------------------------------------------------------------- decor: plaza, D'Deck, palms, pier, ferry, village
DECOR = r'''const softColliders=[[FISH.x,FISH.z,0.6]];
const villagers=[];const dbUpd=DBX?dbDecor(DBX):null;
function dbDecor(X){const ups=[];
  const mosaic=canvasTex(256,256,(x,w,h)=>{x.fillStyle='#d3c9b3';x.fillRect(0,0,w,h);for(let i=0;i<2500;i++){x.fillStyle='rgba(0,0,0,'+(Math.random()*0.06)+')';x.fillRect(Math.random()*w,Math.random()*h,2,2)}
    x.strokeStyle='#58544d';x.lineWidth=8;for(let k=-1;k<3;k++){x.beginPath();for(let i=0;i<=w;i+=4){const y=k*128+64+Math.sin(i/w*Math.PI*2)*28;i?x.lineTo(i,y):x.moveTo(i,y)}x.stroke()}});
  mosaic.wrapS=mosaic.wrapT=THREE.RepeatWrapping;mosaic.anisotropy=ANISO;const paveM=new THREE.MeshLambertMaterial(Object.assign({map:mosaic},PO(-3)));
  function drape(test,x0,x1,z0,z1,lift,uvS){const P=[],U=[],st=1.5;for(let x=x0;x<x1;x+=st)for(let z=z0;z<z1;z+=st){if(!test(x+st/2,z+st/2))continue;
      const c=[[x,z],[x+st,z],[x+st,z+st],[x,z+st]].map(([a,b])=>[a,gridH(a,b)+lift,b]);for(const k of [0,2,1,0,3,2]){const q=c[k];P.push(q[0],q[1],q[2]);U.push(q[0]/uvS,q[2]/uvS)}}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(U,2));g.computeVertexNormals();const me=new THREE.Mesh(g,paveM);me.receiveShadow=true;scene.add(me)}
  drape((x,z)=>(x>-22&&x<42&&z>-40&&z<28)&&!bldAt(x,z),-22,42,-40,28,0.06,9);
  drape((x,z)=>segDist(x,z,DECK)[0]<4.4,-50,110,-115,-75,0.06,9);
  // wall signs on the nearest real facade
  function wallSign(px,pz,text,bg,fg,maxW,yOff){let best=null,bd=1e9;for(const b of BL){if(Math.abs(b.cx-px)>150||Math.abs(b.cz-pz)>150)continue;const p=b.p;
      for(let i=0;i<p.length;i++){const a=p[i],c=p[(i+1)%p.length];const L=Math.hypot(c[0]-a[0],c[1]-a[1]);if(L<5)continue;const mx=(a[0]+c[0])/2,mz=(a[1]+c[1])/2;const d=Math.hypot(mx-px,mz-pz);if(d<bd){bd=d;best={b,a,c,L,mx,mz}}}}
    if(!best)return;const {b,a,c,L,mx,mz}=best;let nx=-(c[1]-a[1])/L,nz=(c[0]-a[0])/L;if(inPoly(b.p,mx+nx*0.5,mz+nz*0.5)){nx=-nx;nz=-nz}const w=Math.min(L-1,maxW);
    const m=new THREE.Mesh(new THREE.PlaneGeometry(w,w*0.16),new THREE.MeshBasicMaterial({map:canvasTex(512,82,(x,W,H)=>{x.fillStyle=bg;x.fillRect(0,0,W,H);x.fillStyle=fg;x.font='bold 42px "Noto Sans TC","PingFang HK",sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText(text,W/2,H/2+2,W-24)})}));
    m.position.set(mx+nx*0.12,Math.min(b.b+b.h-0.4-w*0.08,Math.max(b.b,gridH(mx+nx*1.5,mz+nz*1.5))+yOff),mz+nz*0.12);m.rotation.y=Math.atan2(nx,nz);scene.add(m)}
  wallSign(PIAZ.x,PIAZ.z+12,'愉景廣場  DB PLAZA','#f6efdf','#b4553a',10,4.2);
  wallSign(64,-96,'海灣咖啡  BAY COFFEE','#2b2b2b','#f2c230',7,2.8);
  if(X.pier)wallSign(92,-100,'愉景灣碼頭  DISCOVERY BAY PIER','#1d4e89','#ffffff',14,3.6);
  // fountain in the middle of the piazza
  const stone=mat(0xd8cbb0),py=gridH(PIAZ.x,PIAZ.z);{const f=new THREE.Group();f.position.set(PIAZ.x,py,PIAZ.z);scene.add(f);
    cyl(stone,4.2,4.4,0.7,0,0.35,0,f,28);const wm=new THREE.Mesh(new THREE.CylinderGeometry(3.8,3.8,0.1,28),new THREE.MeshPhongMaterial({color:0x4fa3b8,transparent:true,opacity:0.85,shininess:80}));wm.position.y=0.62;f.add(wm);
    cyl(stone,0.5,0.75,1.8,0,1.2,0,f,12);cyl(stone,1.5,0.6,0.35,0,2.1,0,f,18);cyl(stone,0.18,0.25,0.7,0,2.5,0,f,8);softColliders.push([PIAZ.x,PIAZ.z,4.4])}
  ups.push(dt=>{if(Math.hypot(dog.x-PIAZ.x,dog.z-PIAZ.z)<70)for(let i=0;i<3;i++){const a=Math.random()*6.28;glow.emit(PIAZ.x,py+2.9,PIAZ.z,Math.cos(a)*1.3,3+Math.random()*1.5,Math.sin(a)*1.3,0.8,C_DROP,9.8)}});
  // palms: piazza ring, D'Deck, the back of Tai Pak Beach
  const pts=[];const okP=(x,z)=>!bldAt(x,z)&&!bldAt(x+1.5,z)&&!bldAt(x-1.5,z)&&!RMASK[cellIdx(x,z)]&&gridH(x,z)>0.8&&!pts.some(p=>Math.hypot(p[0]-x,p[1]-z)<5);
  for(let i=0;i<10;i++){const a=i/10*Math.PI*2+0.3;const x=PIAZ.x+Math.cos(a)*(PIAZ.r-2.5),z=PIAZ.z+Math.sin(a)*(PIAZ.r-2.5);if(okP(x,z))pts.push([x,z])}
  for(let i=0;i<DECK.length-1;i++){const a=DECK[i],b=DECK[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);let nx=-(b[1]-a[1])/L,nz=(b[0]-a[0])/L;const mx=(a[0]+b[0])/2,mz=(a[1]+b[1])/2;if(gridH(mx+nx*7,mz+nz*7)<gridH(mx-nx*7,mz-nz*7)){nx=-nx;nz=-nz}
    if(i%2===0){const x=mx+nx*5.5,z=mz+nz*5.5;if(okP(x,z))pts.push([x,z])}}
  for(let k=0;k<1500&&pts.length<50;k++){const a=Math.random()*6.28,r=20+Math.random()*120;const x=PL.beach[0]+Math.cos(a)*r,z=PL.beach[1]+Math.sin(a)*r;const id=cellIdx(x,z);if(CLS[id]===3||CLS[id]===4)continue;
    let near=false;for(const [ox,oz] of [[5,0],[-5,0],[0,5],[0,-5]])if(CLS[cellIdx(x+ox,z+oz)]===3)near=true;if(near&&okP(x,z))pts.push([x,z])}
  {const tg=new THREE.CylinderGeometry(0.15,0.24,7,6,7);const pa=tg.attributes.position;for(let i=0;i<pa.count;i++){const y=pa.getY(i)+3.5;pa.setY(i,y);pa.setX(i,pa.getX(i)+Math.pow(y/7,2)*0.9)}tg.computeVertexNormals();
    const P=[];for(let f=0;f<9;f++){const a=f/9*Math.PI*2+(f%2)*0.2,ca=Math.cos(a),sa=Math.sin(a),L=2.8+(f%3)*0.45;
      for(let s=0;s<6;s++){const pt=(t,side)=>{const r=t*L,y=0.55*t-1.7*t*t,w=0.34*Math.sin(Math.PI*Math.min(1,t*1.1+0.08))*side;return [ca*r-sa*w+0.9,y+7,sa*r+ca*w]};const A=pt(s/6,-1),B=pt(s/6,1),C=pt((s+1)/6,1),Dd=pt((s+1)/6,-1);P.push(...A,...B,...C,...A,...C,...Dd)}}
    const cg=new THREE.BufferGeometry();cg.setAttribute('position',new THREE.Float32BufferAttribute(P,3));cg.computeVertexNormals();
    const tr=new THREE.InstancedMesh(tg,mat(0x8a7458),pts.length),cr=new THREE.InstancedMesh(cg,new THREE.MeshLambertMaterial({color:0x4f8a3a,side:THREE.DoubleSide}),pts.length);const d=new THREE.Object3D();
    pts.forEach((p,i)=>{d.position.set(p[0],gridH(p[0],p[1])-0.1,p[1]);d.rotation.set(0,Math.random()*6.28,0);d.scale.setScalar(0.85+Math.random()*0.4);d.updateMatrix();tr.setMatrixAt(i,d.matrix);cr.setMatrixAt(i,d.matrix);softColliders.push([p[0],p[1],0.35])});
    tr.castShadow=cr.castShadow=true;tr.frustumCulled=cr.frustumCulled=false;scene.add(tr,cr)}
  // D'Deck: stone balustrade on the water side, black-and-yellow bollards and café tables on the land side
  {const rail=[],boll=[],tables=[];let acc=0;
    for(let i=0;i<DECK.length-1;i++){const a=DECK[i],b=DECK[i+1];const L=Math.hypot(b[0]-a[0],b[1]-a[1]);const ex=(b[0]-a[0])/L,ez=(b[1]-a[1])/L;let nx=-ez,nz=ex;const mx=(a[0]+b[0])/2,mz=(a[1]+b[1])/2;if(gridH(mx+nx*7,mz+nz*7)>gridH(mx-nx*7,mz-nz*7)){nx=-nx;nz=-nz}
      for(let t=0;t<L;t+=2.4){const x=a[0]+ex*t,z=a[1]+ez*t;rail.push([x+nx*4.3,z+nz*4.3,Math.atan2(ex,ez)]);acc+=2.4;if(acc>=6){acc=0;boll.push([x-nx*3.9,z-nz*3.9])}
        if(x>44&&x<82&&Math.round(t/2.4)%3===0)tables.push([x-nx*2.6,z-nz*2.6])}}
    const d=new THREE.Object3D();const pg=new THREE.BoxGeometry(0.32,0.95,0.32);pg.translate(0,0.47,0);const posts=new THREE.InstancedMesh(pg,stone,rail.length);const tops=new THREE.InstancedMesh(new THREE.BoxGeometry(0.42,0.12,2.5),stone,rail.length);
    rail.forEach((p,i)=>{const y=gridH(p[0],p[1]);d.position.set(p[0],y,p[1]);d.rotation.set(0,p[2],0);d.scale.set(1,1,1);d.updateMatrix();posts.setMatrixAt(i,d.matrix);d.position.y=y+0.98;d.updateMatrix();tops.setMatrixAt(i,d.matrix)});
    const bg=new THREE.CylinderGeometry(0.13,0.15,0.9,10);bg.translate(0,0.45,0);const bands=new THREE.InstancedMesh(new THREE.CylinderGeometry(0.155,0.155,0.12,10),mat(0xf2c230),boll.length);const bodies=new THREE.InstancedMesh(bg,mat(0x1d1d1d),boll.length);
    boll.forEach((p,i)=>{const y=gridH(p[0],p[1]);d.position.set(p[0],y,p[1]);d.rotation.set(0,0,0);d.updateMatrix();bodies.setMatrixAt(i,d.matrix);d.position.y=y+0.66;d.updateMatrix();bands.setMatrixAt(i,d.matrix);softColliders.push([p[0],p[1],0.15])});
    for(const m of [posts,tops,bodies,bands]){m.castShadow=true;m.frustumCulled=false;scene.add(m)}
    const tw=mat(0x2a2a2a),chair=mat(0x6b4b35);tables.forEach((p,i)=>{const g=new THREE.Group();g.position.set(p[0],gridH(p[0],p[1]),p[1]);scene.add(g);cyl(tw,0.45,0.45,0.04,0,0.74,0,g,14);cyl(tw,0.04,0.04,0.74,0,0.37,0,g,6);
      for(const s of [1,-1])box(chair,0.42,0.45,0.42,0.75*s,0.22,0,g);cyl(mat(0xdddddd),0.03,0.03,2.3,0,1.15,0,g,5);
      const um=new THREE.Mesh(new THREE.ConeGeometry(1.5,0.55,8,1,true),new THREE.MeshLambertMaterial({color:i%3===1?0x232323:0xc8322b,side:THREE.DoubleSide}));um.position.y=2.25;um.castShadow=true;g.add(um);softColliders.push([p[0],p[1],0.7])})}
  // the ferry: comes in, docks at the pier, leaves again
  if(X.pier){const o=obb(X.pier.p);let ux=o.ux,uz=o.uz;if(gridH(o.cx+ux*o.a*1.2,o.cz+uz*o.a*1.2)>gridH(o.cx-ux*o.a*1.2,o.cz-uz*o.a*1.2)){ux=-ux;uz=-uz}
    let nx=-uz,nz=ux;if(gridH(o.cx+nx*(o.b+12),o.cz+nz*(o.b+12))>gridH(o.cx-nx*(o.b+12),o.cz-nz*(o.b+12))){nx=-nx;nz=-nz}
    const berth=[o.cx+ux*o.a*0.3+nx*(o.b+6),o.cz+uz*o.a*0.3+nz*(o.b+6)],ctrl=[berth[0]+ux*140+nx*20,berth[1]+uz*140+nz*20],far=[berth[0]+ux*300+nx*200,berth[1]+uz*300+nz*200];
    const fg=new THREE.Group(),white=mat(0xf4f4f0),glass=mat(0x1f2b33);box(white,30,2.4,8,0,0.4,0,fg);box(mat(0x1d3557),30.1,0.5,8.1,0,-0.45,0,fg);box(mat(0x2a9d8f),30.15,0.25,8.15,0,1.1,0,fg);
    box(white,22,2.3,7,-1.5,2.75,0,fg);box(glass,21.6,0.9,7.08,-1.5,2.95,0,fg);box(white,5,1.4,4.2,5,4.6,0,fg);box(glass,5.05,0.6,4.25,5,4.75,0,fg);fg.traverse(m=>{if(m.isMesh)m.castShadow=true});scene.add(fg);
    const bez=(t)=>{const a=(1-t)*(1-t),b=2*t*(1-t),c=t*t;return [far[0]*a+ctrl[0]*b+berth[0]*c,far[1]*a+ctrl[1]*b+berth[1]*c]};
    const F={state:'dock',t:0,h:Math.atan2(-ux,-uz)};ups.push(dt=>{F.t+=dt;let p=null,u=0;
      if(F.state==='dock'){p=berth;if(F.t>45){F.state='out';F.t=0;if(Math.hypot(dog.x-berth[0],dog.z-berth[1])<220)sfx.horn()}}
      else if(F.state==='out'){u=Math.min(1,F.t/45);p=bez(1-u*u);if(u>=1){F.state='away';F.t=0}}
      else if(F.state==='away'){fg.visible=false;if(F.t>60){F.state='in';F.t=0;fg.visible=true}return}
      else{u=Math.min(1,F.t/45);const e=1-(1-u)*(1-u);p=bez(e);if(u>=1){F.state='dock';F.t=0;if(Math.hypot(dog.x-berth[0],dog.z-berth[1])<220)sfx.horn()}}
      if(F.state!=='dock'){const q=F.state==='out'?bez(Math.max(0,1-(u+0.01)*(u+0.01))):bez(Math.min(1,1-(1-u-0.01)*(1-u-0.01)));const want=Math.atan2(q[0]-p[0],q[1]-p[1]);if(isFinite(want))F.h+=angDiff(F.h,want)*Math.min(1,dt*0.5)}
      fg.position.set(p[0],Math.sin(S.t*0.8)*0.12,p[1]);fg.rotation.set(0,F.h-Math.PI/2,Math.sin(S.t*0.6)*0.015)})}
  // the village by the cove
  if(X.village.length){const tank=[mat(0xf4f4f0),mat(0x2d6fa5),mat(0x222222)],slab=mat(0xe6e2d8),railM=mat(0xf4f4f0),line=mat(0x666666);const CLOTH=[0xe8473c,0xf2c230,0x2d6fa5,0xffffff,0xf08ab0,0x2f8f5a,0x6ab0e8,0xf08a3a];
    X.village.forEach((v,vi)=>{const g=new THREE.Group();g.position.set(v.x,v.base,v.z);g.rotation.y=v.a;scene.add(g);
      for(const k of [1,2]){const y=k*2.9;box(slab,6.6,0.15,1.2,0,y,4.65,g);box(railM,6.6,0.95,0.06,0,y+0.5,5.22,g);
        box(line,6.0,0.02,0.02,0,y+2.05,4.9,g);for(let i=0;i<5;i++){const cl=new THREE.Mesh(new THREE.PlaneGeometry(0.55,0.7),new THREE.MeshLambertMaterial({color:CLOTH[(vi*3+i*2+k)%CLOTH.length],side:THREE.DoubleSide}));cl.position.set(-2.4+i*1.2,y+1.68,4.9);cl.castShadow=true;g.add(cl)}}
      box(slab,8.4,0.9,0.12,0,9.3,4.1,g);box(slab,8.4,0.9,0.12,0,9.3,-4.1,g);box(slab,0.12,0.9,8.4,4.1,9.3,0,g);box(slab,0.12,0.9,8.4,-4.1,9.3,0,g);
      cyl(tank[vi%3],0.6,0.6,1.3,2.6,9.6,-2.6,g,12);box(mat(0x8f8a80),2.2,2.2,2.2,-2.5,10,-2.4,g)});
    const v0=X.village[0];{const g=new THREE.Group();const fx=Math.sin(v0.a),fz=Math.cos(v0.a),rx=Math.cos(v0.a),rz=-Math.sin(v0.a);const sx=v0.x+fx*6+rx*3.5,sz=v0.z+fz*6+rz*3.5;g.position.set(sx,gridH(sx,sz),sz);g.rotation.y=v0.a;scene.add(g);
      box(mat(0xb8322a),0.6,0.7,0.4,0,0.35,0,g);box(mat(0xf2c230),0.4,0.3,0.02,0,0.45,0.21,g);for(const s of [-0.1,0.1])cyl(mat(0xc8322b),0.01,0.01,0.3,s,0.85,0.1,g,4);softColliders.push([sx,sz,0.5])}
    // signpost at the village edge nearest the plaza
    {let w=X.village[0];for(const v of X.village)if(Math.hypot(v.x,v.z)<Math.hypot(w.x,w.z))w=v;const dx=-w.x,dz=-w.z,L=Math.hypot(dx,dz);const sx=w.x+dx/L*9,sz=w.z+dz/L*9;const g=new THREE.Group();g.position.set(sx,gridH(sx,sz),sz);g.rotation.y=Math.atan2(dx,dz);scene.add(g);
      cyl(mat(0x5e4128),0.06,0.06,2.2,0,1.1,0,g,6);const s=new THREE.Mesh(new THREE.PlaneGeometry(1.8,0.5),new THREE.MeshBasicMaterial({side:THREE.DoubleSide,map:canvasTex(256,72,(x,W,H)=>{x.fillStyle='#1f6e4a';x.fillRect(0,0,W,H);x.fillStyle='#fff';x.font='bold 26px "Noto Sans TC",sans-serif';x.textAlign='center';x.fillText('往稔樹灣 →',W/2,30);x.font='bold 18px sans-serif';x.fillText('TO NIM SHUE WAN',W/2,58)})}));s.position.y=2.0;g.add(s)}
    // a day-off get-together by the water: folding table, stools, music, snacks
    let gx=X.vc[0],gz=X.vc[1];{const dx=395-gx,dz=235-gz,L=Math.hypot(dx,dz);for(let r=6;r<40;r+=2){const x=gx+dx/L*r,z=gz+dz/L*r;if(!bldAt(x,z)&&gridH(x,z)>0.6&&!bldAt(x+3,z)&&!bldAt(x-3,z)&&gridH(x+dx/L*4,z+dz/L*4)>0.3){gx=x;gz=z}else if(r>14)break}}
    {const g=new THREE.Group();g.position.set(gx,gridH(gx,gz),gz);scene.add(g);const white=mat(0xf4f4f0);box(white,1.5,0.05,0.8,0,0.72,0,g);for(const x of [-0.65,0.65])for(const z of [-0.32,0.32])box(mat(0x8a9196),0.04,0.7,0.04,x,0.35,z,g);
      cyl(mat(0xb8b8b8),0.18,0.15,0.22,-0.4,0.86,0,g,12);box(white,0.3,0.12,0.22,0.2,0.81,0.1,g);box(mat(0x222222),0.25,0.15,0.12,0.55,0.82,-0.2,g);
      [[0x2d6fa5,0.05],[0xf2c230,0.2]].forEach(([cc,x])=>cyl(mat(cc),0.035,0.035,0.12,x,0.81,-0.25,g,8));softColliders.push([gx,gz,1.0]);
      const looks=[{shirt:0xf08ab0,pants:0x2d4a7a},{shirt:0x6ab0e8,pants:0x2a2a3a},{shirt:0xf2c230,pants:0x4a3a5a},{shirt:0xffffff,pants:0x3a5a7a}];
      [[-1.2,0.2],[1.2,-0.1],[0.1,1.05]].forEach(([x,z],i)=>{const p=makePerson(Object.assign({hair:0x1a1410,skin:0xc68a5e},looks[i]));const wx=gx+x,wz=gz+z;cyl(mat(0xc8322b),0.17,0.14,0.45,wx,gridH(wx,wz)+0.225,wz,scene,10);
        p.g.position.set(wx,gridH(wx,wz)-0.42,wz);p.legs.forEach(l=>l.rotation.x=-1.45);facePerson(p,gx,gz,1);p.seated=true;villagers.push(p)});
      const hp=makePerson(Object.assign({hair:0x1a1410,skin:0xc68a5e},looks[3]));const hx=v0.x+Math.sin(v0.a)*6.5,hz=v0.z+Math.cos(v0.a)*6.5;hp.g.position.set(hx,gridH(hx,hz),hz);hp.g.rotation.y=v0.a+Math.PI;hp.arms.forEach(a=>a.rotation.x=-2.6);hp.hanging=true;villagers.push(hp);
      const un=makePerson({shirt:0xf4f4f0,pants:0x3a3a3a,hair:0xb0aaa0,skin:0xd2a07c});const ux2=v0.x+Math.sin(v0.a)*6+Math.cos(v0.a)*5.2,uz2=v0.z+Math.cos(v0.a)*6-Math.sin(v0.a)*5.2;cyl(mat(0x2d6fa5),0.17,0.14,0.45,ux2,gridH(ux2,uz2)+0.225,uz2,scene,10);
      un.g.position.set(ux2,gridH(ux2,uz2)-0.42,uz2);un.legs.forEach(l=>l.rotation.x=-1.45);un.seated=true;villagers.push(un)}
    const VCHAT=['Ay, may aso! A doggy!','Kain tayo! Come, sit with us!','Day off na! Finally, rest!','Ate, turn up the music!','Doggy, you live in DB? Lucky dog!','早晨! Good morning, dog!','Sige, one more song!','Who wants more pancit?'];let chatT=4;
    ups.push(dt=>{const d=Math.hypot(dog.x-gx,dog.z-gz);for(const p of villagers){if(!(p.patT>0)&&d<12&&!p.hanging)facePerson(p,dog.x,dog.z,dt);if(p.hanging&&!(p.patT>0)){p.arms[0].rotation.x=-2.6+Math.sin(S.t*2)*0.15;p.arms[1].rotation.x=-2.6+Math.cos(S.t*2)*0.15}}
      chatT-=dt;if(chatT<=0&&d<30&&S.started){chatT=6+Math.random()*4;say(pick(villagers),pick(VCHAT),2.6)}
      if(S.started&&!S.villageHint&&d<35){S.villageHint=true;toast('The village by the cove: tiled village houses, laundry on every balcony, and a day-off get-together by the water.')}})}
  return dt=>{for(const f of ups)f(dt)}}'''
c = R(c, 'const softColliders=[[FISH.x,FISH.z,0.6]];', DECOR)
c = R(c, 'function people(){return [auntie,fisher,kid].concat(walkers.map(w=>w.p))}', 'function people(){return [auntie,fisher,kid].concat(walkers.map(w=>w.p),villagers)}')
c = R(c, 'updateItems(dt);updateFeast(dt);', 'if(dbUpd)dbUpd(dt);updateItems(dt);updateFeast(dt);')
c = R(c, "if(PL.carts.length)PLACES.push(['Golf carts',PL.carts[0][0],PL.carts[0][1],'#f6f4ee']);",
         "if(PL.carts.length)PLACES.push(['Golf carts',PL.carts[0][0],PL.carts[0][1],'#f6f4ee']);if(DBX){PLACES.push(['Plaza',PIAZ.x,PIAZ.z,'#b4553a'],['Ferry pier',DECK[DECK.length-1][0],DECK[DECK.length-1][1],'#1d4e89']);if(DBX.vc)PLACES.push(['Village',DBX.vc[0],DBX.vc[1],'#e0a63a'])}")
# snapshot keeps the village hint
c = R(c, "'carryHint','sniffHinted','cartHint'])if(data[k]", "'carryHint','sniffHinted','cartHint','villageHint'])if(data[k]")
c = R(c, "sniffHinted:S.sniffHinted,cartHint:S.cartHint,", "sniffHinted:S.sniffHinted,cartHint:S.cartHint,villageHint:S.villageHint,")

out = head + c
open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(out)
print('ok', len(out))
