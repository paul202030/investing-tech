#!/usr/bin/env python3
# Bake the player creations made so far into the page, so everyone sees and uses them without signing in.
# Usage: seed_creations_xform.py <dir of creations/*.json from ArtifactData list>
import sys, json, glob, re
G = '/home/user/investing-tech/games/ha-yeung-dog-days/'
src = open(G + 'index.html', encoding='utf-8').read()
assert 'genSeed' not in src, 'already transformed'
seed = {}
for f in sorted(glob.glob(sys.argv[1] + '/*.json')):
    d = json.load(open(f)); x, z, lv = d['x'], d['z'], d['lv']
    if lv == 'dbn': lv, x, z = 'db', x - 150, z - 1300   # the old North level now lives inside the one DB map
    seed[f.split('/')[-1][:-5]] = {'by': d.get('by') or 'someone', 'lv': lv, 'x': round(x, 1), 'z': round(z, 1), 't': d.get('t', 0), 'spec': d['spec']}  # no owner ids
txt = json.dumps(seed, ensure_ascii=False, separators=(',', ':'))
assert '</' not in txt
json.dump(seed, open(G + 'data/creations_seed.json', 'w'), ensure_ascii=False, indent=1)

def R(s, old, new, n=1):
    cnt = s.count(old)
    assert cnt == n, (cnt, old[:140])
    return s.replace(old, new)

k = src.rfind('<script>'); head, c = src[:k], src[k:]
head = head + '<script type="application/json" id="genSeed">' + txt + '</script>\n'
c = R(c, "function genListen(){if(GEN.unsub||!DBCAP)return;",
      "function genListen(){if(!GEN.seeded){GEN.seeded=true;try{const sd=JSON.parse(document.getElementById('genSeed').textContent);for(const id in sd)genSpawn(id,sd[id])}catch(e){}}if(GEN.unsub||!DBCAP)return;")
URL = 'https://claude.ai/artifact/42qyenq1UL2K1fZ1d8b4KC'
c = c.replace("'Creating needs Claude: open the game signed in to claude.ai. You can still find what other players made.'", "'Creating needs a Claude sign-in: open "+URL+" while signed in to claude.ai. Everything other players made is already in the world.'")
c = R(c, "cMsg.textContent='Creating needs Claude: open the game signed in to claude.ai.';", "cMsg.textContent='Creating needs a Claude sign-in: open "+URL+" while signed in to claude.ai.';")
open(G + 'index.html', 'w', encoding='utf-8').write(head + c)
print('ok', len(seed))
