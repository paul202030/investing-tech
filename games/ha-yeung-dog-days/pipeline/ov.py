import requests,re,io,json,sys,concurrent.futures as cf
import pyarrow.parquet as pq
B="https://overturemaps-us-west-2.s3.amazonaws.com"
REL="release/2026-09-23.1"
S=requests.Session()
class RF(io.RawIOBase):
  def __init__(s,url):
    s.url=url;s.pos=0;s.size=int(S.head(url).headers['Content-Length'])
  def seekable(s):return True
  def readable(s):return True
  def tell(s):return s.pos
  def seek(s,o,w=0):
    s.pos={0:o,1:s.pos+o,2:s.size+o}[w];return s.pos
  def read(s,n=-1):
    if n<0:n=s.size-s.pos
    if n==0 or s.pos>=s.size:return b''
    r=S.get(s.url,headers={'Range':f'bytes={s.pos}-{s.pos+n-1}'});d=r.content;s.pos+=len(d);return d
  def readinto(s,b):
    d=s.read(len(b));b[:len(d)]=d;return len(d)
def listf(prefix):
  keys=[];tok=None
  while True:
    u=f"{B}/?list-type=2&prefix={prefix}"+(f"&continuation-token={requests.utils.quote(tok)}" if tok else "")
    t=S.get(u).text;keys+=re.findall(r"<Key>([^<]+)</Key>",t)
    m=re.search(r"<NextContinuationToken>([^<]+)<",t)
    if not m:break
    tok=m.group(1)
  return [k for k in keys if k.endswith('.parquet') or 'part-' in k]
import os
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BBOX','114.272,114.300,22.292,22.316').split(',')]
OUT=os.environ.get('OUT','dem')
def scan(key,cols):
  f=pq.ParquetFile(RF(f"{B}/{key}"))
  md=f.metadata;names=[md.schema.column(i).path for i in range(md.num_columns)]
  ix={n:names.index(n) for n in ['bbox.xmin','bbox.xmax','bbox.ymin','bbox.ymax']}
  rgs=[]
  for g in range(md.num_row_groups):
    rg=md.row_group(g);st={k:rg.column(i).statistics for k,i in ix.items()}
    if st['bbox.xmin'].min>X1 or st['bbox.xmax'].max<X0 or st['bbox.ymin'].min>Y1 or st['bbox.ymax'].max<Y0:continue
    rgs.append(g)
  if not rgs:return []
  t=f.read_row_groups(rgs,columns=cols).to_pylist()
  return [r for r in t if r['bbox']['xmin']<X1 and r['bbox']['xmax']>X0 and r['bbox']['ymin']<Y1 and r['bbox']['ymax']>Y0]
def run(theme,typ,cols,out):
  keys=listf(f"{REL}/theme={theme}/type={typ}/")
  print(theme,typ,len(keys),'files',file=sys.stderr)
  res=[]
  with cf.ThreadPoolExecutor(16) as ex:
    for r in ex.map(lambda k:scan(k,cols),keys):res+=r
  for r in res:
    g=r.get('geometry')
    if isinstance(g,bytes):r['geometry']=g.hex()
  json.dump(res,open(out,'w'),default=str);print(out,len(res),file=sys.stderr)
which=sys.argv[1]
if which=='roads':run('transportation','segment',['id','bbox','geometry','class','subtype','names'],OUT+'/roads.json')
if which=='bldg':run('buildings','building',['id','bbox','geometry','height','num_floors','class'],OUT+'/buildings.json')
if which=='water':run('base','water',['id','bbox','geometry','class','subtype'],OUT+'/water.json')
if which=='land':run('base','land',['id','bbox','geometry','class','subtype'],OUT+'/land.json')
if which=='landuse':run('base','land_use',['id','bbox','geometry','class','subtype'],OUT+'/landuse.json')

if which=='places':run('places','place',['id','bbox','geometry','names','categories'],OUT+'/places.json')
