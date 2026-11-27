# Gandhi News infographics: drawn scenes

Owner's rule, November 27, 2026. The old card (one big icon beside a number, with a small chart) is retired. A Gandhi News
graphic is now a detailed vector drawing of the subject itself, in white on the brand red. A highway story gets a drawn
highway, a state story its map, an industry story its plant, a food-label story the packets and the labels.

A photograph is still the first choice. Draw a graphic only where RUNBOOK.md rules 11 and 11a allow one (nothing to show,
or no correct photo exists anywhere), and for no more than one piece in four.

## The rules

1. Draw the subject. Ask what a reader would see if they stood in front of the story: a road through forest, a port and a
   plant, a state on the map, a House of 60 seats, packets on a shelf. Never an icon beside a number, never a grid of icons,
   never a card of three statistics.
2. Colours: white on `#cc0000`, with `#a30000` for the ground and solid shapes. Nothing else. No gradients, no shadows, no
   pills, no filled colour boxes, no accent bars or stripes, no grey.
3. The figures are part of the drawing and are drawn to scale wherever they can be: a road used as a ruler, a timeline whose
   spacing is real time, one mast or coin for a fixed amount. Say in a label what one mark stands for.
4. Every number, date and name comes from the story. Nothing is added from memory. Where part of the drawing is schematic
   (a valley drawn as an oval, a generic packet), say so in the comment at the top of the scene file.
5. Maps come only from `public/maps/india.svg` (the official boundary, with all of Jammu and Kashmir), through
   `india_locator()` and `state_shape()`. Never draw India or a state by hand.
6. No faces, no party symbols, no company logos or brand names. Packets, lorries and buildings are generic.
7. Labels sit inside the scene, next to what they describe. Type is PT Serif (Hindi: Noto Serif Devanagari), 12 to 18 px for
   labels, set by the kit. No line of text may touch or cross a drawn object or another line of text.
8. The drawing fills the frame down to the source line. No empty lower half.
9. English and Hindi are both made. The Hindi strings use the Hindi story's own spellings (copy them from the Hindi file).
10. Dates are written month day, year in English. No em dashes anywhere.

## How to make one

1. Read the story in both languages. Write down the four or five facts the drawing must carry.
2. Copy the nearest file in `scenes/` to `scenes/<story-id>.py` and rework it. Worked examples:
   - `modi-bastar-naxal-areas-15000-km-roads-9500-towers-claim.py`: a road as a ruler, masts counted in units, forest and hills
   - `manipur-election-2027-60-seats-after-presidents-rule.py`: locator map, a state drawn large, a hemicycle, a timeline to scale
   - `nbs-explained-fertiliser-subsidy-rabi-2026-27-dap-urea.py`: ship, quay crane, plant, sacks, tractor, coins for money
   - `front-of-pack-warning-labels-explained-supreme-court-sugar-salt-fat.py`: objects on a shelf, a detail enlarged, a size drawn to scale
3. A scene file has two things:
   - `STR = {'en': {...}, 'hi': {...}}` with `kicker`, `headline`, `dek`, `source` and every label the drawing uses. The
     headline, dek and source match the story's `infographic:` block.
   - `draw(P, S, lang)` returning `(art, notes, tile_box)`. `art` is the drawing (it is also used alone on cards);
     `notes` are the small labels (left off cards); `tile_box` is `(x, y, width, height)` of the part of the drawing a card shows.
   The frame is 1280 x 853. Keep the drawing between y 170 and y 780; the headline sits above and the source line at y 825.
4. Preview: `python3 newsroom/infographics/build.py <story-id> --preview`. It writes six PNG files to
   `/home/claude/gn-work/infographics/`. Open every one with the Read tool and check:
   - nothing overlaps, nothing is cut off at an edge, no label runs past the frame
   - every figure matches the story, in both languages
   - the Hindi reads correctly and no word is left in English that the Hindi story translates
   - the card picture (`-t`) reads as a picture without its labels, and the share picture (`-cover`) has a clear headline
   - it looks like a drawing of the subject, not a chart with decorations
   Fix and preview again until all six are clean.
5. Register: `python3 newsroom/infographics/build.py <story-id>` (add `--nophoto "<what was searched>"` under rule 11a).
   This writes the pictures to `public/photos/s-<id>-...` and records them in `content/photos.map.json` with `style: "scene"`.
6. If the story's figures change later, change the scene file and run step 5 again.

If a good scene cannot be drawn in the time the run has, hold the piece for the next run as a picture hold (`held.py`, RUNBOOK.md section B) and publish
the rest. A weak graphic is never published to fill a slot. `newsroom/scripts/make_infographic.py` no longer runs.

## The kit (`gnig.py`)

- Frames: `full`, `tile`, `cover` (called by build.py; a scene file never calls them)
- Text: `T` one line, `TL` several lines, `T2` a bold figure with its description
- Land and sky: `ridge` and `smooth` for hills, `y_on`, `forest`, `sal`, `pine`, `wheat`, `waves`, `birds`, `smoke`, `hatch`
- Vehicles: `truck`, `bus`, `car`, `motorbike`, `tractor`, `ship`
- Industry: `quay_crane`, `process_tower`, `silo`, `sphere_tank`, `chimney`, `shed`, `mobile_tower`
- Goods and money: `sack`, `big_bag`, `price_tag`, `coin`, `sign_board`
- Maps: `india_locator`, `state_shape`, `india_paths`, `path_bbox`, `hill_mark`
- Counting and time: `hemicycle`, `timeline`, `hexagon`

When a story needs an object the kit does not have (a dam, a train, a courtroom, a hospital), draw it in the scene file as a
small function in the same line style: white outline 2 to 2.5 px, `P.sh` fill for solid faces, real proportions, enough
detail to be recognised at card size. If it will be useful again, move it into `gnig.py`.
