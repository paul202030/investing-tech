# Ha Yeung Dog Days

A browser game where you live a day as a golden retriever in Ha Yeung village (Clear Water Bay, Hong Kong), built on real terrain, roads and buildings.

- **Play:** https://claude.ai/artifact/42qyenq1UL2K1fZ1d8b4KC
- **Flyers:** https://claude.ai/artifact/Uz9THZYrwCVcWDPL2u7qCa (`flyer/project/` holds the artboards)

## What's here

| Path | What it is |
|---|---|
| `index.html` | The whole game: one self-contained page (three.js r128 from cdnjs + the Ha Yeung world data embedded). Open it in a browser. |
| `data/ha-yeung/world.json` | Processed world for Ha Yeung: 3 m height grid, land classes, roads, 495 buildings, game places. |
| `data/discovery-bay/world.json` | Processed world for Discovery Bay, embedded in `index.html` as the second level (`#worldDataDB`); reach it by bus. |
| `data/*/overture-*.json` | Raw Overture Maps extracts (roads, buildings, land, land use) for each area. Water polygons and elevation tiles are left out (large, re-fetchable). |
| `pipeline/ov.py` | Pulls Overture Maps data for a bounding box straight from the public S3 bucket (HTTP range reads, no DuckDB extensions needed). |
| `pipeline/build_data.py` | Builds a world: samples elevation tiles, canopy/coast corrections, flattens roads, levels house platforms, writes `world_base.json`. |
| `pipeline/places.py` / `places_db.py` | Picks game locations (home, bus stop, store, beach, fisherman, dig spots, golf cart parking) for Ha Yeung / Discovery Bay. |
| `pipeline/los.py` | Line-of-sight check (can you see the sea from Ha Yeung Road?). |
| `tests/run*.js` | Playwright scripts used to smoke-test the game headlessly (`run21.js`: bus between levels, carried state, golf carts). |
| `pipeline/discovery_bay_part1_xform.py` | One-shot record of the edit script that added the two-level engine, bus travel and golf carts (asserts it hasn't run already). |

## Rebuilding a world

```bash
# 1. elevation tiles (AWS Terrain Tiles, terrarium z15, 5x5 around the centre) -> <dir>/big.npy
# 2. Overture extracts
BBOX=113.995,114.035,22.283,22.312 OUT=db python3 pipeline/ov.py roads   # also: bldg land water landuse places
# 3. world
IN=db CENTER=22.29589,114.0165 BOX=-520,530,-480,270 MAINROAD="Discovery Bay Road" JUNCROAD="Plaza Lane" \
  CW=14 CS=6 CG=4 RAMP=60 python3 pipeline/build_data.py
python3 pipeline/places_db.py
```

Defaults in `build_data.py` reproduce Ha Yeung (`CENTER=22.304332,114.286545`, `BOX=-330,720,-420,330`).

## Data credits

Elevation: AWS Terrain Tiles (Mapzen terrarium; mixed sources, about 30 m). Roads, buildings, land and places: Overture Maps Foundation, © OpenStreetMap contributors (ODbL). People, shops and dogs in the game are fictional.
