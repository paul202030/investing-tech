#!/usr/bin/env python3
# Recover from WebGL context loss by rebuilding the current level from a snapshot (lighter quality).
import sys
G='/home/user/investing-tech/games/ha-yeung-dog-days/'
s=open(G+'index.html',encoding='utf-8').read();assert 'rebuildLevel' not in s
def R(o,n):
    global s;assert s.count(o)==1,o[:100];s=s.replace(o,n)
R("function switchLevel(id,carry){","const RECOV={times:[]};\nfunction rebuildLevel(id,data){const old=LV;LV=null;if(old)try{old.destroy()}catch(e){}setTimeout(()=>{try{LV=buildLevel(id,data,false)}catch(e){console.error(e);fade(false);const el=$('#lostMsg');if(el)el.hidden=false}},80)}\nfunction switchLevel(id,carry){")
R("renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;const el=$('#lostMsg');if(el)el.hidden=false})",
  "renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();if(lost||dead)return;lost=true;const now=Date.now();RECOV.times=RECOV.times.filter(t=>now-t<60000);RECOV.times.push(now);\n"
  "  if(RECOV.times.length>3||!S.started){const el=$('#lostMsg');if(el)el.hidden=false;return}\n"
  "  fade(true,'Graphics hiccup, restoring…');setTimeout(()=>{if(dead)return;const sn=snapshot();sn.quality=Math.max(0,quality-1);sn.recover=true;rebuildLevel(LEVEL,sn)},300)})")
R("  if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name","  if(S.recover){toast('Graphics restored in a lighter mode. Carry on!');return}\n  if(WD.level==='db'){toast('Welcome to Discovery Bay, '+S.name")
R("if(data.started)start()}","if(data.started){S.recover=!!data.recover;start();if(data.recover)setTimeout(()=>fade(false),250)}}")
open(sys.argv[1] if len(sys.argv)>1 else G+'index.html','w',encoding='utf-8').write(s);print('ok')
