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

## #4 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (game version 13, same link)
- **Discovery Bay look** (`dbPrep()` runs before buildings are indexed; `dbDecor()` adds the props): cross-shaped footprints become 16–23-floor cream towers (Overture had no heights; every building was ≤12 m). Villas under 400 m² (Beach Village, Headland) get pastel walls and hip roofs in terracotta or slate (`hipRoof()` built on an oriented bounding box). Village houses and the pier have their own facade textures. Walls now reach the ground after the terrain is reshaped.
- **Plaza:** the piazza at (10,-20) is levelled to 13 m with mosaic paving, a fountain and a ring of palms; the "愉景廣場 DB PLAZA" sign sits on the nearest facade. Only a 21 m disc is paved: the lawn between it and the mall is still grass (an unfinished tweak; see the plaza part of `pipeline/discovery_bay_look_xform.py`).
- **D'Deck** (`DECK` polyline, from the real shore path): a level promenade 1.7 m above the sea with mosaic paving, a stone balustrade, black-and-yellow bollards, café tables under red and black umbrellas, and a "BAY COFFEE" sign (fictional name).
- **Pier and ferry:** the pier footprint is raised onto a jetty and carries a blue "DISCOVERY BAY PIER" sign. A ferry docks for 45 s, leaves, stays away for 60 s and comes back, sounding its horn when you're near.
- **Tai Pak Beach** sand is golden; palms line the back of the beach.
- **Cove village** (south-east corner, flat ground west of the cove): 9 tiled three-storey village houses with balconies, laundry lines and roof tanks, a red shrine, a "往稔樹灣 To Nim Shue Wan" signpost, and a day-off get-together (folding table, stools, music). Five villagers chat, give pats and take gifts (they're in `people()`).
- **Golf carts:** top speed 16 m/s, turbo 22 m/s (Shift / Run / full joystick), movement in substeps so fast carts don't pass through walls, camera pulls back with speed, and the HUD shows km/h. Resident carts run at 8–10 m/s.
- **Police chase:** after 40–90 s of driving above 5 m/s, a patrol car with a blue-and-yellow check band and flashing lights spawns 50–95 m behind you on the main road. You get "逃げろ! POLICE!", a siren, loudspeaker lines ("Dog! Get out of the cart!") and a chase HUD with a 30 s countdown. Get 90 m away or last 30 s to escape (+500, to-do `police`). If it stays within 3.6 m for 0.7 s you're BUSTED: the dog is put out of the cart and patted. Hopping off ends the chase. 18 to-dos in total.
- Tests: `tests/run22.js` (DB styles, walking across the piazza, turbo, police spawn/busted/escaped, screenshots), run with a debug copy that boots into DB. Everything passed. Ha Yeung was only smoke-tested after the building refactor (loads, no errors); `run21.js` was not re-run on this build.

### Learned
- In the headless browser the DB scene runs at about 3 fps, so tests must wait for conditions (`waitForFunction`), never fixed sleeps.
- Overture places give good anchors for DB: plaza (0,0), D'Deck (14,-45), ferry pier (128,-97), Tai Pak Beach (-139,-256), bus terminus (113,17).

### Status / next
- The user said the game feels a bit boring and is thinking of stopping. If it continues, the ideas that came up were: make the arcade chases the core loop (graded daily heists and chases, combos, leaderboard), and multiplayer for friends via the artifact `room` capability (no game server to run; check costs and limits in the `artifact-capabilities` skill before promising anything).
- Open nits: pave the rest of the plaza; real-device performance check of DB (palms, towers, ferry) on the iPhone.

## #5 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (game version 14, same link, now published with `capabilities: {room: {}}`)
- **Light multiplayer** through the artifact `room` capability: presence only (no topics, no db, nothing stored). `ROOM` is resolved once outside levels (`claude.use('room')`; `null` means single-player as before). Each level sends `{lv,x,z,y,h,s,n,b}` about 10 times a second (`s` = stand/sit/lie/swim/cart, `b` = bark counter). Friends on the same level are drawn with `makeDog()` and a "🐾 name" bubble, simply animated, sitting in a cart when `s:'cart'`; barks show "Woof! Woof!" and play the sound nearby. Friends appear as yellow dots on the minimap, and a toast says when one joins. Code: `MP` / `mpUpd()` next to `dbDecor`. Edit script: `pipeline/multiplayer_xform.py`.
- Test: `tests/run23_multiplayer.js` fakes `window.claude.use('room')` with an inline script and plays a friend (shown, rides a cart, removed on leave). It passed with no errors. Not tested with two real people yet.

### Learned
- Who can join a room: signed-in members of the owner's organisation plus invited guests. Signed-out or public-link viewers can't connect (they still play solo). The user asked to drop the sign-in requirement; that's the platform's rule and can't be changed from the page.
- Presence limits: 4 KiB per participant, coalesced to about 30 Hz; emits and presence share about 40 msgs/s; about 256 peers.
- `page.addInitScript` doesn't apply to `setContent`; inject test shims as an inline `<script>` in the content.
- Existing quirk (not new): at the Ha Yeung start spot the camera can sit right against the yellow plaque on the red door, filling the lower screen with yellow until you move.

### Next
- Try it with two signed-in people. Possible later additions: shared scoreboard (db), chase each other, bark emotes on a topic.

## #6 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (game version 15; capabilities room + db + sample)
- **Player creations** ("✨ Create" button under the minimap, key N): the player types an idea, and one `sample.json` call on the **player's own Claude account** (`modelTier: 'quick'`, explicit action only, one per 90 s per player) returns an object spec: name, zh, label, line, move (none/bounce/float/spin), effect (none/giant/tiny/zoom/rain/party) and 2–14 primitive parts. `cleanSpec()` whitelists and clamps everything (shapes, #rrggbb colours, sizes ≤1.6 m); text goes into the page only via textContent. Each creation spawns as a carryable item (`ITYPES['gen_'+id]`, not stashable) and is saved to db `creations/{id}` `{lv,x,z,spec,by,t}`. Every view listens to the latest 200 (`onSnapshot`) and spawns up to 70 for its level, so the world grows from what players make. Prompt: `genPrompt()` (friendly, not weird, no brands or real people). New to-do `create` (19 total).
- No procedural/random generator (the user doesn't want one), and no automatic GitHub sync. The user may ask a session to "sync creations": read db `creations` with ArtifactData and commit them (e.g. `data/creations.json`).
- Test: `tests/run24_creations.js` (fake `sample` and `db`): N opens the box, a creation spawns and saves, another player's creation appears, invalid specs are ignored, and picking one up triggers its effect (giant dog). Passed, no errors. Not tried yet with real Claude accounts.

### User ideas parked (not started; the user wants to keep spending low)
- More dog breeds (e.g. a bichon frise as a playable choice), and GTA-style missions given by a Chinese auntie (a mission giver with chained objectives: deliveries, heists, escapes on a timer). Both are feasible on the current engine.

## #7 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (game version 16)
- **Open-ended creations:** the spec now allows `ride: "drive" | "fly"` (vehicle, front towards +x, `seat`, up to 4 m) and `talk` + `hello` (a character you can chat with, up to 3 m). More effects: fireworks, teleport, night, day (plus giant, tiny, zoom, rain, party). Vehicles go into `rides` (hop on with X). Drive uses `rideCart`; fly uses `rideFly()`: hold W to climb (needs more than 10 m/s), let go to glide, S to dive and land, A/D to steer, Shift for turbo; it bonks off buildings below roof height and you can hop off only on land. Characters go into `genFolk` and can be chatted with.
- **Chat** (context button "Chat", key X, within 3.6 m): Granny Chan, Auntie Wong (once a mission is running), Uncle Lam the fisherman, BBQ Uncle, Ming, the village helpers, and player-made characters. `sample.json` on the player's account returns `{reply, action: none|treat|pat}`; a treat (egg tart) at most every 2 min per person. Persona text is in `PERSONAS()`.
- **Auntie Wong's missions** ("Mission" next to her): Claude writes a 1–3 step mission from a whitelist: goto, deliver (stick/stone/shell/cone/branch), bark, sit, dig, steal (bbq/picnic), and in DB drive and police. `misClean()` drops anything that doesn't map to a real place or person. A timer runs 60–300 s, the reward is clamped to 100–800, there's a yellow target marker and minimap dot, a `#missionHud`, and banners ミッション開始! / ミッションクリア! / しっぱい…. Hooks: `misEv()` is called from finishLoot, endPolice(win), doBark, finishDig.
- **Bichon frise:** breed choice on the start card (`makeDog(breed)`: white, pom-pom head, short muzzle, tail up, `D.k` = 0.62 scale). `D` is now `let`; the breed travels in snapshots and multiplayer presence (`br`).
- **Playable by anyone:** everything works signed out; Claude features show a short note, plus one gentle tip after 15 s for signed-out players.
- New to-dos: chat, mission, fly (22 total).
- Tests: `tests/run25_rides_chat_missions.js` was written (fake Claude: bichon, chat, mission, plane) but **not run**: the user stopped the long run. Only a load smoke test was done (no errors). Run it next time.

### Ideas from the user (not built)
- Players setting up their own mini-games inside the world (e.g. a gambling booth / game stall they design). Feasible later as a creation kind with a small whitelisted rule set (e.g. a stall with a coin-flip / guess game paying good-dog points); not started.

## #8 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

- Publishing version 16 was blocked by the session's auto-mode safety check ("Create Unsafe Agents"). Likely cause: one player's creation text (a talking character's personality) was fed into other players' Claude requests (prompt-injection path).
- Fixes: (1) `genReview()`: a second quick-tier `sample.json` call on the creator's account reviews a creation's text (name, zh, label, line, hello, talk) and blocks harmful content or AI-instruction text before it's spawned or saved. (2) Chatting with player-made characters no longer sends their `talk` text; the prompt only gets the label, quoted as a name tag. The client-side review can be bypassed by a tampered client, so (2) is the real guard; review is a filter, not a security boundary.
- Only a load smoke test was run (no errors).

## #9 · 2026-10-14 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

### What changed (game version 17; capabilities room, sample, user, db)
- **Coins 🪙** (`S.coins`, start 100, +10 per to-do, +reward/5 per mission). Signed-in players' wallets are saved in db `data/users/<user.id()>/wallet` (`walletUpd()`, outer `W`, saved 2 s after a change); otherwise per session. Coins are game money only: they can't be bought or cashed out.
- **Game booths:** creation spec `booth: {game: coin|dice|cups|wheel, stake: 10-100}`. Context "Play" opens `#boothBox`; `crypto.getRandomValues` decides. Payouts: coin 50% × 1.9; dice 5–6 × 2.8; cups 1/3 × 2.8; wheel 0× (55%) / 1.5× (25%) / 2× (15%) / 5× (5%). When a player loses, half the stake goes to `creations/{id}.bank`; the owner (`owner` = creator's user id) collects it at their booth. The ledger is trust-based (a tampered client can cheat); fine for friends.
- **People:** spec `person: {shirt, pants, hair, skin, hat?}` builds a `makePerson` villager; `giver: {theme}` makes them hand out missions ("Mission" context).
- **Missions rewritten:** Auntie or any giver; 2–4 steps; new types race (own countdown), collect (n pickups), gift, swim, nap, ride (cart or player vehicle), fly (altitude, only if a flying creation exists). A giver's label goes into the prompt only as a quoted name tag.
- New to-do `booth` (23 total).
- Test `tests/run26_coins_booths_givers.js` (fake Claude/db/user) passed: wallet load, booth with owner, 5 plays, giver person, 2-step mission. Chat, flying, etc. from #7 are still not run end to end.

## #10 · 2026-10-15 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

- The user hit "Graphics paused" (WebGL context lost) on the MacBook Air after a long session in v17 (950 points, chat open). Fix: on `webglcontextlost` the level now rebuilds itself from `snapshot()` one quality step lower (`rebuildLevel()`, `S.recover`, "Graphics hiccup, restoring…" fade, then "Graphics restored" toast). The Reload card only appears after more than 3 losses in a minute or before the game has started. Script: `pipeline/context_recovery_xform.py`; test: `tests/run27_context_recovery.js` (forces loss with WEBGL_lose_context; passed).
- Root cause not pinned down. Suspects for GPU memory growth in long sessions: every creation part and every seeded stick gets its own geometry and material; dug holes are removed but not disposed; "rain" effect copies. Worth sharing geometries/materials if it keeps happening.

## #11 · 2026-10-15 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

- **Paraglider** (game version 19): flying above 4 m, the context button shows "Jump!" (X). `jumpOut()` drops the dog into `dog.para` free fall (A/D steer); X or Space opens a striped canopy (`makeCanopy`, `openChute`): about 2.6 m/s descent, glide 4–11 m/s, W faster, S drops quicker. Landing with the chute open and slow gives NICE LANDING (+100, to-do `para`, 24 total); without it, a cartoon BONK (happy −10); sea landings just splash. The empty plane glides down and parks (`dropUpd`, `k.drop`). Script `pipeline/paraglider_xform.py`, test `tests/run28_paraglider.js` (passed: create plane, Jump!, open with Space, land, plane parks).
- Discussed (not built): making money (personalised "your dog in your neighbourhood" games, local sponsors; no real-money coins) and all of Hong Kong (about $300–700 open world vs about $150–250 for 10–15 highlight places).

## #12 · 2026-10-15 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

- **Discovery Bay North** is a third level (game version 20), about 1.4 km north of DB Plaza. It's a separate level rather than a bigger DB map, to keep GPU memory down.
  - Build: Overture extracts reused from `data/discovery-bay/` (bbox already covered it), plus `water.json` (ov.py) and terrarium z15 tiles fetched in the sandbox (not committed). `IN=<dir> CENTER=22.30765,114.01504 BOX=-600,450,-420,330 MAINROAD="Discovery Bay Road" JUNCROAD="Siena Avenue" CW=14 CS=6 CG=4 RAMP=60 python3 pipeline/build_data.py`, then `IN=<dir> python3 pipeline/places_dbn.py`. The bus route (`cwb`) is the shortest path over w≥7 roads from the west (tunnel) edge to North Plaza, because no single named road covers it. Output: `data/discovery-bay-north/world.json` (1.4 MB), embedded as `#worldDataDBN`.
  - Game: `LEVELS.dbn`; `WD.dbish` (db or dbn) turns on golf carts, resident carts, police, no taxi/minibus, styled towers/villas, palms by the beach. DB-only set pieces (piazza, D'Deck, pier/ferry, cove village) are gated by `SITE` inside dbPrep/dbDecor. DBN gets a "愉景北商場 DB NORTH PLAZA" sign and a fictional "NORTH BAY COFFEE" café for Auntie. Buses: `DESTS` (hy→db, db→hy|dbn, dbn→db); from DB, "Board bus" opens a `#busBox` picker. New to-do `north` (25 total).
  - Test `tests/run29_db_north.js` (DB → picker → DBN → back) passed with no errors. The page is now about 4.5 MB.
- Ideas discussed, not built: open-ended player features (AI review is not a security boundary; suggested a sandboxed-iframe experiment or a whitelisted power-up kit).

## 13. One Discovery Bay (south + Headland Drive / Parkridge + north), game version 21
- The user asked to drop the second DB bus stop and join both halves, filling the gap in the middle (Headland Drive and Parkridge). The DBN level is gone; `data/discovery-bay/world.json` now covers the whole of DB in one map (box x -760..530, z -1720..270, same origin as before, so the piazza/D'Deck/pier/village coordinates are unchanged). 657 buildings, 385 roads, 2.6 MB.
  - Build: Overture extracts for the combined bbox plus terrarium z15 tiles (not committed). `IN=<dir> CENTER=22.29589,114.0165 BOX=-760,530,-1720,270 MAINROAD="Discovery Bay Road" JUNCROAD="Plaza Lane" CW=14 CS=6 CG=4 RAMP=60 python3 pipeline/build_data.py`, then `IN=<dir> python3 pipeline/places_db.py` (now takes `IN`). The bus terminus is still DB Plaza.
  - Game (`pipeline/db_combine_xform.py`): removed `#worldDataDBN` and `LEVELS.dbn`; DB's bus goes straight to Ha Yeung (no picker). "愉景北商場 DB NORTH PLAZA" sign at (35,-1352); map pins for North Plaza and Headland Drive. The `north` to-do is now "Walk or drive to Discovery Bay North" and completes when z < -1100. Tree count scales with map area (up to 1.8x). Old hot snapshots saved in `dbn` fall back to Ha Yeung. Leftover `dbn` branches in welcome toasts are dead code.
  - Fixed: the sign-in tip read `sessionStorage` outside try/catch, which threw where storage is blocked.
  - `data/discovery-bay-north/` is deleted (still in git history); `pipeline/places_dbn.py` stays but is unused.
  - Brief test `tests/run30_db_combined.js`: one DB level loads, north to-do fires, bus goes to HY. Screenshots looked right (Headland Drive towers, North Plaza by the water). The page is about 4.2 MB.

## 14. Discovery Bay Marina, game version 22
- Widened the DB map east/south to include the Marina Club basin: `BOX=-760,1160,-1720,540` (same CENTER/origin and other env as #13; Overture extracts and big.npy already covered it). 829 buildings, world.json 3.5 MB; bus terminus unchanged.
- `pipeline/marina_xform.py`: re-embeds the world, and in dbDecor (SITE) scans the basin (x 745..1140, z 125..520, water deeper than 1.2 m) for up to 70 moored yachts on pontoon fingers, with walkways clipped to each row of boats; the yachts bob while the dog is within ~320 m. Map pin "Marina" at (950,320).
- Brief test `tests/run31_marina.js`: DB loads, 70 yachts, bus to HY works, no errors; screenshots checked.
- Discussed, not built: back-mounted bomb launcher for buddy matches (plan in chat: a launch is one shared event; each player's own game decides its hits).

## 15. No sign-in needed to play; creations baked in (game version 24)
- Removed the 15 s "sign in to Claude" tip toast. Sign-in is now only mentioned when a player tries to create, chat or ask for a mission.
- `pipeline/seed_creations_xform.py <dir>` bakes the creations made so far (32, read with ArtifactData `list` of `creations`, owner ids stripped; the one from the old DBN level shifted by (-150,-1300) into the combined DB map) into `#genSeed` and `data/creations_seed.json`. `genListen` spawns the seed once, then the live db snapshot adds anything new (ids dedupe). So signed-out players see and use every creation (rides, flyers, booths, mission givers).
- Also published a second, capability-free copy (no db/sample/room/user, so claude.ai has nothing to ask a signed-out viewer to sign in for) as the "play" link; the create box there points to the main link for creating. Re-run the seed transform before republishing to pick up newer creations.

## #16 · 2026-10-24 · https://claude.ai/code/session_01KRGTnyo7iveA8i8hYTcjm4

- Correction to #13–#15: their headers didn't follow the `## #N · date · link` format; same session as this one.
- **Request:** border terrier mode with a pink lead, friends for the terrier, a typical Lantau street dog, and "live the life of a dog" features. A design panel produced 5 units (specs were in the session scratchpad; summary below). The user capped spend at about $20 more partway, so units 2–5 were merged into one slim build and independent verification was dropped.
- **Unit 1, breeds** (`pipeline/breeds_xform.py`, test `tests/run32_breeds.js`, 62 checks pass): playable **border terrier** (grizzle-and-tan, otter face, beard, folded ears, hot-pink collar, "Yap! Yap!", digs faster, smells treasure further, catches the cat quicker) and **Lantau street dog 唐狗** (fawn, black mask, prick ears with an ear-tip nick, curled tail, deep "Wuff!", swims faster, hungry slower). `BREEDS`/`BREED_IDS`/`breedInfo()`; `makeDog(breed,{lite,mc,c,collar})` builds cheap shared-material NPC rigs; `D.leashPt` on the neck. Breed-aware lines (pats, BBQ, picnic, chat/create prompts) and multiplayer friends render their breed. Golden/bichon meshes unchanged (54/56).
- **Slim build** (`pipeline/doglife_slim_xform.py`, test `tests/run37_doglife_slim.js`, 29 checks pass):
  - **Pink lead walkies** with Jie Jie Rose (family helper, `ROSE`, `WALK`, `LEASH` = 10 shared pink cylinder segments with sag). Terrier starts on the lead; L / Lead button toggles (lantau: free dog). Speed capped at 6.5 on the lead, Rose gets dragged (グイグイ! TUG!), treats for sitting by her, auto-unclip for swim/cart/para and re-clip after a swim. To-do `walkies` (200 m).
  - `pipeline/rose_side_xform.py`: Rose walks to the dog's side (also eases sideways while dragged) so she doesn't block the camera.
  - **Zoomies** (Z / Zoom; terrier after swims): loops with LOOP ×n, then flops down.
  - **NPC dog engine** (`npcDogs`, `mkNpcDog`, `poseDog2`, `npcMove`, `greetStep`, `followStep`, `updateNpcDogs`). **Friends** Biscuit (blue-and-tan terrier), Mochi 麻糬 (bichon), Bobo 波波 (golden) in both levels: nose-to-tail sniff hello → ともだち! NEW FRIEND!, up to 2 follow (`S.pack`, `S.pals`, carried over bus rides), mirror sit/lie, bark back, go home 22:00–07:00. Terrier start: Biscuit runs up in the first minute. To-do `friend`.
  - **Street dogs** Wong Choi 旺財, Siu Hak 小黑, Fa Fa 花花 in the DB cove village and Lucky 幸運 by the Ha Yeung store: shy of running dogs, trust grows while you're slow/sitting nearby (pink marker), then they greet and escort you within ~70 m of home. Lantau-breed players start at trust 0.6. To-do `streetdog`. 28 to-dos in total.
  - **Nose cam** (V / 👃): dog-height first person; second press adds a dog-colours filter.
- **Not built (designed, specs summarised in the unit descriptions above):** slip-the-lead chase, road-wait treats, tag with friends, nap dreams, pack dinner bowl, siren howl-along chorus, pee-mail posts, rolling in seaweed/stink + sea wash, drinking (water bowl/fountain/salty sea), pigeons, feral cattle.
- **Learned:** `tests/mkdebug.py` + `tests/smoke.js` are the reusable harness (any level/breed via `window.__BOOT`, prepended because the page has no `<head>`). Rose is in `people()`, so she also gives pats. Untested: pack carry-over on the bus, escort stopping 150 m from home.
