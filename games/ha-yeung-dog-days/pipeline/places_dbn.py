import json,pickle,math,random,os,numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import nearest_points
from shapely import wkb
random.seed(7)
IN=os.environ.get('IN','dbn');W=json.load(open(IN+'/world_base.json'));s=pickle.load(open(IN+'/state.pkl','rb'))
H,gx,gz,inSea=s['H'],s['gx'],s['gz'],s['inSea']
X0,Z0,C=W['x0'],W['z0'],W['cell'];LAT0,LON0=22.30765,114.01504;MX=111320*math.cos(math.radians(LAT0));MY=110540
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
PLC={x['names']['primary']:(x['bbox']['ymin'],x['bbox']['xmin']) for x in json.load(open(IN+'/places.json'))}
term=P(*PLC['DB North Plaza']);plaza=P(*PLC['DB North Plaza']);cafe=P(*PLC['Uncle Russ Coffee'])
# bus route: shortest path over the main roads from the tunnel (west edge) to North Plaza
import heapq,collections
NODES={};ADJ=collections.defaultdict(list)
def nid(p):
  k=(round(p[0]),round(p[1]))
  if k not in NODES:NODES[k]=len(NODES)
  return NODES[k]
for r in W['roads']:
  if r['w']<7:continue
  for a,b in zip(r['p'],r['p'][1:]):
    i,j=nid(a),nid(b);d=math.hypot(a[0]-b[0],a[1]-b[1]);ADJ[i].append((j,d));ADJ[j].append((i,d))
POS={v:k for k,v in NODES.items()}
near=lambda x,z:min(NODES.items(),key=lambda kv:(kv[0][0]-x)**2+(kv[0][1]-z)**2)[1]
src_=min(NODES.items(),key=lambda kv:kv[0][0])[1];dst=near(*term)
dist={src_:0};prev={};pq=[(0,src_)]
while pq:
  d,u=heapq.heappop(pq)
  if u==dst:break
  if d>dist.get(u,1e18):continue
  for v,w in ADJ[u]:
    if d+w<dist.get(v,1e18):dist[v]=d+w;prev[v]=u;heapq.heappush(pq,(d+w,v))
path=[dst]
while path[-1]!=src_:path.append(prev[path[-1]])
path=[list(POS[i]) for i in reversed(path)]
# run the route a little past the plaza so the bus can stop and drive on
W['cwb']=[[float(p[0]),float(p[1])] for p in path]
cw=LineString(W['cwb'])
print('route',len(path),path[0],path[-1],round(cw.length))
sstop=min(cw.project(Point(*term)),cw.length-25);p0=cw.interpolate(sstop);p1=cw.interpolate(min(cw.length,sstop+2));dx,dz=p1.x-p0.x,p1.y-p0.y;L=math.hypot(dx,dz) or 1;fx,fz=dx/L,dz/L;lx,lz=fz,-fx
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
LAND=json.load(open(IN+'/land.json'));bc=None;ba=0
for x in LAND:
  if x['class']=='beach':
    g=wkb.loads(bytes.fromhex(x['geometry']));c=g.centroid;a=g.area
    q=P(c.y,c.x)
    if a>ba and X0<q[0]<X0+(W['nx']-1)*C and Z0<q[1]<Z0+(W['nz']-1)*C:ba=a;bc=[round(v,1) for v in q]
print('beach',bc)
kid=landpt(bc[0],bc[1],30,maxh=2.5)
sea=np.argwhere(inSea);spts=np.column_stack([gx[sea[:,1]],gz[sea[:,0]]])
def tosea(p):k=np.argmin((spts[:,0]-p[0])**2+(spts[:,1]-p[1])**2);return [float(spts[k,0]),float(spts[k,1])]
pier=P(*PLC['Love Lock Promenade, Discovery Bay, Hong Kong'])
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
W['level']='dbn';W['name']='Discovery Bay North';W['nameZh']='愉景北';W['busDest']='愉景北 DB NORTH';W['otherDest']='愉景灣 DISCOVERY BAY';W['signText']='北灣咖啡  NORTH BAY COFFEE';W['roadName']='Siena Avenue'
print(json.dumps(W['places'])[:900])
json.dump(W,open(IN+'/world.json','w'),separators=(',',':'))
