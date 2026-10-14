import json,math,base64,heapq,collections
import numpy as np, shapely
from shapely import wkb
from shapely.geometry import Point,LineString,box as sbox
from PIL import Image
import os
IN=os.environ.get('IN','dem');LAT0,LON0=[float(v) for v in os.environ.get('CENTER','22.304332,114.286545').split(',')]
MX=111320*math.cos(math.radians(LAT0));MY=110540
def P(lon,lat):return ((lon-LON0)*MX,-(lat-LAT0)*MY)
def inv(x,z):return (LON0+x/MX, LAT0-z/MY)
X0,X1,Z0,Z1=[int(v) for v in os.environ.get('BOX','-330,720,-420,330').split(',')];CELL=3
import os
CANOPY_WOOD=float(os.environ.get('CW','10'));CANOPY_SHRUB=float(os.environ.get('CS','3'));CANOPY_WILD=float(os.environ.get('CG','0'));RAMP=float(os.environ.get('RAMP','25'))
NX=(X1-X0)//CELL+1;NZ=(Z1-Z0)//CELL+1
L=lambda f:[(x,wkb.loads(bytes.fromhex(x['geometry']))) for x in json.load(open(f))]
def tolocal(g):return shapely.transform(g,lambda a:np.column_stack([(a[:,0]-LON0)*MX,-(a[:,1]-LAT0)*MY]))
# --- DEM sampling (terrarium mosaic) ---
big=np.load(IN+'/big.npy');big=np.clip(big,-25,400)
z=15;n=2**z;lr=math.radians(LAT0)
fx=(LON0+180)/360*n;fy=(1-math.log(math.tan(lr)+1/math.cos(lr))/math.pi)/2*n
TX,TY=int(fx)-2,int(fy)-2
def dem_px(lon,lat):
  x=(lon+180)/360*n;r=np.radians(lat);y=(1-np.log(np.tan(r)+1/np.cos(r))/math.pi)/2*n
  return (x-TX)*256-0.5,(y-TY)*256-0.5
def sample(arr,px,py):
  px=np.clip(px,0,arr.shape[1]-1.001);py=np.clip(py,0,arr.shape[0]-1.001)
  i=np.floor(px).astype(int);j=np.floor(py).astype(int);u=px-i;v=py-j
  return arr[j,i]*(1-u)*(1-v)+arr[j,i+1]*u*(1-v)+arr[j+1,i]*(1-u)*v+arr[j+1,i+1]*u*v
gx=X0+np.arange(NX)*CELL;gz=Z0+np.arange(NZ)*CELL;GX,GZ=np.meshgrid(gx,gz)
lon,lat=inv(GX,GZ);px,py=dem_px(lon,lat);H=sample(big,px,py)
# --- masks ---
water=[(x,tolocal(g)) for x,g in L(IN+'/water.json')]
sea=shapely.union_all([g for x,g in water if x['subtype'] in('ocean','physical') and g.geom_type in('Polygon','MultiPolygon')])
inSea=shapely.contains_xy(sea,GX,GZ)
land=[(x,tolocal(g)) for x,g in L(IN+'/land.json')]
lu=[(x,tolocal(g)) for x,g in L(IN+'/landuse.json')]
def mask(geoms):
  gs=[g for g in geoms if g.geom_type in('Polygon','MultiPolygon')]
  if not gs:return np.zeros_like(inSea)
  return shapely.contains_xy(shapely.union_all(gs),GX,GZ)
beach=mask([g for x,g in land if x['class']=='beach'])
forest=mask([g for x,g in land if x['subtype'] in('forest','shrub','tree')])
devel=mask([g for x,g in lu if x['subtype'] in('residential','developed','construction','education')])
# heights: sea below 0, land above
dsea=np.where(inSea,1,0)
H=np.where(inSea,np.minimum(H,-1.2),np.maximum(H,0.5))
# deepen sea with distance to shore (cheap: blur of mask)
from scipy.ndimage import distance_transform_edt,gaussian_filter
dist_in=distance_transform_edt(inSea)*CELL;dist_out=distance_transform_edt(~inSea)*CELL
H=np.where(inSea,np.minimum(H,-0.8-dist_in*0.12),H)
H=np.where(inSea,np.maximum(H,-14),H)
# land near shore: gentle ramp to waterline (DEM is coarse at coastline)
# canopy correction: the elevation tiles are a surface model (tree tops), so lower wooded land to approximate bare ground
wood=mask([g for x,g in land if x['subtype']=='forest'])
shrub=mask([g for x,g in land if x['subtype'] in('shrub','tree')])
wild=(~inSea)&(~wood)&(~shrub)&(~devel)
canopy=gaussian_filter(wood.astype(float)*CANOPY_WOOD+shrub.astype(float)*CANOPY_SHRUB+wild.astype(float)*CANOPY_WILD,2.0)
H=np.where(~inSea,np.maximum(H-canopy,0.6),H)
ramp=np.clip(dist_out/RAMP,0,1)
H=np.where(~inSea,0.4+(H-0.4)*(ramp*ramp*(3-2*ramp))+ (beach*0),H)
H=np.where(beach&~inSea,np.minimum(H,0.3+dist_out*0.06),H)
# --- roads ---
roads=[];RW={'primary':9,'secondary':9,'tertiary':7,'residential':4.5,'unclassified':4.5,'living_street':4,'service':3.5,'track':3,'footway':1.8,'path':1.4,'steps':1.8,'cycleway':2}
for x,g in L(IN+'/roads.json'):
  if x['subtype']!='road' or x['class'] not in RW:continue
  g=tolocal(g).intersection(sbox(X0+3,Z0+3,X1-3,Z1-3))
  for ls in getattr(g,'geoms',[g]):
    if ls.is_empty or ls.geom_type!='LineString' or ls.length<2:continue
    nm=((x.get('names') or {}).get('primary')) or ''
    roads.append(dict(c=x['class'],w=RW[x['class']],name=nm,ls=ls))
# road profiles: sample terrain along line and smooth, then flatten terrain under road
from scipy.interpolate import RegularGridInterpolator
Hs=gaussian_filter(H,1.0)
interp=lambda arr:RegularGridInterpolator((gz,gx),arr,bounds_error=False,fill_value=None)
Hi=interp(Hs)
Hflat=H.copy();wsum=np.zeros_like(H);acc=np.zeros_like(H)
for r in sorted(roads,key=lambda r:r['w']):
  ls=r['ls'];L_=ls.length;k=max(2,int(L_/2))
  pts=[ls.interpolate(t*L_/(k-1)) for t in range(k)]
  hh=Hi([[p.y,p.x] for p in pts]);
  win=15 if r['w']>=7 else 7
  if len(hh)>win:hh=np.convolve(np.pad(hh,win//2,mode='edge'),np.ones(win)/win,mode='valid')
  elif len(hh)>2:hh=np.full_like(hh,hh.mean())*0.5+hh*0.5
  hh=np.maximum(hh,0.6)
  r['pts']=[[round(p.x,1),round(p.y,1),round(float(h),2)] for p,h in zip(pts,hh)]
  hw=r['w']/2+(7 if r['w']>=7 else 2.5);core=r['w']/2+0.6
  for p,h in zip(pts,hh):
    i0=int((p.x-hw-X0)//CELL);i1=int((p.x+hw-X0)//CELL)+1;j0=int((p.y-hw-Z0)//CELL);j1=int((p.y+hw-Z0)//CELL)+1
    for j in range(max(0,j0),min(NZ,j1+1)):
      for i in range(max(0,i0),min(NX,i1+1)):
        d=math.hypot(gx[i]-p.x,gz[j]-p.y)
        if d<hw:
          w=1.0 if d<core else ((hw-d)/(hw-core))**1.5
          w*= (3 if r['w']>=7 else 1)
          acc[j,i]+=h*w;wsum[j,i]+=w
m=wsum>0;Hflat[m]=np.where(inSea[m],Hflat[m],acc[m]/wsum[m])
H=Hflat
# --- building platforms: level the ground under each house (HK village houses sit on cut terraces) ---
from shapely import contains_xy
Hplat=H.copy();onroad=wsum>0
for x,g in L(IN+'/buildings.json'):
  g=tolocal(g)
  if g.geom_type=='MultiPolygon':g=max(g.geoms,key=lambda a:a.area)
  if g.geom_type!='Polygon':continue
  mnx,mnz,mxx,mxz=g.bounds
  if mxx<X0 or mnx>X1 or mxz<Z0 or mnz>Z1:continue
  i0=max(0,int((mnx-6-X0)//CELL));i1=min(NX-1,int((mxx+6-X0)//CELL)+1);j0=max(0,int((mnz-6-Z0)//CELL));j1=min(NZ-1,int((mxz+6-Z0)//CELL)+1)
  sx=GX[j0:j1+1,i0:i1+1];sz=GZ[j0:j1+1,i0:i1+1]
  inside=contains_xy(g,sx,sz)
  if not inside.any():
    c=g.centroid;inside=contains_xy(g.buffer(2),sx,sz)
    if not inside.any():continue
  sub=H[j0:j1+1,i0:i1+1];plat=float(np.median(sub[inside]))
  d=shapely.distance(g,shapely.points(sx,sz)) if hasattr(shapely,'points') else None
  w=np.clip(1-(d-1.5)/4.5,0,1)  # 1 within 1.5 m of the walls, fading to 0 by 6 m
  blk=Hplat[j0:j1+1,i0:i1+1];sea=inSea[j0:j1+1,i0:i1+1];rd=onroad[j0:j1+1,i0:i1+1]
  w=np.where(sea|rd,0,w)
  Hplat[j0:j1+1,i0:i1+1]=blk*(1-w)+plat*w
H=Hplat
Hi=interp(H)
# --- buildings ---
bl=[]
for x,g in L(IN+'/buildings.json'):
  g=tolocal(g)
  if g.geom_type=='MultiPolygon':g=max(g.geoms,key=lambda a:a.area)
  if g.geom_type!='Polygon':continue
  c=g.centroid
  if not(X0+8<c.x<X1-8 and Z0+8<c.y<Z1-8):continue
  g=g.simplify(0.3)
  fl=x['num_floors'] or (3 if g.area<200 else 4)
  hgt=x['height'] or fl*2.9
  hgt=min(hgt,60)
  co=list(g.exterior.coords)[:-1]
  hs=Hi([[q[1],q[0]] for q in co]+[[c.y,c.x]])
  base=float(np.median(hs))-0.6
  bl.append(dict(p=[[round(a,1),round(b,1)] for a,b in co],b=round(base,2),h=round(float(hgt+0.6),2),f=int(fl),a=round(g.area),cx=round(c.x,1),cz=round(c.y,1)))
# flatten terrain a bit under buildings? (they sink instead)
# --- surface classes for colour: 0 grass,1 forest,2 developed,3 beach,4 sea, 5 rock(shore)
cls=np.zeros(H.shape,np.uint8)
cls[forest]=1;cls[devel]=2
cls[(~inSea)&(dist_out<7)]=5
cls[beach&~inSea]=3
cls[inSea]=4
# --- outer coarse terrain (for horizon) ---
step=6;ob=big[::step,::step];oh,ow=ob.shape
ox=np.arange(ow)*step;oy=np.arange(oh)*step
OXP,OYP=np.meshgrid(ox+0.5,oy+0.5)
olon=(OXP/256+TX)/n*360-180;olat=np.degrees(np.arctan(np.sinh(math.pi*(1-2*(OYP/256+TY)/n))))
OX,OZ=P(olon,olat)
# --- graph routing on roads for walkers ---
nodes={};adj=collections.defaultdict(list)
def nid(pt):
  k=(round(pt[0]),round(pt[1]))
  if k not in nodes:nodes[k]=len(nodes)
  return nodes[k]
for r in roads:
  if r['c'] in('primary','secondary'):continue
  ps=r['pts']
  for a,b in zip(ps,ps[1:]):
    i,j=nid(a),nid(b);d=math.hypot(a[0]-b[0],a[1]-b[1]);adj[i].append((j,d));adj[j].append((i,d))
npos={v:k for k,v in nodes.items()}
def nearest_node(x,z):return min(nodes.items(),key=lambda kv:(kv[0][0]-x)**2+(kv[0][1]-z)**2)[1]
def route(a,b):
  dist={a:0};prev={};pq=[(0,a)]
  while pq:
    d,u=heapq.heappop(pq)
    if u==b:break
    if d>dist.get(u,1e18):continue
    for v,w in adj[u]:
      nd=d+w
      if nd<dist.get(v,1e18):dist[v]=nd;prev[v]=u;heapq.heappush(pq,(nd,v))
  if b not in dist:return None
  path=[b]
  while path[-1]!=a:path.append(prev[path[-1]])
  return [list(npos[i]) for i in reversed(path)]
# --- key places ---
MAIN=os.environ.get('MAINROAD','Clear Water Bay Road');JUNC=os.environ.get('JUNCROAD','Ha Yeung Road')
cwb=[r for r in roads if MAIN in r['name']]
hy=[r for r in roads if JUNC in r['name']] or cwb
# merge CWB into single polyline ordered north->south
segs=[r['pts'] for r in cwb]
cw=shapely.line_merge(shapely.MultiLineString([[(p[0],p[1]) for p in s] for s in segs]))
if cw.geom_type=='MultiLineString':cw=max(cw.geoms,key=lambda a:a.length)
cwc=list(cw.coords)
if cwc[0][1]>cwc[-1][1]:cwc=cwc[::-1]
# junction: nearest CWB point to Ha Yeung road's westmost point
hypts=[p for r in hy for p in r['pts']]
wpt=min(hypts,key=lambda p:p[0]);print('HY west point',wpt,'HY segs',len(hy))
jd=cw.project(Point(wpt[0],wpt[1]));
out=dict(origin=[LAT0,LON0],x0=X0,z0=Z0,cell=CELL,nx=NX,nz=NZ)
out['h']=base64.b64encode((np.round(H*10).astype('<i2')).tobytes()).decode()
out['cls']=base64.b64encode(cls.tobytes()).decode()
out['outer']=dict(w=ow,h=oh,x=[round(v,1) for v in OX.flatten()],z=[round(v,1) for v in OZ.flatten()],e=[round(float(v),1) for v in ob.flatten()])
out['roads']=[dict(c=r['c'],w=r['w'],n=r['name'],p=r['pts']) for r in roads]
out['bld']=bl
out['cwb']=[[round(a,1),round(b,1)] for a,b in cwc];out['junction_s']=round(jd,1)
json.dump(out,open(IN+'/world_base.json','w'))
import pickle;pickle.dump(dict(H=H,cls=cls,gx=gx,gz=gz,inSea=inSea,dist_out=dist_out,beach=beach,nodes=nodes,adj=dict(adj),cwc=cwc,jd=jd,wpt=wpt),open(IN+'/state.pkl','wb'))
print('roads',len(roads),'bld',len(bl),'grid',NX,NZ,'beach cells',int((beach&~inSea).sum()))
# preview
c=np.zeros(H.shape+(3,))
pal=np.array([[110,150,70],[60,105,55],[170,165,150],[230,210,160],[40,100,140],[140,130,115]])/255
c=pal[cls]*np.clip(0.75+H[...,None]/200,0.5,1.2)
im=Image.fromarray((np.clip(c,0,1)*255).astype('uint8')).resize((NX*2,NZ*2),Image.NEAREST)
from PIL import ImageDraw;d=ImageDraw.Draw(im)
f=lambda x,z:((x-X0)/CELL*2,(z-Z0)/CELL*2)
for r in roads:d.line([f(p[0],p[1]) for p in r['pts']],fill=(255,140,40) if r['w']>=7 else (250,250,250) if r['w']>=3 else (180,255,180),width=max(1,int(r['w']/1.5)))
for b in bl:d.polygon([f(*p) for p in b['p']],fill=(225,205,175))
jp=cw.interpolate(jd);d.ellipse([*f(jp.x-8,jp.y-8),*f(jp.x+8,jp.y+8)],outline=(255,0,0),width=3)
im.save(IN+'/world_preview.png')
