import json,pickle,math,random,numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import nearest_points
random.seed(4)
W=json.load(open('dem/world_base.json'));s=pickle.load(open('dem/state.pkl','rb'))
H,gx,gz,inSea,do=s['H'],s['gx'],s['gz'],s['inSea'],s['dist_out']
X0,Z0,C=W['x0'],W['z0'],W['cell']
def gh(x,z):
  i=(x-X0)/C;j=(z-Z0)/C;i0=int(i);j0=int(j);u=i-i0;v=j-j0
  return float(H[j0,i0]*(1-u)*(1-v)+H[j0,i0+1]*u*(1-v)+H[j0+1,i0]*(1-u)*v+H[j0+1,i0+1]*u*v)
lines=[(r,LineString([(p[0],p[1]) for p in r['p']])) for r in W['roads']]
def nearest_road(x,z,classes=None):
  best=None
  for r,l in lines:
    if classes and r['c'] not in classes:continue
    d=l.distance(Point(x,z))
    if best is None or d<best[0]:best=(d,r,l)
  return best
B=W['bld'];polys=[Polygon(b['p']) for b in B]
def door_of(i,push=1.6):
  pg=polys[i];c=pg.centroid
  d,r,l=nearest_road(c.x,c.y)
  rp=nearest_points(l,c)[0]
  bp=nearest_points(pg.exterior,rp)[0]
  vx,vz=bp.x-c.x,bp.y-c.y;L=math.hypot(vx,vz) or 1
  return [round(bp.x+vx/L*push,1),round(bp.y+vz/L*push,1)],[rp.x,rp.y]
free=lambda x,z,m=1.0:all(not p.buffer(m).contains(Point(x,z)) for p in polys)
# home: 3-storey house nearest origin
cand=[i for i,b in enumerate(B) if 50<b['a']<200]
home=min(cand,key=lambda i:math.hypot(B[i]['cx'],B[i]['cz']))
hd,_=door_of(home)
c=polys[home].centroid;vx,vz=hd[0]-c.x,hd[1]-c.y;L=math.hypot(vx,vz);ux,uz=vx/L,vz/L;px_,pz_=-uz,ux
bed=[round(hd[0]+px_*2.2,1),round(hd[1]+pz_*2.2,1)];bowl=[round(hd[0]-px_*2.0,1),round(hd[1]-pz_*2.0,1)]
start=[round(hd[0]+ux*1.8,1),round(hd[1]+uz*1.8,1)]
# bus stop on CWB just past the junction (southbound, east kerb)
segs=[[(p[0],p[1]) for p in r['p']] for r in W['roads'] if 'Clear Water' in r['n']]
cur=(-144.4,-417.0);chain=[cur];used=set()
while True:
  nxt=None
  for k,sg in enumerate(segs):
    if k in used:continue
    for seq in (sg,sg[::-1]):
      if abs(seq[0][0]-cur[0])<0.2 and abs(seq[0][1]-cur[1])<0.2 and not (abs(seq[-1][0]+133.5)<0.2 and abs(seq[-1][1]-27.9)<0.2):
        nxt=(k,seq);break
    if nxt:break
  if not nxt:break
  used.add(nxt[0]);chain+=nxt[1][1:];cur=chain[-1]
cw=LineString(chain);W['cwb']=[[round(a,1),round(b,1)] for a,b in chain]
W['junction_s']=round(cw.project(Point(-133.5,27.9)),1);print('cwb len',cw.length,'junction',W['junction_s'],chain[-1])
sstop=W['junction_s']+22
p0=cw.interpolate(sstop);p1=cw.interpolate(sstop+2);dx,dz=p1.x-p0.x,p1.y-p0.y;L=math.hypot(dx,dz);fx,fz=dx/L,dz/L
lx,lz=fz,-fx  # left of southbound travel (check sign below)
# left = up x forward = (fz,0,-fx)
stop=[round(p0.x+lx*6.2,1),round(p0.y+lz*6.2,1)]
# shop: building nearest the junction, on the village side
jp=cw.interpolate(W['junction_s'])
shop=min([i for i,b in enumerate(B) if b['a']>30 and i!=home and b['cx']>jp.x],key=lambda i:polys[i].distance(Point(jp.x,jp.y)))
sd,srp=door_of(shop,1.4)
sp=polys[shop];sc=sp.centroid
# sign edge: edge of shop closest to its road point
ex=list(sp.exterior.coords);best=None
for a,b in zip(ex,ex[1:]):
  d=LineString([a,b]).distance(Point(*srp))
  if best is None or d<best[0]:best=(d,a,b)
_,ea,eb=best
# beach + shore spots
bc=[431,-301]
def landpt(cx,cz,r,maxh=4,minh=0.35,tries=4000,needfree=True):
  for _ in range(tries):
    a=random.random()*6.283;rr=r*math.sqrt(random.random());x,z=cx+math.cos(a)*rr,cz+math.sin(a)*rr
    h=gh(x,z)
    if minh<h<maxh and (not needfree or free(x,z,1.5)):return [round(x,1),round(z,1)]
  return None
kid=landpt(bc[0],bc[1],25,maxh=2.5)
# fisherman: shore point near road end (642,13.5)
fi=landpt(632,8,30,maxh=3,minh=0.4)
# facing for fisherman: toward nearest sea cell
sea=np.argwhere(inSea);sp_=np.column_stack([gx[sea[:,1]],gz[sea[:,0]]])
def tosea(p):
  k=np.argmin((sp_[:,0]-p[0])**2+(sp_[:,1]-p[1])**2);return [float(sp_[k,0]),float(sp_[k,1])]
digs=[landpt(bc[0],bc[1],30,maxh=3) for _ in range(3)]+[landpt(60,0,170,maxh=120) for _ in range(5)]
perch=[door_of(i,1.2)[0] for i in sorted(cand,key=lambda i:math.hypot(B[i]['cx']-B[home]['cx'],B[i]['cz']-B[home]['cz']))[1:9]]
W['places']=dict(home=home,door=hd,bed=bed,bowl=bowl,start=start,stop_s=round(sstop,1),stop=stop,shop=shop,auntie=sd,sign=[ea,eb],
  beach=bc,kid=kid,fisher=fi,fisherLook=tosea(fi),digs=digs,perch=perch)
print(json.dumps(W['places']))
print('home h',gh(*hd),'stop h',gh(*stop),'kid h',gh(*kid),'fisher h',gh(*fi),'beach dist from home',math.hypot(bc[0]-hd[0],bc[1]-hd[1]))
json.dump(W,open('dem/world.json','w'),separators=(',',':'))
