import json,base64,numpy as np,math
W=json.load(open('dem/world.json'));nx,nz=W['nx'],W['nz'];X0,Z0,C=W['x0'],W['z0'],W['cell']
H=np.frombuffer(base64.b64decode(W['h']),dtype='<i2').reshape(nz,nx)/10
cls=np.frombuffer(base64.b64decode(W['cls']),dtype=np.uint8).reshape(nz,nx)
def g(x,z):j=int(round((z-Z0)/C));i=int(round((x-X0)/C));return float(H[j,i]),int(cls[j,i])
hy=[r for r in W['roads'] if 'Ha Yeung Road' in r['n'] or r['n'].startswith('下洋路')]
pts=sorted([p for r in hy for p in r['p']],key=lambda p:p[0])[::8]+[[-84,17,0]]
tv=0;tt=0
for p in pts:
  x,z=p[0],p[1];eye=g(x,z)[0]+2.2;vis=0;tot=0
  for hd in range(30,100,5):
    dx,dz=math.sin(math.radians(hd)),-math.cos(math.radians(hd));m=-1e9
    for d in range(5,1300,3):
      tx,tz=x+dx*d,z+dz*d
      if tx>X0+(nx-1)*C or tz<Z0:break
      t,c=g(tx,tz)
      if c==4:tot+=1;vis+=((0-eye)/d>=m);break
      m=max(m,(t-eye)/d)
  tv+=vis;tt+=tot;print(f'({x:.0f},{z:.0f}) h={g(x,z)[0]:.0f}: sea visible {vis}/{tot}')
print('TOTAL',tv,'/',tt,'home',g(*W['places']['door'])[0],'stop',g(*W['places']['stop'])[0])
