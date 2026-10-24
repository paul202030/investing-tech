#!/usr/bin/env python3
"""Make a debug copy of index.html for headless tests.

  python3 tests/mkdebug.py OUT.html [extra names...]

- Exposes game internals as window.__g (refreshed every frame at the start of updateDog). Each name is
  read inside its own try/catch, so a name that does not exist in this build is simply skipped.
- Boots with window.__BOOT (inject <script>window.__BOOT={level:'db',breed:'terrier'}</script> before the
  page's scripts) instead of the hot-reload data, so a test can start in either level.
"""
import sys
G = __file__.rsplit('/tests/', 1)[0] + '/'
src = open(G + 'index.html', encoding='utf-8').read()
names = ['dog', 'D', 'S', 'cam', 'bus', 'PL', 'WD', 'LEVEL', 'placeVehicle', 'ctxAction', 'aiCarts', 'police', 'carts', 'BL',
         'DBX', 'GEN', 'genFolk', 'rides', 'keys', 'items', 'people', 'villagers', 'cat', 'MP', 'gridH', 'groundAt', 'bldAt',
         'complete', 'TODOS', 'makeDog', 'scene', 'toast', 'say', 'snapshot'] + sys.argv[2:]
hook = 'window.__g=window.__g||{};' + ''.join('try{__g.%s=%s}catch(e){}' % (n, n) for n in dict.fromkeys(names))
a = 'function updateDog(dt){'
assert src.count(a) == 1
src = src.replace(a, a + hook, 1)
b = 'else first((H0&&H0.data)||{})'
assert src.count(b) == 1
src = src.replace(b, 'else first(window.__BOOT||(H0&&H0.data)||{})', 1)
open(sys.argv[1], 'w', encoding='utf-8').write(src)
print('debug copy ->', sys.argv[1])
