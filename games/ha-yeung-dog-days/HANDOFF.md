# Ha Yeung Dog Days: handoff log

**Rules for this file (append-only):**
- Read every entry before starting work. Newest entry is at the bottom.
- Never edit or delete an earlier entry. If something in an old entry is now wrong, say so in a new entry ("Correction to #1: ...").
- Before a session ends (or before handing off), append a new entry: `## #N · YYYY-MM-DD · <session link>` with what changed, what was learned, and what's next.
- Keep entries factual and short enough to scan; link files instead of pasting code.

---

## #1 · 2026-10-14 · https://claude.ai/code/session_01DJtiMEA9gjnoS7fY1wfeK7

### Where things are
- **Live game:** https://claude.ai/artifact/42qyenq1UL2K1fZ1d8b4KC (shared: anyone with the link). Latest published version = `index.html` in this folder.
- **Flyers:** https://claude.ai/artifact/Uz9THZYrwCVcWDPL2u7qCa (Design canvas, private; artboards `Main.dc.html` arcade poster, `Ad.dc.html` cute 4:5 ad). Copies in `flyer/project/`.
- To republish the game from a new session: Artifact tool, `url` = the game link above, `file_path` = this `index.html` (read the artifact first if the tool asks). Keep the URL; don't create a new artifact.
- The session scratchpad is not persistent. This folder is the source of truth now.

### What the game is
Single self-contained page `index.html` (~1.5 MB):
1. `<title>`, fonts link, one `<style>` (HUD, start card, arcade overlays), HUD markup.
2. `<script type="application/json" id="worldData">`: the Ha Yeung world (same as `data/ha-yeung/world.json`).
3. three.js **r128** from cdnjs (UMD, global `THREE`).
4. One IIFE with the whole game. Section banners (`// ===== ... =====`) in order: Real-world data · Renderer · Terrain · Sea · Buildings · Roads · Clear Water Bay Road vehicle path · Places · Vegetation · Characters · Things to retrieve · Dim sum feast · BBQ · Picnic · Wholesome stuff · State/HUD · Big map · Audio · Input · Actions · Simulation · Camera · Main loop · Boot.

Key names: `WD` world JSON, `PL` = `WD.places`; `gridH(x,z)` terrain height (3 m grid, bilinear); `groundAt(x,z)` = what feet stand on (uses `ROADY` raster on the main road, +0.08 on lanes); `CLS` land class per cell (0 grass, 1 forest, 2 developed, 3 beach, 4 sea, 5 shore rock); `RMASK` road raster; `BL` buildings + `bldAt`/`pushOutB` (spatial hash); `softColliders` circles; `CW`/`cwAt(s)` main-road polyline for vehicles (s runs north to south; vehicles keep left); `S` game state; `dog` sim state, `D` dog model; `cam`.

Coordinates: metres, x east, z **south** (north is -z), origin = map centre. y up.

Features (all live): real terrain/roads/495 buildings; golden retriever (walk, 7x run with no tiredness, sniff, dig, sit/lie/nap, swim/shake, bark); fetch with Ming; sticks/stones/cones/shells to carry to the bed stash or to Ming; Auntie Wong / fisherman serve a dim sum feast after a held sit; BBQ tomahawk heist and beach-picnic snack heist (auto-dash, arcade にげろ!/RUN!, chase meter, visible take-back, leftover bone); Granny Chan's slipper quest; pats and belly rubs; gifts; butterflies; sunset; bus, taxi, green minibus (sit at stop to hail); map tap-to-travel; daylight 05:30-21:30 with fast nights; 15 daily to-dos; adaptive quality.

### How the world data is built (`pipeline/`, see README)
- Elevation: AWS Terrain Tiles (terrarium z15). It is a **surface** model, so `build_data.py` lowers wooded land (canopy correction `CW=14`, scrub `CS=6`, wild grass `CG=4`) and ramps the last `RAMP=60` m to the sea. Without this the sea is hidden from Ha Yeung Road.
- Roads: centre heights smoothed (window 15 for main roads), terrain flattened under them with a wide soft blend.
- Houses: each footprint gets a levelled platform; building base = platform height.
- Overture data: `ov.py` reads the public S3 parquet with HTTP range requests (DuckDB extensions are blocked in the cloud sandbox).

### Gotchas learned the hard way
1. **Load order.** Everything is `const` in one IIFE. Init code that touches a `const` declared further down (e.g. `S`, `softColliders`) throws "Cannot access before initialization" and the whole game fails to load. Always run the headless smoke test after edits.
2. **One error must never freeze the game.** The frame loop calls `requestAnimationFrame` first and wraps `step()` in try/catch. (Original freeze: a NaN reached a Web Audio param when a vehicle spawned before being placed.)
3. **Vehicles:** call `placeVehicle` the moment one spawns.
4. **Roads:** main roads (`w >= 7`) get kerbs, pavements, railings and write `ROADY`; segments not on the main chain (junction slip road) are drawn as plain asphalt only (`CWSET` check). Lanes and footpaths are draped on the terrain (no skirts), or you get floating stepped slabs.
5. **three r128:** `InstancedMesh` culls by the base geometry's sphere, so set `frustumCulled = false` on instanced trees and rocks.
6. **Performance:** phones and some MacBook Airs drop to lighter modes automatically (`lowerQuality`); shadows update every other frame; tree count is lower on `lowEnd`.
7. **Editing method used so far:** small Python scripts that `str.replace` exact snippets with an assert that each snippet occurs exactly once, then `node --check` on the extracted script, then the headless test. Fast and safe for a 1.5 MB file.
8. **Headless testing** (`tests/`): Playwright with Chromium at `/opt/pw-browsers/chromium` and `--use-gl=swiftshader`. cdnjs is blocked inside the sandbox, so install `three@0.128.0` from npm into `tests/lib/` and serve it by intercepting the `three.min.js` request (see `tests/run*.js`). The scripts expect a `perf3.html` copy of the game with a debug hook (`window.__g = {...}` set inside `updateDog`) to move the dog and read state. SwiftShader runs at about 25% speed (dt is capped), so timings stretch, and CSS animations don't show in screenshots mid-animation.
9. **Sandbox network:** HK government data portals (LandsD/CSDI) are blocked; AWS S3 (terrain tiles, Overture) works; Google Fonts and cdnjs don't load in tests (fine for players).

### The user (Paul)
- New to game dev; plays on a MacBook Air (Chrome) and an iPhone 15; sends screenshots of bugs.
- Cost-aware: give price estimates before big work; prefers splitting work into smaller releases.
- Likes Hong Kong authenticity, cute and arcade (Japanese) style, wholesome and non-violent naughtiness (golden retriever stealing food), big visible feedback.
- Wants this handoff log maintained append-only every session.

### Next (agreed, not started)
**Discovery Bay, part 1** (estimate about $10-14 of usage in a fresh session):
1. Two-level engine: wrap game init so the scene can be torn down and rebuilt for another world, carrying over name/points/stash/to-dos. Use an AbortController for all listeners, cancel the RAF loop, dispose the renderer.
2. Level variants via world flags (`WD.level`, `name`, `nameZh`, `busDest`, `signText`, `roadName`, `places.noHome`): no taxi or green minibus in Discovery Bay, no red home door, renamed labels and intro toasts.
3. Bus boarding: context button while the bus dwells at the stop, short fade ("Taking the bus to Discovery Bay…"), arrive at the terminus; same back. No big animation (user's request).
4. Golf carts: parked at `WD.places.carts` ([x, z, heading]); walk up, "Hop on", the dog sits at the wheel, W/S throttle, A/D steer, joystick on phone; collide with buildings, stop at water; hop off. AI carts replace taxis on Discovery Bay Road.

**Part 2:** street dogs (friendly 唐狗 village dogs) near the helpers' picnic spot in both places; Discovery Bay café/picnic life.

`data/discovery-bay/world.json` is already built (centre DB Plaza 22.29589, 114.0165; main road "Discovery Bay Road"; stop at the internal bus terminus; 6 golf cart spots; Tai Pak Beach; fisherman near the ferry pier).

**Ideas backlog:** saved progress; treasure Dog-dex with rares; graded daily heists and combos; photo postcards; shared leaderboard; multiplayer packs/territories via the `room` + `db` artifact capabilities (feasible for friend groups; there is no authoritative server).

## #2 · 2026-10-14 · https://claude.ai/code/session_01DJtiMEA9gjnoS7fY1wfeK7

- Picnic loot enlarged so it reads in the dog's mouth: `ITYPES.chicken` is now a big drumstick (meat ~0.3 m with visible bone), `ITYPES.lumpia` a bundle of three 0.38 m rolls. Tested headless (no errors), published as game version 11.
- Publishing now goes from this repo file: Artifact tool with `url` = the game link and `file_path` = `games/ha-yeung-dog-days/index.html`.
- Coordination: the user may run a separate Discovery Bay session. Before editing `index.html`, `git pull` this branch; before publishing, make sure the live game isn't newer than your copy (the Artifact tool refuses stale publishes, so merge rather than force).

## #3 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (Discovery Bay part 1, live as game version 12, same link)
- **Two-level engine.** The old game IIFE body is now `runLevel(LEVEL, BOOT, ARRIVE, AC)` and returns `{snapshot, destroy}`. `buildLevel()` patches `EventTarget.prototype.addEventListener` while a level builds so every listener gets the level's AbortController signal; `destroy()` aborts them, cancels the RAF loop (`rafId`, `dead`), disposes geometries, materials, textures and the renderer, removes the canvas and clears bubbles/pops/toasts. `switchLevel(id, snapshot)` destroys the old level, then builds the new one 40 ms later. The audio (`sfx`) now lives outside levels, so there's one AudioContext.
- **Carried state** goes through `snapshot()`: name, points, day/time, stats, to-dos and counters, treasures, hints, run lock, graphics quality. The stash is now `S.stash` (a list of item types); each level rebuilds it around its own bed via `stashPlace()`. Hot reload also restores the level (`snapshot.level`).
- **Discovery Bay level:** `<script type="application/json" id="worldDataDB">` holds `data/discovery-bay/world.json`. Level text comes from world flags (`name`, `nameZh`, `otherDest`, `signText`, `roadName`); Ha Yeung's defaults live in `LVDEF.hy`. In DB: taxi and green minibus never spawn (`wait=Infinity`), there's no red door (`places.noHome`; the bed is a "Rest spot"), the café sign is 愉景茶餐廳 DB CAFÉ, and the stop sign and toasts are renamed.
- **Bus travel:** the bus now dwells 12 s. A green context button (`#aCtx`, key X) offers **Board bus** within 10 m of the stop while it dwells. A fade overlay (`#fade`) shows "Taking the bus to …"; you arrive about 6 m past the other stop's shelter, with the bus parked beside you. The bus headsign shows where boarding takes you (`otherDest`).
- **Golf carts:** six parked carts at `places.carts`. **Hop on** within 2.8 m (X or the button). The dog sits at the wheel, steered with WASD/arrows or the joystick (up = drive, down = brake/reverse, sideways = steer); max 6.5 m/s forward, 2.5 m/s reverse. The cart bumps off buildings (two `pushOutB` circles, bounces back), stops at the water's edge and on very steep ground, and pushes off soft colliders and other carts. **Hop off** when below 1.2 m/s. Three resident carts with drivers use the vehicle system on Discovery Bay Road instead of taxis (they beep, don't nag).
- Two new to-dos (17 total): `bus` (ride between the villages, done on arrival) and `cart` (drive 60 m).
- `tests/run21.js` covers all of it. `pipeline/discovery_bay_part1_xform.py` is the edit script used (record only; it refuses to run twice).

### Learned
- The live artifact = `index.html` plus about 550 bytes of wrapper (doctype/meta/style before `<title>`, `</body></html>` after). To check whether live is newer, compare from `<title>` onward.
- SwiftShader runs game time at about ¼ speed, so drive/walk tests need long waits or a pre-set state (the test sets `cart.dist=50` to check the cart to-do).
- The debug hook used for tests (not shipped) is inserted at the start of `updateDog`: `window.__g={dog,cwAt,cam,S,bus,taxi,mini,carts,aiCarts,PL,WD,keys,ctxAction,placeVehicle,items,BL,bldAt,gridH,LEVEL};`. Run with `TLIB=<dir with three@0.128.0 + playwright> PERF=<perf copy> OUT=<shots dir> node tests/run21.js`.
- The page is now about 3.0 MB (two worlds). Only the active world is parsed and built.

### Next
- Not tested on a real iPhone: check joystick driving feel, the 150 px green button, and memory after several bus trips (each trip disposes the old renderer).
- **Part 2** (unchanged): friendly 唐狗 village dogs near the picnic spots in both places; Discovery Bay café/picnic life. DB currently reuses Ha Yeung's cast (Auntie at the café, BBQ uncle, Granny Chan, Ming, fisherman).
