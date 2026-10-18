# MG technique catalogue — MG-001 … MG-093

Pick with `mg-brain.md` (meaning → metaphor → layout → technique). Code helpers: `assets/mg-kit/mg-kit.js` (`MG.*`), styles `mg-kit.css`, working example `demo.html`; text helpers in `assets/rtl-kit.js` (`RK.*`) and `assets/ta_kit.js` (`TA.*`).
Units: 30 fps, `f` = 1/30 s, px in the 1080×1920 canvas (render 4K with `--resolution portrait-4k`). Eases: GSAP names. Every recipe is seek-safe: paused timeline, no `Math.random` (use `MG.rng(seed)`), no `repeat:-1`, transforms/opacity/clip/filter only, no CSS `transform` on GSAP-animated nodes, never tween a timed `.clip` element.
Format per entry — **Look** · **When** · **Recipe** · **Assets** · **RTL** (Arabic pitfalls; "—" = none).
Global RTL rules: never split Arabic into letter spans (whole words, clip wipes or text substrings only); Arabic reveals run right→left, Latin/code left→right; digits Western, never kashida'd; UI in RTL is mirrored (send button left, outgoing chat bubbles left, back arrow right); numbers inside Arabic lines keep LTR order (`<bdi>`).

---

## A. Kinetic typography

### MG-001 Spring word pop (target-level headline)
- Look: centred heavy line (Cairo 900, ~104 px) on a fixed top band; words pop RTL at their final positions, one accent word by colour only.
- When: takeover/stage headlines, the written hook, any line that names the metaphor.
- Recipe: `MG.springWords(tl, el, wordTimes)` — scale .6→1 back.out(2.5), y 14→0, opacity 3 f, 12 f total, words 18–36 f apart; small words skip the scale. Line stays until the transition; it is the last thing to leave.
- Assets: Cairo-VF / Tajawal ExtraBold. RTL: the line is laid out centred BEFORE animating (no reflow).

### MG-002 Ghost / outline giant word
- Look: 300–420 px outline word at 8–12 % opacity behind the hero, slow drift.
- When: chapter themes, definition beats, depth on a takeover stage.
- Recipe: `-webkit-text-stroke:2px var(--mg-ink); color:transparent`; fade 12 f, drift x −30 px over the beat `sine.inOut`.
- RTL: crop off-frame on the LEFT so the word's start (right) stays readable.

### MG-003 Kashida stretch on the term
- Look: the key word's tatweel bar grows, then the tail lands.
- When: a defined term, a hero word, signature moment (1 per screen).
- Recipe: `RK.kashidaIn(tl, el, t, {n:6})` (wipe 6 f + bar 12 f power3.out).
- RTL: only legal joins (helper enforces), never inside «لا», never on digits.

### MG-004 Mask rise per word
- Look: each word slides up out of an invisible line mask.
- When: sublines, quotes, calm premium pace.
- Recipe: `TA.maskRise(tl, el, t, {stagger:3f})` — yPercent 100→0, 10 f power3.out.
- RTL: order words right→left (helper does).

### MG-005 Weight / size shift
- Look: a word breathes from light 200 to black 900 (variable font) or one word swells while others shrink.
- When: emphasis without colour, "more/less", contrast inside one line.
- Recipe: tween `fontVariationSettings:"'wght' 200"→"'wght' 900"` 12 f power2.inOut (Cairo-VF/Alexandria-VF); see `assets/templates/ar/ar-weight-shift.html`.
- RTL: width grows with weight → centre-anchored container to avoid jitter.

### MG-006 Scale-through (zoom into a letter/word)
- Look: the camera dives into a letter counter or the dot of a letter → the next scene inside.
- When: transition into a new chapter/world (hero transition, 1 per reel).
- Recipe: group scale 1→12 power2.in 8 f around the counter's coordinates (`transformOrigin` px), next scene starts at scale 1.3→1 expo.out.
- RTL: pick a closed counter (ه، و، ص) or a dot.

### MG-007 Slot-machine roll
- Look: a word cell rolls vertically through options and lands with a bounce.
- When: tool names, "any X", choosing among options, randomness.
- Recipe: `MG.roll(tl, parent, t, ['Cursor','Lovable','Claude'], {lineHeight:130})` — steps 7 f power2.inOut, last 14 f back.out(1.6).
- Assets: logos optional per item. RTL: Latin names fine; Arabic items keep whole words.

### MG-008 Typewriter + caret
- Look: text appears char by char with a blinking caret.
- When: prompts, searches, chat input, code.
- Recipe: `MG.type(tl, el, t, text, {cps:18–24, caret})` (finite caret blink, ends visible); word-mode `{by:'word'}` for long Arabic.
- RTL: char typing shows intermediate letter shapes — that is realistic; keep `dir="rtl"` on the field.

### MG-009 Justified stacked block
- Look: 3–4 lines stacked to equal width (size per line differs), tight leading.
- When: a manifesto/rule, a summary card in takeover.
- Recipe: measure with `window.__hyperframes.pretext` or kashida-justify (`RK.kashida`) lines to the widest; lines enter 4 f apart mask-rise.
- RTL: justify Arabic with kashida, never letter-spacing.

### MG-010 Flip card (myth / truth)
- Look: a card flips on Y showing the corrected statement on its back.
- When: T16 contrast, "people think… but".
- Recipe: parent `.mg-3d`; front rotationY 0→90 power2.in 7 f, back −90→0 power3.out 8 f; `backface-visibility:hidden`.
- RTL: flip direction right→left (rotationY negative first).

### MG-011 Footage inside type
- Look: giant word filled with the speaker's blurred footage or a texture.
- When: brand/hero word over a takeover; intro title.
- Recipe: `background-clip:text` with a still frame/gradient; animate `backgroundPosition` slowly; or SVG `<clipPath>` text over a `<video>`.
- RTL: heavy weight only (thin Arabic strokes lose the image).

### MG-012 Strike + replace
- Look: an accent bar sweeps through a word, the word dims, the correct word pops beside/below.
- When: negation, prices → $0, old way → new way.
- Recipe: `MG.strike(tl, el, t)` (scaleX from right 8 f power3.out, dim .55) then `MG.springWords` the new word.
- RTL: sweep right→left (`{ltr:true}` for Latin/prices).

## B. Shapes & lines

### MG-013 Path morph (shape → shape)
- Look: one outline smoothly becomes another (circle → shield, bubble → logo, check → cross).
- When: the verb is "becomes/turns into/protects/fixes"; continuity between beats.
- Recipe: `MG.morph(tl, path, t, toD, {dur:14f, ease:'power3.inOut', points:96})` — any two paths (resampled + aligned); chain in time order. Combine with fill/stroke colour tween.
- Assets: simple SVG icons (same family, 1 stroke weight). RTL: —

### MG-014 Liquid blob
- Look: soft organic blob slowly morphing, glow; can swallow/release objects.
- When: background life on stages, "AI thinking", transitions between colour worlds.
- Recipe: 3–4 blob paths, `MG.morph` chain 1.2–2 s `sine.inOut`; or CSS border-radius keyframes (`border-radius: 42% 58% 63% 37% / 41% 44% 56% 59%`) tweened; blur 40–80 px for background blobs.
- RTL: —

### MG-015 Box morph (card ↔ pill ↔ circle ↔ bar)
- Look: a DOM container changes width/height/radius and content swaps inside.
- When: button → card → screen, notification → panel, any UI growing.
- Recipe: `tl.to(el,{width,height,borderRadius,duration:12f,ease:'power3.inOut'})`; inner content `MG.swap` at 40 %.
- RTL: anchor growth from the right edge (`right:` positioning) for RTL UIs.

### MG-016 Fake morph (swap)
- Look: A grows + blurs out while B settles from smaller — reads as a morph for different silhouettes.
- When: logos, photos, complex icons that cannot path-morph.
- Recipe: `MG.swap(tl, a, b, t, {dur:7f})`.
- RTL: —

### MG-017 Orbit rings
- Look: thin ellipses with dots/logos revolving, depth by scale.
- When: ecosystem, "tools around an AI model", AI core.
- Recipe: `MG.orbit(tl, items, t, {rx:360, ry:120, turns:.5, dur:3})` (finite); ring = SVG ellipse drawn with `MG.draw`.
- RTL: revolve counter-clockwise (front item moves right→left).

### MG-018 Shockwave / ripple
- Look: expanding ring that fades, from an impact or click.
- When: hits, slams, clicks, a pin landing, "spreads everywhere".
- Recipe: `MG.shockwave(tl, parent, t, {at:[x,y], size:600})` 16 f expo.out; stack 2 with 4 f offset for water ripples.
- RTL: —

### MG-019 Stroke draw-on
- Look: lines/icons draw themselves (trim path).
- When: diagrams, wireframes, icon builds, underlines, signatures.
- Recipe: `MG.draw(tl, paths, t, {dur:12–18f, ease:'power2.inOut', stagger:3f})`; outline first, fill fades in at frame 6–20; `MG.erase` to exit forward.
- Assets: stroke icons with round caps/joins. RTL: path direction right→left for flowcharts (reverse path or `{reverse:true}`).

### MG-020 Growing connectors / arrows
- Look: dashed or solid lines grow from node to node, arrowhead pops at the end.
- When: cause → effect, integration (MCP), data flow.
- Recipe: `MG.draw` the connector 10–14 f, arrowhead `popIn` 6 f back.out at end; marching dashes = `strokeDashoffset` finite tween.
- RTL: flows run right→left.

### MG-021 Dot travelling along a path
- Look: a glowing dot/token/key moves along a route, lighting nodes it passes.
- When: requests, data, "goes from A to B", leaks, delivery.
- Recipe: `MG.travel(tl, dot, path, t, {dur:1, ease:'power2.inOut', rotate:true})`; trigger node highlights at the path fractions (compute times).
- RTL: start on the right.

### MG-022 Hand-drawn annotation
- Look: wobbly circle/underline/arrow around a UI element, marker style.
- When: point at a setting, button, line of code, number.
- Recipe: hand-drawn SVG paths (slightly overshooting loop), `MG.draw` 14 f power2.out; optional 12 fps stepping (MG-090). See `assets/templates/ar/ar-hw-scribble-transition.html`.
- RTL: arrows point toward the target, never onto the speaker's face.

### MG-023 Blueprint grid draw
- Look: a 90 px grid draws itself, then the object appears on it.
- When: "planning", architecture, building a site/app.
- Recipe: `.mg-grid` stage with `clip-path` reveal from centre, or line set drawn with `MG.draw` stagger 1 f; drift `MG.gridDrift` 40 px/s.
- RTL: —

### MG-024 Radial burst lines
- Look: short strokes shoot out radially around an object.
- When: "new", reveal, success, emphasis on a logo/number.
- Recipe: 8–12 lines, each `MG.draw` 6 f then `MG.erase` 6 f, stagger 1 f; rotate group 15°.
- RTL: —

## C. Transitions, masks & reveals

### MG-025 Wipe with coloured edge bar
- Look: the next scene slides in behind a 24 px bar in another palette colour.
- When: default takeover in/out; between two stage colours.
- Recipe: `MG.takeover(tl, stage, t, {style:'wipe', from:'right'})` (power4.inOut 8 f, ~60 % of travel in 2 middle frames); `giveBack` continues direction. Alternate directions across the reel.
- RTL: first wipe from the right.

### MG-026 Blinds / slats
- Look: horizontal slats of different widths slide in staggered.
- When: a stronger chapter change (≤ 1 per reel).
- Recipe: 6–8 divs full width, x 100 %→0, 9 f power3.inOut, stagger 1 f top→bottom.
- RTL: slats from the right.

### MG-027 Push into colour
- Look: the whole frame pushes up/sideways revealing a flat colour world.
- When: switching to a takeover whose mood differs.
- Recipe: `MG.takeover(..., {style:'push', under:'#spk-sh'})` 12 f power3.inOut; old scene darkens to .45.
- RTL: —

### MG-028 Iris from an element
- Look: a circle grows from a button, dot, caret or spark to fill the frame.
- When: "click → result", idea → world, the speaker's PiP dot → takeover.
- Recipe: `MG.takeover(tl, stage, t, {style:'iris', at:[x,y]})` expo.in 10 f (~×1.6 radius/frame).
- RTL: —

### MG-029 Glitch cut
- Look: 5–7 frames of slice displacement + hue jitter, hard cut in the middle.
- When: errors, hacks, "wait", tech transitions (≤ 2 per reel).
- Recipe: `MG.glitch(tl, el, t, {frames:6, seed})` on the outgoing scene, next scene starts at frame 3.
- RTL: — (keep away from caption text).

### MG-030 Zoom-through (dynamic zoom)
- Look: camera flies into a screen/window/object and lands in the scene inside.
- When: into the speaker's monitor (L-OTS), into a phone, into a folder.
- Recipe: outer group scale 1→6 power3.in 12 f centred on the target; inner scene from scale .4→1 expo.out 12 f overlapping 4 f; blur 0→8→0.
- RTL: —

### MG-031 Pixelate / blur → clear reveal
- Look: a card is pixelated/desaturated and clears on the reveal word.
- When: curiosity, results, «انظر إلى النتيجة».
- Recipe: `filter: blur(18px) saturate(.4) brightness(.7)` → none 10 f power2.out on the word; pixelation = render at low res via CSS `image-rendering:pixelated` scale trick.
- RTL: —

### MG-032 Blur-whip swap
- Look: old content whips sideways with motion blur, new arrives.
- When: fast list switches, comparisons.
- Recipe: `MG.takeover(..., {style:'blur-whip'})` or per object x ±260 + blur 30, 10 f.
- RTL: new content enters from the right.

### MG-033 Morph cut (object becomes the next object)
- Look: the last beat's object transforms into this beat's object (cell → card, pill → city, line → tube, circle → the speaker's PiP).
- When: the default way to chain metaphors — premium continuity.
- Recipe: `MG.morph` (paths), `MG.swap` (DOM/images), `tl.to(el,{width,height,borderRadius})` (boxes); timed so the morph completes ON the new hit word.
- RTL: —

### MG-034 Flipping stack / card deck
- Look: cards stacked in depth; the top one flips away to reveal the next.
- When: rankings, tips 1-2-3, "next".
- Recipe: stack with y offsets 18 px and scale .95 steps; out-card rotationX 0→−90 + y −120 9 f power2.in, rest move up 8 f power3.out.
- RTL: —

### MG-035 Match cut by shape/position
- Look: a round thing in scene A cuts to a round thing at the same position in B.
- When: between takeovers or from MG back to the speaker's face (a ring → the circle PiP).
- Recipe: align centres/sizes exactly; cut on the motion's midpoint ("12 f move, cut on 6, pick up on 7").
- RTL: —

### MG-036 Ink / liquid reveal mask
- Look: organic ink spreads to reveal the next scene.
- When: soft/creative topics, calm transitions.
- Recipe: SVG mask with 3–5 circles scaled with stagger + `feTurbulence`/`feDisplacementMap` (static seed); 14 f power2.out. Or a pre-rendered CC0 luma matte as `mask-image` video frames.
- RTL: —

## D. Camera & depth

### MG-037 Zoom into the detail (screen recording)
- Look: the screen recording zooms smoothly into the typed field, then out on the result.
- When: every demo (default).
- Recipe: wrapper scale 1→1.8 with transformOrigin at the field, 0.9 s power3.inOut; hold; out 0.9 s; add a soft highlight ring (`MG.ring` on a rect geometry).
- RTL: —

### MG-038 2.5D parallax layers
- Look: background / mid / foreground move at different speeds → depth.
- When: any held stage > 2 s ("never fully still"), photo collages.
- Recipe: `MG.parallax(tl, [{el:bg,depth:.3},{el:mid,depth:.6},{el:fg,depth:1}], t, dur, {dx:-60, zoom:.04})` sine.inOut.
- RTL: truck right→left (dx negative).

### MG-039 Camera fly over a big canvas
- Look: one huge board; the camera travels from region to region.
- When: a process with 3–5 stations, a "map" of an ecosystem.
- Recipe: board 3000×5000 px; `tl.to(board,{x,y,scale,duration:.9,ease:'expo.inOut'})` per station, hold ≥ 1.5 s.
- RTL: stations ordered right→left/top→bottom.

### MG-040 3D card tilt / rise
- Look: a UI card rises from a steep angle and settles slightly tilted, floats.
- When: product/UI reveals, proof cards.
- Recipe: `MG.tiltIn(tl, el, t, {rx:12, ry:-18, float:2})` (parent `.mg-3d`); light sweep (MG-049) after landing.
- RTL: tilt toward the right side (ry negative).

### MG-041 Speed lines / motion trail
- Look: streaks behind a moving object; ghost copies.
- When: speed, automation, «بسرعة».
- Recipe: 3 ghost copies at opacity .3/.2/.1 following with 1–2 f lag (same tween, offset start); or thin lines scaleX 0→1→0 behind.
- RTL: trails extend to the right of an object moving left.

### MG-042 Extruded 3D type / tiles
- Look: thick 3D letters or app tiles with a side face.
- When: hero numbers, brand names, big app icons.
- Recipe: `textShadow / boxShadow = MG.extrude(14, '#7a3a2c')` + light sweep; rotate with rotationX/Y on parent `.mg-3d`.
- RTL: extrude down-left for RTL reading balance (`MG.extrude(14, c, -1, 1)`).

### MG-043 Three.js hero object
- Look: real 3D (glossy brain, key, shield, chip, globe) rotating slowly, lit.
- When: THE abstract hero noun of the reel (1–2 per reel).
- Recipe: render the Three.js frame from the HyperFrames seek time (`hf-seek`), never a `requestAnimationFrame` clock; `data-duration` on root, assets preloaded; alpha canvas over the stage.
- Assets: glTF from Poly Pizza/Sketchfab CC0, or built from primitives. RTL: —

### MG-044 Isometric world
- Look: 30° isometric mini-world (servers, laptop, buildings) assembling.
- When: architecture (frontend/backend/database), "how a website works".
- Recipe: SVG iso tiles; pieces drop y −200→0 back.out(1.4) stagger 3 f; connectors (MG-020) between.
- Assets: iso icon set (one family). RTL: build order right→left.

## E. Particles & FX

### MG-045 Particle converge (many → one)
- Look: a cloud of dots flows into one point/shape.
- When: "all this started from one idea", simplification, AI condensing data.
- Recipe: `pts = MG.particles(stage, 60, {seed})` → `MG.converge(tl, pts, t, {at:[540,960]})` power3.in; end with a pulse ring.
- RTL: —

### MG-046 Burst / explosion (one → many)
- Look: one point bursts into many particles/icons.
- When: scale, spread, launch, «ينتشر».
- Recipe: `MG.burst(tl, pts, t, {at})` expo.out + MG-018 shockwave + flash frame (≤ 3 f).
- RTL: —

### MG-047 Icon swarm / scatter
- Look: many small icons/logos/price tags fly in or scatter away.
- When: overload, subscriptions, money leaving, «كل هذه الأدوات».
- Recipe: particles builder with `<img>` children instead of dots; scatter = burst reversed with rotation ±40° seeded.
- Assets: logo set (official SVGs, Simple Icons). RTL: —

### MG-048 RGB split / glitch tint
- Look: red/cyan channel offsets, slices, scanlines.
- When: danger, hacking, errors (T14).
- Recipe: `MG.glitch`; for text use `textShadow:'3px 0 #ff3b5c,-3px 0 #2fe6ff'` flicker on seeded frames; scanlines = repeating-linear-gradient overlay 6 % opacity.
- RTL: keep Arabic text sharp in the final frame.

### MG-049 Light sweep / sheen
- Look: a diagonal highlight passes over a card/logo/word.
- When: "premium", completion, landing of a hero.
- Recipe: `::after` gradient 105° translateX −120→120 % 22 f power2.inOut, `mix-blend-mode:screen`; or `TA.shimmer` for text.
- RTL: sweep right→left.

### MG-050 Grain, vignette, glow, leaks
- Look: finishing layer.
- When: always subtle on full-frame MG (unless the clean System A look from `mg-recipes.md` is chosen — then no grain).
- Recipe: grain via seeded noise PNG sequence 3–5 %; vignette radial 20–30 %; warm glow `.mg-glow` behind hero; light leak overlay (`assets/templates/ar/ar-organic-light-leak-overlay.html`) on transitions only.
- RTL: —

## F. Data visualisation (real numbers only)

### MG-051 Counter / odometer slam
- Look: number counts up and lands with a tiny scale punch + hit.
- When: any spoken number (T01, T19).
- Recipe: `MG.count(tl, el, t, N, {dur, ease:'expo.out', suffix, sep:','})` with `dur` ending ON the number word; `font-variant-numeric: tabular-nums`; land: scale 1.12→1 6 f + MG-018.
- RTL: Western digits; unit word after the number in reading order (`<bdi>`).

### MG-052 Scale comparison (circles/objects by size)
- Look: two circles (or objects) whose areas match the values.
- When: A vs B magnitude, «أكبر بعشر مرات».
- Recipe: radius ∝ √value; small pops first, big grows from it 18 f expo.out; labels inside.
- RTL: first-mentioned on the right.

### MG-053 Bar chart grow
- Look: bars rise (or grow sideways) with values counting.
- When: 2–6 values the speaker says.
- Recipe: `MG.bars(tl, parent, t, data, {rect, suffix, horizontal})` stagger 4 f, 16 f power3.out; winner `accent:true`.
- RTL: vertical order right→left; horizontal bars grow right→left (built in).

### MG-054 Line chart + area
- Look: a line draws with area fill following, end dot pops.
- When: growth/decline over time.
- Recipe: `MG.lineChart(tl, svg, t, values, {rect, dur:1.1})`.
- RTL: time axis may stay left→right (convention) — pick one per reel and keep it.

### MG-055 Donut / ring
- Look: ring fills to a percentage, number counts in the centre.
- When: a single percentage, progress, share.
- Recipe: `MG.donut(tl, parent, t, pct, {x, y, size, stroke})` (fills counter-clockwise for RTL; `{cw:true}` otherwise).
- RTL: built in.

### MG-056 Bar race
- Look: horizontal bars re-order as values change over time.
- When: ranking changes, «أصبح الأول».
- Recipe: bars as absolutely positioned rows; per step tween widths and `y = rank * rowH` 12 f power2.inOut; numbers via `MG.count`. Keep ≤ 6 rows, ≤ 4 steps.
- RTL: bars grow right→left, labels on the right.

### MG-057 Gauge / meter
- Look: semicircle meter with a needle swinging to a value (overshoot).
- When: risk level, quality, speed, "danger".
- Recipe: `MG.gauge(tl, parent, t, pct, {x, y, size})` (needle back.out(1.2)); colour the arc accent or red by meaning.
- RTL: —

### MG-058 Waffle / dot grid (part of whole)
- Look: 100 (or 10/20) cells; N light up.
- When: most people, shares, «4 من كل 100».
- Recipe: `MG.waffle(tl, parent, t, {n:100, on:4, cols:10, at:hitTime})` — grid wave enter, lit cells pulse accent on the hit.
- RTL: fills from the top-right (`from:'end'`).

### MG-059 Clock sweep / countdown
- Look: clock hand sweeps fast; or a big countdown 3-2-1.
- When: time, deadlines, «في دقيقة».
- Recipe: hand rotation tween (finite turns) power2.inOut; countdown = `MG.count` with `ease:'steps(N)'`; collapse a 3-hour clock into a 5-minute timer with scale squash (worked example 6).
- RTL: —

### MG-060 Progress bar race / timeline playhead
- Look: one or more progress bars filling; or an editor timeline with a moving playhead.
- When: speed comparison, loading, "the AI is working", process duration.
- Recipe: fill scaleX 0→1 with different eases per bar (winner `expo.out`); playhead x linear (allowed: it IS a clock).
- RTL: fill right→left in Arabic UI; video timelines stay LTR.

## G. Maps & places

### MG-061 Map zoom + pin drop
- Look: flat map, camera zooms to a country/city, pin drops with a ripple.
- When: places the speaker names (country, city).
- Recipe: SVG world/country map (Natural Earth, public domain); group scale/translate 1 s expo.inOut; pin y −120→0 back.out(1.6) 10 f + MG-018; country fill accent.
- Assets: SVG map. RTL: Arabic labels, never Latin place names.

### MG-062 Route draw
- Look: dashed route draws between two points, a dot/plane travels it.
- When: journeys, "from X to Y", data travelling.
- Recipe: quadratic path; `MG.draw` + `MG.travel({rotate:true})`.
- RTL: —

### MG-063 Globe with arcs
- Look: rotating globe, arcs pop between cities.
- When: "worldwide", users everywhere, networks.
- Recipe: Three.js (MG-043) sphere + arcs, or 2D orthographic SVG with rotating longitude (precomputed).
- RTL: rotate west → east so the Arab world comes to the front on the key word.

## H. UI mockups (rebuild, never paste screenshots)

### MG-064 Browser build
- Look: browser chrome appears, the site inside assembles.
- When: websites, landing pages, «موقعك».
- Recipe: `B = MG.ui.browser(parent, {rect, url})` + `MG.uiIn(tl, B.box, t, 'tilt')`; fill `B.body` with blocks (MG-073).
- RTL: Arabic sites `dir="rtl"` inside the body; URL bar stays LTR.

### MG-065 Phone mock + scroll
- Look: phone frame; app screens scroll or slide like cards.
- When: apps, TikTok/IG talk, mobile builds; L-DEVICE.
- Recipe: `P = MG.ui.phone(parent)`; content in `P.inner`; `MG.scroll(tl, P.inner, t, dy)`; the speaker inside = `MG.frameTo(spk,'device-phone')`.
- RTL: mirrored app chrome (back arrow right).

### MG-066 Prompt bar typing
- Look: AI input bar; prompt types; send pressed.
- When: every "you type it a prompt" line, «تكتب له».
- Recipe: `p = MG.ui.prompt(parent, {rect, placeholder})` → `MG.uiIn` → `MG.type(tl, p.field, t, text, {caret:p.caret})` → `MG.click(..., {press:p.send})` → iris (MG-028) into the result.
- RTL: send button sits LEFT; Latin prompts set `{dir:'ltr'}`.

### MG-067 Code editor typing
- Look: dark editor with line numbers; syntax-coloured lines type in.
- When: code, vibe coding, API keys, «سطر واحد».
- Recipe: `E = MG.ui.editor(parent, {file, lines:[html with .tk-k/.tk-s/.tk-f/.tk-c/.tk-n]})` → `MG.typeLines(tl, E.lines, t, {cps:30})` (clip + steps keeps colours); highlight a line with an accent background bar at 15 % (it is UI, not caption text).
- Assets: JetBrains Mono (Google Fonts). RTL: code always LTR.

### MG-068 Terminal
- Look: terminal window, command types, output lines appear instantly, green ✓.
- When: installs, CLI tools, Claude Code.
- Recipe: `T = MG.ui.terminal(parent)`; `L = MG.ui.lines(T.body, [{text, cls:'is-cmd'}, {text, cls:'is-ok'}])`; `MG.typeLines(tl, L, t, {instant:[L[1]]})`.
- RTL: LTR inside.

### MG-069 Screen recording highlight
- Look: the speaker's own recording in the split stage, zoom (MG-037), a soft spotlight dims everything but the field.
- When: real demos.
- Recipe: recording `<video>` in the stage; spotlight = full overlay with `mask-image: radial-gradient(...)` animated position; ring around the field.
- RTL: —

### MG-070 Cursor path + click
- Look: macOS-like cursor moves on a curved path, squashes, ripple.
- When: buttons, menus, «تضغط هنا».
- Recipe: `c = MG.cursor(parent)`; `MG.click(tl, c, t, from, to, {press:btn})` (x power2.inOut / y power3.inOut = curve).
- RTL: —

### MG-071 Button press / counter UI (CTA)
- Look: Save/Follow/Like button pressed, count ticks up, icon fills.
- When: CTA, social proof the speaker states.
- Recipe: button `popIn`, `MG.click` press, icon `MG.morph` outline → filled, `MG.count` +1.
- RTL: Arabic labels («احفظ»، «تابع»).

### MG-072 Chat thread
- Look: AI conversation; bubbles pop, typing dots before AI replies, thread scrolls.
- When: talking to Claude/ChatGPT, examples of answers.
- Recipe: `C = MG.ui.chat(parent, {msgs})` + `MG.chatPlay(tl, C, times)`; an AI reply can type with `MG.type` instead.
- RTL: outgoing (user) bubbles LEFT (accent), AI right (built in); keep each bubble ≤ 2 lines.

### MG-073 Site assembling (skeleton → content)
- Look: grey skeleton blocks appear, then real content (image, headline, button) replaces each.
- When: generation, loading, «يبني لك موقعاً».
- Recipe: skeleton divs drop in stagger 3 f back.out(1.4); per block `MG.swap` to the real block; final light sweep.
- Assets: Pexels photo, brand-free fonts. RTL: blocks build right column first.

### MG-074 Notification stack
- Look: iOS-style glass notifications slide down and stack.
- When: messages, alerts, sales, «وصلك إشعار».
- Recipe: `MG.ui.notif(parent, {title, body, icon})` + `MG.uiIn(..., 'drop')`; older ones scale .94 and move down 20 px.
- RTL: icon on the right.

## I. Diagrams & systems

### MG-075 Node flow with travelling pulse
- Look: rounded nodes connected; a pulse travels and lights each node.
- When: processes, pipelines, agents, request → response.
- Recipe: nodes `popIn` stagger 4 f; connectors `MG.draw`; pulse `MG.travel` along one combined path; node highlight at computed fractions.
- RTL: right→left / top→bottom order.

### MG-076 Logo wheel → hero → dock
- Look: logos orbit; the active one swells to a hero with its number/name, then docks to a header strip.
- When: listicles of tools/skills.
- Recipe: `MG.orbit` → selected logo `tl.to(scale 3, x/y centre, 14f expo.inOut)` → hero text `springWords` → dock `tl.to(scale .5, x/y header)`.
- Assets: official logos SVG. RTL: dock order right→left.

### MG-077 Exploded stack (layers)
- Look: a stack (app, model, OS) separates into floating layers in 3D, labels appear.
- When: "what's inside", tech stack, layers of security.
- Recipe: `.mg-3d` parent rotateX 55 rotateZ −30; layers translateY steps −90 px stagger 3 f power3.out; labels with connector lines.
- RTL: labels on the right side.

### MG-078 Versus split
- Look: frame splits into two worlds (colour each), items appear on both sides; a VS mark slams.
- When: comparisons (T04).
- Recipe: two halves clip-path wipe from the seam 10 f; VS `RK.slam`; winner side brightens, loser `filter: grayscale(1) brightness(.7)` 10 f.
- RTL: first-mentioned on the right/top.

### MG-079 Before / after slider
- Look: divider line slides across an image revealing the after.
- When: redesigns, results, «قبل وبعد».
- Recipe: after layer `clipPath: inset(0 0 0 X%)` tween 100→0 % 1 s power2.inOut, divider follows; handle pulse.
- RTL: reveal from right (after on the left side becomes visible as it moves left).

### MG-080 Funnel / tree / branching
- Look: items flow into a funnel and fewer come out; or a tree branches.
- When: filtering, decisions, "options".
- Recipe: dots travel down paths (MG-021) with some fading at each stage; tree = `MG.draw` branch paths stagger, leaf nodes pop.
- RTL: —

## J. Icons, illustration & collage

### MG-081 Icon grid light-up
- Look: grid of dim icons; the named ones light accent with a pop.
- When: features, "it can do X, Y, Z".
- Recipe: grid of 6–12 icons opacity .25; on each word `tl.to(icon,{opacity:1, color:accent, scale:1.15→1})`.
- Assets: ONE icon family (Lucide/Phosphor). RTL: order right→left.

### MG-082 Sticker cut-out
- Look: object/person with thick white outline, drop shadow, slaps in with rotation.
- When: playful beats, meme-ish reactions, objects (laptop, coffee).
- Recipe: PNG with outline via 8 stacked `drop-shadow(0 0 0 #fff)` offsets; in: scale 1.4→1, rotation −12→−4, 8 f back.out(2); MG-090 stepping optional.
- RTL: —

### MG-083 Paper collage / cut-out (12 fps)
- Look: torn paper shapes, halftone photos, stepped motion.
- When: editorial/story beats, history, «في الماضي».
- Recipe: textures + halftone photos; motion on 2s (MG-090); paper SFX.
- Assets: paper textures (CC0). RTL: —

### MG-084 Lock / shield build & break
- Look: padlock or shield draws, snaps shut (or cracks open with glitch).
- When: security (T14/T15).
- Recipe: `MG.draw` outline → fill fade → shackle y −30→0 back.out(2.5) 8 f + click; break: crack path draw + `MG.glitch` + shackle pops up; red tint.
- RTL: —

### MG-085 Checklist ticks
- Look: list items with checkboxes; ticks draw in one after another.
- When: steps done, requirements, «تأكد من».
- Recipe: tick path `MG.draw` 8 f per item on its word; item text `TA.maskRise`.
- RTL: checkbox on the right of each line.

## K. Mood, symbol & rhythm

### MG-086 Colour-world flip
- Look: the stage background flips between the 3 palette colours on beats.
- When: every takeover change; contrast moments.
- Recipe: `MG.flipColor(tl, stage, t, color)` 6 f or via a wipe (MG-025); text always in the two colours that are not the background.
- RTL: —

### MG-087 Smooth push + grade shift (no graphic)
- Look: slow push 1.00→1.07 while the grade cools/warms slightly.
- When: emotional, serious lines (T17) — restraint is the technique.
- Recipe: `MG.frameTo(spk, {rect:[...full], zoom:1.07, faceAt:.33})` over the sentence `sine.inOut`; any grade shift in the NLE (or skip it).
- RTL: —

### MG-088 Freeze / pause beat
- Look: everything stops for 10–22 f (deliberate stillness), a pause icon or frame counter blinks.
- When: before a reveal, «انتظر»، «مهلاً».
- Recipe: hold all tweens; frame counter `f ####` (MG-091) blinks via finite yoyo; then hard cut.
- RTL: —

### MG-089 Spotlight / vignette breath
- Look: edges darken (or a red pulse) focusing on the centre.
- When: warnings, focus on one element, tension.
- Recipe: radial gradient overlay opacity 0→.35→.15 over 20 f; red variant 15 % for danger.
- RTL: —

### MG-090 12 fps stutter (Vox-hand-made feel)
- Look: graphics move on 2s (every other frame) for a crafted feel.
- When: collage/editorial sections, hand-drawn annotations.
- Recipe: use `ease: 'steps(N)'` with N = duration×15, or quantise in onUpdate (`Math.round(p*15)/15`).
- RTL: —

### MG-091 Frame counter / tech HUD micro-detail
- Look: tiny monospace "f 0234" or coordinates ticking in a corner.
- When: AI/coding topics on takeovers (System A detail, `mg-recipes.md`).
- Recipe: `MG.count` with `ease:'none'` tied to the stage time; 30 px JetBrains Mono, mid-grey, x 122 y 177.
- RTL: corner top-left keeps it out of Arabic reading flow.

### MG-092 Liquid-glass UI panel
- Look: frosted, refractive panel with rim light (Apple 2025 look) holding UI or an image.
- When: premium product/UI reveals (not behind captions).
- Recipe: the `.glass` recipe in `references/craft/03-talking-head-mg.md` + liquid bounce entry (height 3 f, width 4 f back.out(2)).
- RTL: —

### MG-093 Text on a path / arc
- Look: words run along a curve, orbit, or around a circle.
- When: ecosystems, badges, cyclical ideas.
- Recipe: SVG `<textPath>`; animate `startOffset` finite; for Arabic keep whole text, animate `startOffset` 100 %→0.
- RTL: `direction="rtl"` + `text-anchor="end"`; check shaping on Chrome.

---

### Quick index by meaning type (see mg-brain §2)
T01 051/052 · T02 058/055 · T03 054/053 · T04 078/079/052 · T05 076/034/056 · T06 075/019/060 · T07 020/021/033 · T08 059/060/041 · T09 061/062/063 · T10 064–068/072 · T11 069/070/037 · T12 066/073/028 · T13 043/045/013/014 · T14 084/048/012/057 · T15 013/085/020 · T16 012/010/086 · T17 087/089 · T18 001/031 · T19 012/051/047 · T20 045/046/047 · T21 003/002 · T22 071/070
