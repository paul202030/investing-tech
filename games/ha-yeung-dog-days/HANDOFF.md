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
