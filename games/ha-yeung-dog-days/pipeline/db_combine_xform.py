#!/usr/bin/env python3
# One Discovery Bay: south + Headland Drive / Parkridge + north in a single level (drops the separate DBN level and bus picker).
import sys, re
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'worldDataDBN' in src, 'already transformed'
world = open(sys.argv[1] if len(sys.argv) > 1 else G + 'data/discovery-bay/world.json', encoding='utf-8').read().strip()
assert '</script' not in world

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

# swap world JSON blocks
m = re.search(r'(<script type="application/json" id="worldDataDB">)(.*?)(</script>)', src, re.S)
src = src[:m.start(2)] + world + src[m.end(2):]
m = re.search(r'\s*<script type="application/json" id="worldDataDBN">.*?</script>', src, re.S)
src = src[:m.start()] + src[m.end():]

k = src.rfind('<script>'); head, c = src[:k], src[k:]
c = R(c, "const LEVELS={hy:'worldData',db:'worldDataDB',dbn:'worldDataDBN'};", "const LEVELS={hy:'worldData',db:'worldDataDB'};")
c = R(c, "DESTS={hy:['db'],db:['hy','dbn'],dbn:['db']}[WD.level]||['hy']", "DESTS={hy:['db'],db:['hy']}[WD.level]||['hy']")
# north plaza sign + map pin in the combined world
c = R(c, "if(SITE)wallSign(PIAZ.x,PIAZ.z+12,", "if(SITE)wallSign(35,-1352,'愉景北商場  DB NORTH PLAZA','#f6efdf','#2d6fa5',12,4.2);\n  if(SITE)wallSign(PIAZ.x,PIAZ.z+12,")
c = R(c, "if(DBX.vc)PLACES.push(['Village',DBX.vc[0],DBX.vc[1],'#e0a63a'])}", "if(DBX.vc)PLACES.push(['Village',DBX.vc[0],DBX.vc[1],'#e0a63a']);PLACES.push(['North Plaza',35,-1352,'#2d6fa5'],['Headland Drive',-200,-690,'#7a8f3a'])}")
c = R(c, "['north','Take the bus to Discovery Bay North']", "['north','Walk or drive to Discovery Bay North']")
c = R(c, "if(dbUpd)dbUpd(dt);", "if(dbUpd)dbUpd(dt);if(WD.level==='db'&&dog.z<-1100)complete('north');")
# storage can be blocked (private windows, previews): never read it unguarded
c = R(c, "if(!dead&&!SAMP&&!sessionStorage.__dogTip){try{sessionStorage.__dogTip=1}catch(e){}", "let seen=0;try{seen=sessionStorage.__dogTip;sessionStorage.__dogTip=1}catch(e){}if(!dead&&!SAMP&&!seen){")
# more ground to cover: scale tree count with map area
c = R(c, "const target=lowEnd?900:2200;", "const target=Math.round((lowEnd?900:2200)*Math.min(1.8,Math.max(1,(X1-X0)*(Z1-Z0)/800000)));")
open(sys.argv[2] if len(sys.argv) > 2 else G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok')
