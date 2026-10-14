import json,pickle,math,random,numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import nearest_points
from shapely import wkb
random.seed(7)
W=json.load(open('db/world_base.json'));s=pickle.load(open('db/state.pkl','rb'))
H,gx,gz,inSea=s['H'],s['gx'],s['gz'],s['inSea']
X0,Z0,C=W['x0'],W['z0'],W['cell'];LAT0,LON0=22.29589,114.0165;MX=111320*math.cos(math.radians(LAT0));MY=110540
P=lambda lat,lon:((lon-LON0)*MX,-(lat-LAT0)*MY)
def gh(x,z):
  i=(x-X0)/C;j=(z-Z0)/C;i0=int(i);j0=int(j);u=i-i0;v=j-j0
  return float(H[j0,i0]*(1-u)*(1-v)+H[j0,i0+1]*u*(1-v)+H[j0+1,i0]*(1-u)*v+H[j0+1,i0+1]*u*v)
lines=[(r,LineString([(p[0],p[1]) for p in r['p']])) for r in W['roads']]
B=W['bld'];polys=[Polygon(b['p']) for b in B]
free=lambda x,z,m=1.0:all(not p.buffer(m).contains(Point(x,z)) for p in polys)
def nearest_road(x,z):
  best=None
  for r,l in lines:
    d=l.distance(Point(x,z))
    if best is None or d<best[0]:best=(d,r,l)
  return best
def door_of(i,push=1.6):
  pg=polys[i];c=pg.centroid;d,r,l=nearest_road(c.x,c.y);rp=nearest_points(l,c)[0];bp=nearest_points(pg.exterior,rp)[0]
  vx,vz=bp.x-c.x,bp.y-c.y;L=math.hypot(vx,vz) or 1;return [round(bp.x+vx/L*push,1),round(bp.y+vz/L*push,1)],[rp.x,rp.y]
def landpt(cx,cz,r,maxh=4,minh=0.35,tries=6000):
  for _ in range(tries):
    a=random.random()*6.283;rr=r*math.sqrt(random.random());x,z=cx+math.cos(a)*rr,cz+math.sin(a)*rr;h=gh(x,z)
    if minh<h<maxh and free(x,z,1.5):return [round(x,1),round(z,1)]
  return None
# main road chain (Discovery Bay Road) as built
cw=LineString(W['cwb'])
term=P(22.29574,114.01759);plaza=P(22.29589,114.0165);cafe=P(22.29658,114.01691)
sstop=cw.project(Point(*term));p0=cw.interpolate(sstop);p1=cw.interpolate(min(cw.length,sstop+2));dx,dz=p1.x-p0.x,p1.y-p0.y;L=math.hypot(dx,dz) or 1;fx,fz=dx/L,dz/L;lx,lz=fz,-fx
stop=[round(p0.x+lx*6.2,1),round(p0.y+lz*6.2,1)]
if not free(*stop,0.5):stop=[round(p0.x-lx*6.2,1),round(p0.y-lz*6.2,1)]
W['junction_s']=round(max(0,sstop-30),1)
# rest spot (bed + bowl) on open ground near the plaza, and the café "auntie"
rest=landpt(plaza[0],plaza[1]+20,45,maxh=40,minh=0.5);print('rest',rest)
shop=min([i for i,b in enumerate(B) if b['a']>60],key=lambda i:polys[i].distance(Point(*cafe)))
sd,srp=door_of(shop,1.4);sp=polys[shop];ex=list(sp.exterior.coords);best=None
for a,b in zip(ex,ex[1:]):
  d=LineString([a,b]).distance(Point(*srp))
  if best is None or d<best[0]:best=(d,a,b)
home=min([i for i,b in enumerate(B) if 40<b['a']<400 and i!=shop],key=lambda i:polys[i].distance(Point(*rest)))
# Tai Pak Beach: largest beach polygon
LAND=json.load(open('db/land.json'));bc=None;ba=0
for x in LAND:
  if x['class']=='beach':
    g=wkb.loads(bytes.fromhex(x['geometry']));c=g.centroid;a=g.area
    if a>ba:ba=a;bc=[round(v,1) for v in P(c.y,c.x)]
print('beach',bc)
kid=landpt(bc[0],bc[1],30,maxh=2.5)
sea=np.argwhere(inSea);spts=np.column_stack([gx[sea[:,1]],gz[sea[:,0]]])
def tosea(p):k=np.argmin((spts[:,0]-p[0])**2+(spts[:,1]-p[1])**2);return [float(spts[k,0]),float(spts[k,1])]
pier=P(22.29677,114.01776)
fi=landpt(pier[0]-40,pier[1]+30,45,maxh=4,minh=0.4)
digs=[landpt(bc[0],bc[1],35,maxh=3) for _ in range(4)]+[landpt(plaza[0],plaza[1],200,maxh=60) for _ in range(4)]
cand=[i for i,b in enumerate(B) if 40<b['a']<400]
perch=[door_of(i,1.2)[0] for i in sorted(cand,key=lambda i:polys[i].distance(Point(*rest)))[:8]]
# golf cart parking spots: beside lanes near the plaza and the beach
carts=[]
for r,l in sorted(lines,key=lambda rl:rl[1].distance(Point(*plaza))):
  if r['w']>=7 or r['w']<3:continue
  m=l.interpolate(0.5,normalized=True);
  for side in (1,-1):
    a=l.interpolate(max(0,l.project(m)-1));b=l.interpolate(min(l.length,l.project(m)+1));dx,dz=b.x-a.x,b.y-a.y;LL=math.hypot(dx,dz) or 1
    q=[round(m.x-dz/LL*side*(r['w']/2+1.4),1),round(m.y+dx/LL*side*(r['w']/2+1.4),1),round(math.atan2(dx,dz),3)]
    if free(q[0],q[1],1.2) and gh(q[0],q[1])>0.4:carts.append(q);break
  if len(carts)>=6:break
W['places']=dict(home=home,door=rest,bed=[rest[0]+1.6,rest[1]],bowl=[rest[0]-1.2,rest[1]+0.6],start=stop,stop_s=round(sstop,1),stop=stop,shop=shop,auntie=sd,sign=[best[1],best[2]],
  beach=bc,kid=kid,fisher=fi,fisherLook=tosea(fi),digs=digs,perch=perch,carts=carts,noHome=True)
W['level']='db';W['name']='Discovery Bay';W['nameZh']='愉景灣';W['busDest']='愉景灣 DISCOVERY BAY';W['otherDest']='下洋 HA YEUNG';W['signText']='愉景茶餐廳  DB CAFÉ';W['roadName']='Discovery Bay Road'
print(json.dumps(W['places'])[:900])
json.dump(W,open('db/world.json','w'),separators=(',',':'))
