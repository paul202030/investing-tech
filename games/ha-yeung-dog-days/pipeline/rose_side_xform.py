#!/usr/bin/env python3
# Rose walks beside the dog (to its side, a little behind) instead of straight behind it, so she doesn't block the camera.
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'ROSE_SIDE' not in src, 'already transformed'
old = "else if(d>1.8){if(!dog.sniff){const st=Math.min(1.5*dt,d-1.8);rp.x+=(dog.x-ox)/d*st;rp.z+=(dog.z-oz)/d*st}"
new = ("else if(!dog.sniff&&d>1.2){/*ROSE_SIDE*/const fh=Math.sin(dog.heading),ch=Math.cos(dog.heading),sd=WALK.side||(WALK.side=1),"
       "tx=dog.x+ch*1.7*sd-fh*0.6,tz=dog.z-fh*1.7*sd-ch*0.6,td=Math.hypot(tx-ox,tz-oz);"
       "if(td>0.25){const st=Math.min((td>3?2.6:1.5)*dt,td);rp.x+=(tx-ox)/td*st;rp.z+=(tz-oz)/td*st}}"
       "else if(d>1.8){if(!dog.sniff){const st=Math.min(1.5*dt,d-1.8);rp.x+=(dog.x-ox)/d*st;rp.z+=(dog.z-oz)/d*st}")
assert src.count(old) == 1
src = src.replace(old, new)
# while dragged, ease her round to the side too (stays on the lead circle), so she isn't straight behind the dog
old2 = "if(d>Lmax){dragged=true;const k=Lmax/d;rp.x=dog.x-(dog.x-ox)*k;rp.z=dog.z-(dog.z-oz)*k}"
new2 = ("if(d>Lmax){dragged=true;const k=Lmax/d;rp.x=dog.x-(dog.x-ox)*k;rp.z=dog.z-(dog.z-oz)*k;"
        "{const fh=Math.sin(dog.heading),ch=Math.cos(dog.heading),sd=WALK.side||(WALK.side=1),vx=ch*sd-fh*0.6,vz=-fh*sd-ch*0.6,vl=Math.hypot(vx,vz),"
        "sx=dog.x+vx/vl*Lmax*0.95,sz=dog.z+vz/vl*Lmax*0.95,w=Math.min(1,dt*1.5);rp.x+=(sx-rp.x)*w;rp.z+=(sz-rp.z)*w}}")
assert src.count(old2) == 1
src = src.replace(old2, new2)
open(G + 'index.html', 'w', encoding='utf-8').write(src)
print('ok')
