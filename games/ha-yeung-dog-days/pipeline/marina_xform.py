#!/usr/bin/env python3
# Discovery Bay Marina: wider DB map (x to 1160, z to 540) plus pontoons and moored yachts in the marina basin.
import sys, re
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'MARINA' not in src, 'already transformed'
world = open(G + 'data/discovery-bay/world.json', encoding='utf-8').read().strip()
assert '</script' not in world
m = re.search(r'(<script type="application/json" id="worldDataDB">)(.*?)(</script>)', src, re.S)
src = src[:m.start(2)] + world + src[m.end(2):]

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

k = src.rfind('<script>'); head, c = src[:k], src[k:]
MAR = r'''if(SITE)wallSign(35,-1352,'愉景北商場  DB NORTH PLAZA','#f6efdf','#2d6fa5',12,4.2);
  // MARINA: Discovery Bay Marina Club basin (Overture marina landuse), pontoon fingers with moored yachts that bob
  if(SITE){const deckM=mat(0xb59a72),hullM=[mat(0xf7f7f2),mat(0xeef1f4),mat(0x1f3550)],cabM=mat(0xdfe6ea),glass=mat(0x2c3e50),boats=[];
    const wet=(x,z)=>gridH(x,z)<-1.2&&x<X1-6&&z<Z1-6;
    for(let z=125;z<=520;z+=16)for(let x=745;x<=1140;x+=7){if(boats.length>=70)break;
      if(!(wet(x,z)&&wet(x,z-6)&&wet(x,z+6)&&wet(x+3,z)&&wet(x-3,z)))continue;if(((x*7+z*3)|0)%5===0)continue;
      box(deckM,1.2,0.25,13,x+3.3,0.35,z,scene);
      const g=new THREE.Group(),L=8+((x+z)%5),hm=hullM[((x*3+z)|0)%3];g.position.set(x,0,z);scene.add(g);
      box(hm,2.6,1.1,L,0,0.35,0,g);box(hm,1.8,0.9,1.4,0,0.35,-L/2-0.4,g);box(cabM,1.9,1.0,L*0.42,0,1.35,0.6,g);box(glass,1.95,0.4,L*0.3,0,1.45,0.2,g);
      if((x+z)%3<1)cyl(cabM,0.06,0.08,9,0,5,-0.5,g,5);boats.push({g,ph:(x*0.37+z*0.11)});x+=4}
    for(let z=125;z<=520;z+=16){const row=boats.filter(o=>Math.abs(o.g.position.z-z)<1).map(o=>o.g.position.x);if(row.length<2)continue;const a=Math.min(...row)-1,b=Math.max(...row)+5;box(deckM,b-a,0.25,1.6,(a+b)/2,0.35,z+7.3,scene)}
    if(boats.length)ups.push(dt=>{if(Math.hypot(dog.x-950,dog.z-320)>320)return;for(const o of boats){o.g.position.y=Math.sin(S.t*1.3+o.ph)*0.12;o.g.rotation.z=Math.sin(S.t*0.9+o.ph)*0.03}});X.marina=boats.length}'''
c = R(c, "if(SITE)wallSign(35,-1352,'愉景北商場  DB NORTH PLAZA','#f6efdf','#2d6fa5',12,4.2);", MAR)
c = R(c, "PLACES.push(['North Plaza',35,-1352,'#2d6fa5']", "PLACES.push(['Marina',950,320,'#1d6fa5'],['North Plaza',35,-1352,'#2d6fa5']")
open(sys.argv[1] if len(sys.argv) > 1 else G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok')
