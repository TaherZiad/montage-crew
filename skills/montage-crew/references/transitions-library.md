# Transitions & cutting library (TR-NNN)

The working catalogue for cuts and transitions in a reel. It builds on `craft/01` (retention), `craft/07` (transition craft), `craft/10` (sources), `resolve/04` (Resolve recipes; Resolve ships 67 Fusion transitions plus 32 simple ones) and `mg-recipes.md` (the measured wipes, irises and morphs of target-level reference reel A). Code: `assets/transitions/tr-kit.js` (GSAP functions) and `assets/transitions/plate.html` + `plate.mjs` (render one transition as an alpha plate or a junction clip).

Research behind it: StudioBinder (transition types, J/L cuts), PremiumBeat (hiding jump cuts, Murch's blink), Adobe (morph cut 4–8 f), TokCount (14 micro-cuts with frame counts), Flashboards (seamless transitions: object, frame, screen, arc, roll, infinite), Murch *Rule of Six* (emotion 51 % > story 23 % > rhythm 10 % > eye-trace 7 % > 2D 5 % > 3D 4 %), the CapCut 2026 trend pages (velocity, beat sync, glitch, zoom-blur, swipe, before/after, slow-mo + blur, liquid morph), Film Impact packs (push, blur-to-colour, glass, rays, spin), luma/ink/liquid matte tutorials (Shotstack, Motion Array, Chris Curry), the framecn kinetic-type-mask (hold 12 f, transition 24 f, max scale 120), retention guides (Shortzly, socialync, Pixflow: interrupt every 5–8 s, a visual change every 3–5 s in the body), and AE motion-blur practice (shutter 180°, up to 360° for fast moves), plus the ~190 tutorials already distilled in `craft/`.

## 0. Defaults (these override everything below, unless the brief, the profile or the user's `rules.md` says otherwise)
- **Smooth zooms, never snaps.** Framing changes are 0.9–1.0 s ease-in-out moves (1.00↔1.07 per list item). Do not punch in on a cut. Do not use expo snaps on the speaker. A zoom *transition* between scenes may be faster (12–20 f), but use the soft profile (`power2`), never `expo` on the speaker's face.
- **No white flashes.** Flashes only in a palette colour, at ≤ 0.4 opacity, or not at all. Do not use dip-to-white either.
- **Few, quiet SFX.** Use at most one SFX per transition, at −8…−12 dB under the voice. Blur cuts, scale-in-place, leaks, morphs and colour flips stay silent. Never put a whoosh on a zoom, and never use shimmer, a record scratch or a flash "crack".
- **Nothing behind the speaker's back.** Content goes on the split stage (speaker on top, the panel below) or into a short full-frame MG cutaway.
- **Bake transitions, assemble with `scripts/compose.py`.** Anything animated is baked in HyperFrames: either an alpha overlay plate over a hard cut, or a junction clip that replaces the cut; `scripts/compose.py` assembles the final MP4 (plus the FCP7 XML when the profile's editor is Resolve/Premiere). In the optional LIVE Resolve mode (`references/resolve/00-control-architecture.md`): Resolve free has no keyframe API, so a framing move goes in as one clip per frame (`scripts/live.py camera`, eased cubic in-out), and `AddTransition` works too (simple or Fusion templates; it needs handles on both sides).
- **Target level** (`mg-recipes.md`): MG-to-MG transitions are *designed*: 6–10 f, a wipe with a 24 px edge bar, an iris grown from a UI element, a glitch cut, a push into colour, or above all a **morph**. Allow at most one plain hard cut per MG sequence.

## 1. Cutting rules (numbers, 30 fps)
**Priority when two cuts compete** (Murch): emotion, then story, then rhythm, then eye-trace, then screen direction, then 3D continuity.

| Rule | Number |
|---|---|
| Dead air between phrases | ≤ 3–6 f (high energy 2–4 f). Keep 1–2 f of breath before a hard consonant ("breath-snip") |
| Deliberate pause before a punchline or emotional line | 8–15 f (max 2 per short), up to 12–30 f after an emotional line |
| Cut point inside a sentence gap | 1–3 f after the last word ends (the "blink" point, where the thought ends), never mid-word |
| J-cut (next audio first) | 3–5 f for talking heads, 6–15 f into B-roll or a new scene |
| L-cut (previous audio carries over) | 6–15 f, used to show a result or reaction while the speaker finishes the line |
| Cut on action / gesture | cut ⅓–½ of the way through the motion (2–3 f in), matching direction and speed on both sides |
| Match cut alignment | key shape within ≤ 40 px and ≤ 10 % size between A and B (check with 50 % onion skin); colour match within ~10° hue |
| Jump-cut hiding (single camera) | Default: alternate framing with **smooth** 1.00↔1.07 moves on sentence gaps. Otherwise B-roll or MG over the joint, or a 3–4 f crossfade + 1.03 scale (poor man's morph cut). Smooth Cut is Studio, not available |
| Morph cut (Premiere/Avid/Resolve Studio) | 4–8 f, only for static head + static background |
| Visual change | Reels 2.5–4 s (hook 1–1.5 s, body 3–5 s); never > 5 s static; new idea every 3–7 s |
| Pattern interrupt | every 5–8 s (B-roll, MG cutaway, split-stage change, music drop) |
| Designed (stylised) transitions | ≤ 1 per 8–15 s; 3–4 in a 60 s reel; 1 hero transition; one family per video; same preset ≤ 3× |
| Transition lengths | cut-based 0 f · micro (colour flip, glitch) 2–7 f · reference-reel wipe/iris 6–10 f · whip 8–10 f · zoom 12–20 f (soft) / 16–30 f (velocity) · leak 15–30 f · morph 10–24 f |
| B-roll / cutaway | 0.5–1 s proof flash, 3–5 s max; rhythm B / 1–2 A / B; cut on its action start |
| Speed ramp | ramp 5–6 f S-curve, peak 400–1000 %, land at 100 % on the beat; same-direction clips only |
| Hook | no stylised transition in the first 1–2 s; first visual change within 15 f |
| Photosensitivity | ≤ 3 flashes/s; subliminal frames ≤ 2 f |

**Pacing curve per reel**: hook (0–3 s, changes every 1–1.5 s) → body (a change every 3–5 s, an interrupt every 5–8 s, a breather beat every 2–3 beats) → pre-payoff slow-down (4–6 s shot, 8–15 f pause) → payoff (the hero transition or morph lands here) → CTA (hard cut, no transition, hold ≥ 1.5 s). Music or section changes are the only places a "big" transition is allowed.

**Seamless rules**: motion speed, direction and exposure must match on both sides of a hidden cut. Peak velocity and peak blur sit on the cut frame (ease-in out of A, ease-out into B). Direction continues: an RTL exit means an RTL entry, a zoom-in continues as a zoom-in, and rotation keeps its sign. For Arabic content "forward" = right→left; keep that consistent across the video.

## 2. Motion blur
- Shutter 180° (standard) means a streak of ½ the per-frame displacement; go up to 360° on whips and spins. Gaussian σ ≈ streak ÷ 3. Example: a whip moving 300 px/f gets a 150 px streak, so σ ≈ 50 → `o.blur` 40–50 (at 1080 wide; the kit scales it by W/1080).
- Use **directional** blur for moves (kit `dirBlur`, an SVG `feGaussianBlur stdDeviation "σ 0"` tweened natively). Use **isotropic** `filter: blur()` only for zooms and spins. Peak blur goes on the cut and is 0 at both ends.
- Rule: once an element moves more than ⅓ of the frame width per frame, it needs blur. Under 40 px/f, skip it.
- Resolve: built-in Push/Slide have a Motion Blur checkbox (set it in the inspector). Fusion Transform motion blur Q 8–10, shutter 180–360. Per-clip ResolveFX Motion Blur is Studio-only, so per-frame Resolve whips have **no blur**: bake them in HyperFrames instead.
- Cheap real blur for a junction clip: render at 120 fps, then `ffmpeg -vf tmix=frames=4,fps=30`.

## 3. Decision table: idea change → transition
| What changes in the story | Use (first choice → alternatives) | Never |
|---|---|---|
| Next sentence, same idea | hard cut (TR-100) + J-cut 3–5 f; default: smooth framing move (TR-109) | any stylised transition |
| Next item of a list (split stage) | panel push in reading direction (TR-115 / TR-002 on the panel) → wipe with bar (TR-040) → morph from the previous item (TR-050) | spin, cube, glitch |
| New section or topic | soft zoom (TR-010) or cover wipe with bar (TR-042) → iris from a UI element (TR-041) | flash, film burn |
| Problem → solution / before → after | wipe RTL (before on the right) (TR-040) → card flip (TR-030) → split doors (TR-043) | dissolve |
| Cause → consequence (X makes Y) | **morph** X into Y (TR-050) → match cut on shape (TR-103) | unrelated wipe |
| Zoom into detail (app, screen, code) | portal into the screen (TR-052) → zoom into letter (TR-060) | spin |
| "Wait / stop / but…" (contrast) | smash cut (TR-108) → colour flip 2 f (TR-093) → hard cut + 8–15 f pause | smooth transitions |
| Error / AI fail / hacking | glitch cut (TR-080) + slices (TR-081), 6–8 f | glitch on anything else |
| Time skip ("after a week") | blur cut (TR-020) → page turn (TR-033) → light leak (TR-090) | whip |
| Emotional / serious line | hard cut or L-cut, nothing else | everything stylised |
| Hook → body | one designed transition (the hero): soft zoom, morph or ink | in the first 1–2 s |
| Full-frame MG cutaway in/out | in: iris from an element in the speaker's frame (TR-041/046) or cover wipe; out: reverse direction wipe or morph back to the speaker's frame (TR-127) | crossfade |
| Big reveal / number | zoom-through + rings (TR-096) → kashida wipe (TR-061) | flash |
| Chapter in a long video | blinds (TR-044), coloured bars (TR-045), kashida wipe (TR-061) | ripple |
| Outro / CTA | hard cut, or iris closing on the logo | — |

## 4. How to build
**A. HyperFrames, inside an MG composition** (MG→MG, panel→panel, cutaways): load GSAP (`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`, or the copy `scripts/fetch_assets.py` downloads) + `assets/transitions/tr-kit.js`, then call e.g. `TR.wipe(tl, "#s1", "#s2", 3.2, 8*TR.F, {dir:"rtl", barColor:"#CF6E56", peek:true})`. A and B must be full-frame siblings (B later in the DOM). The kit hides B at build and shows it on time. After rendering, read `TR.cues` for the SFX times.
**B. Overlay plate over a hard cut** (alpha .mov): `node assets/transitions/plate.mjs <fn> --dur 0.4 --o '{"dir":"rtl","color":"#181813"}' --out <work>/tr/t01 --render` (4K: `--w 2160 --h 3840`). It prints the record start (edit − cut offset) and the SFX. Put the plate on a track above the cut (`scripts/compose.py` overlay; `live.py put` in LIVE Resolve mode). For `leak`/`burn`, set Composite Mode to Screen.
**C. Junction clip with footage** (whip, zoom, spin, cube… on real shots): `node assets/transitions/plate.mjs whip --dur 0.33 --a <work>/tr/cutA.mp4 --a-out 12.40 --b <work>/tr/cutB.mp4 --b-in 0 --out <work>/tr/t02 --render`. This cuts the handles with ffmpeg and renders an mp4. On the base track it replaces `[edit − cut·dur, edit + (1 − cut)·dur]`.
**D. Resolve per-frame clips** (LIVE Resolve mode only; zoom/pan moves, no blur): framing JSON → `live.py camera` (`{"s","e","z0","z1","tx0","tx1","ty0","ty1"}`, cubic in-out per frame). Opacity or rotation per frame would need `SetProperties({"Opacity"|"RotationAngle"})` added to live.py (not done yet; add it when a transition needs it).
**E. Resolve `AddTransition`** (LIVE Resolve mode, 21.1, needs handles both sides; `None` = wrong name or no handles): `left.AddTransition({"type": T, "category": "simple"|"fusion"|"ofx", "position": "end", "alignment": "center", "duration": f})`. Names: see `resolve/04`. Check 16:9 Fusion templates for mirror-edge artefacts on 9:16.

Kit conventions: `t` = start (s), `d` = length, the cut is at `t + d·o.cut` (default 0.5). Options common to all: `o.soft` (default true = soft eases; `false` = editorial expo values), `o.seed`, `o.dir` ∈ rtl|ltr|up|down (= direction of travel), colours `o.color/o.barColor/o.colors`. Default palette (reference reel A): charcoal `#181813`, cream `#ECECDE`, coral `#CF6E56`. Replace these with the video's 3 colours.

## 5. Catalogue
Format: **look** · when / never · frames & eases · blur · SFX (quiet, peak on the cut) · build (HF kit fn | plate | Resolve).

### Cut craft (no effect at all)
- **TR-100 Hard cut.** The default (≈ 95 % of joins). Cut 1–3 f after the thought ends · SFX none · Resolve: just the edit.
- **TR-101 J-cut.** B's audio leads its picture by 3–5 f (talking head) or 6–15 f (new scene) · use: entering B-roll, new section · never: a hook's first frame · Resolve: extend audio (`AppendToTimeline` audio item starting earlier).
- **TR-102 L-cut.** A's audio continues 6–15 f over B (result shot, reaction, screen) · Resolve: as above.
- **TR-103 Match cut on shape.** A circle in A becomes a circle in B (cup → logo → button), aligned ≤ 40 px, 0 f or a 2–4 f blend · use: cause→effect, metaphors · build: place B's shape on A's position in HF (onion skin 50 %).
- **TR-104 Match on motion/direction.** The speaker's hand moving left continues as a card moving left in B · cut 2–3 f into the motion · velocities equal.
- **TR-105 Match on colour.** The last frame of A and the first of B share the dominant colour (accent stage colour flip, reference reel A) · hue ±10°.
- **TR-106 Match on word / sound.** The speaker says «سرعة» and the next shot opens on the same word on screen, or the same sound continues (J-cut 6–15 f) · use: Arabic captions → MG headline handoff.
- **TR-107 Cut on gesture.** Cut at ⅓–½ of a hand gesture, head turn or lean · hides jump cuts better than anything.
- **TR-108 Smash cut.** Loud → silent, or calm → loud, 0 f, no SFX lead-in · use: «بس…», contrast, a joke · never on serious lines.
- **TR-109 Smooth framing alternation (default jump-cut hider).** 1.00 ↔ 1.07 (≤ 1.12) over 27–30 f `ease_io` on sentence gaps, eyes anchored · never a snap punch · LIVE Resolve: `live.py camera` framing JSON; otherwise baked in the MG segment / compose step.
- **TR-110 Cutaway / insert.** B-roll or a proof screenshot 0.5–5 s over continuing voice; on action start · Resolve V2.
- **TR-111 Speed ramp (velocity).** 5–6 f S-ramp to 400–1000 %, land on the beat · only on footage moving the same direction (screen recordings scrolling, hands) · Resolve: retime is not scriptable on free, so bake it with ffmpeg `setpts` segments or a HF `currentTime` mapping · SFX: riser into it, soft hit on landing.
- **TR-112 Freeze hold.** 1 frame frozen 12–45 f with a slight 1.00→1.03 push, under a title or a "wait" line · SFX none, music ducks −12 dB.
- **TR-113 Morph cut (substitute).** 3–4 f crossfade + 1.00→1.03 scale on B to hide a micro jump · only same framing, static background · Resolve: `AddTransition` Cross Dissolve 4 f (Smooth Cut is Studio).
- **TR-114 Speaker-movement seamless.** The speaker leans into the lens (or a hand covers it) at the end of A, and B starts with the speaker leaning back. Cut on the darkest/most-covered frame (≤ 2 f black) · needs to be filmed for it; tell the creator when a script would benefit.

### Soft / premium (safe defaults)
- **TR-010 Soft velocity zoom** (`TR.zoom`). A 1→1.25 `power2.in` + blur 8 px, B 1.2→1 `power2.out`, 2 f crossfade on the cut · 12–20 f · section change · never on the speaker's face mid-sentence · blur isotropic · SFX none (default) · `o.soft:false` = 1→2.2 expo, 16–30 f velocity edit (hype only) · Resolve: Fusion "Zoom In" / "Crash Zoom" via `AddTransition`, or junction plate.
- **TR-020 Blur cut** (`TR.blurCut`). Blur 0→24→0 px, 6 f crossfade, B scale 1.06→1 · 10–16 f `power2` · time skip, calm topic change · SFX none · Resolve: simple "Blur Dissolve" 8–12 f.
- **TR-021 Scale in place** (`TR.scaleInPlace`). A settles to 0.92 and dims; B arrives 1.06→1 with a fade · 10–14 f · panel-to-panel on the split stage, the quietest designed change · SFX none.
- **TR-050 Morph** (`TR.morph(tl, from, to, …)`). FLIP: object A flies onto object B's box while they crossfade (cell → card, pill → bar, logo → button) · 10–24 f `power3.inOut` · cause → consequence, the reference-reel signature · never between unrelated objects · SFX none or a soft pop at landing · build only in HF MG (both objects at rest when built).
- **TR-090 Soft light leak** (`TR.leak`, plate). Warm radial layers drifting, peak 0.75 on the cut · 15–30 f `sine` · premium/emotional chapter change · Composite Mode Screen in Resolve · SFX none · never more than 1 per video.
- **TR-091 Soft film burn** (`TR.burn`, plate). Warm radial from an edge, scale 0.25→1.6 `power2.in`, peak ≤ 0.85 (never pure white) · 15–30 f · flashback, "the old way" · Screen · SFX swell (very low) · Resolve alternative: ofx "Burn Away".
- **TR-092 Palette flash** (`TR.flash`, plate). 2 f up to ≤ 0.4 opacity in a palette colour, 6 f down · emphasis hit · **Default: avoid; never white.**
- **TR-093 Colour flip** (`TR.colorFlip`, plate). 1–3 solid frames of the next stage colour exactly on the cut (reference-reel flash frame) · "wait!" / pattern interrupt · SFX none.
- **TR-116 Dip to colour.** Dip to charcoal (not white) 6–10 f · only at chapter ends · Resolve: simple "Dip To Color Dissolve".
- **TR-117 Luma / gradient wipe.** Soft-edged wipe following brightness (light areas first) · 12–20 f · dreamy/premium · Resolve: Fusion "Luma Wipe" or simple "Edge Wipe" with Feather via `AddTransition` (a feathered edge is not possible with clip-path, so not in the kit).
- **TR-120 Position-matched crossfade** (reference reel A). Crossfade 6–8 f where the hero object of B sits exactly where A's was · build: place in HF, plain opacity tweens.

### Directional (motion)
- **TR-001 Whip pan** (`TR.whip`). A leaves along dir `power3.in`, B enters `power3.out`, directional blur 40 px peak on the cut · 8–10 f · topic change in a fast reel, list items in montage · never with face close-ups mid-word · SFX transition_swipe · Resolve: junction plate (per-frame Pan has no blur); Fusion "Pan Left/Slide Left" acceptable.
- **TR-002 Push** (`TR.push`). A and B ride one `power3.inOut` curve, blur 18 px · 8–14 f · next list item, panel change (RTL = next) · SFX whoosh_soft · Resolve: simple "Push" (Motion Blur on) or per-frame `tx` spans.
- **TR-003 Slide-over** (`TR.slideOver`). B slides over A, A drifts 30 % and dims to 0.55 · 10–14 f · stacking cards, "one more thing" · SFX whoosh_soft · Resolve: simple "Slide".
- **TR-115 Split-panel slide.** On the split stage only the bottom panel pushes (TR-002 on the panel element) while the speaker stays top with a 1.00↔1.07 smooth move · 10–14 f · every list item · SFX quiet whoosh_soft every 2nd item at most.
- **TR-125 Scroll wipe** (TikTok-feed feel). The panel pushes up 10 f `expo.out` with a 3 % overshoot back · feeds, "next post", phone UIs · `TR.push` with `dir:"up", ease:"back.out(1.2)"`.
- **TR-012 Spin** (`TR.spin`). ±25° + the exact over-scale for corner cover (cos + (H/W)·sin, +4 %), blur 10 px · 10–14 f · hype, gaming · never on calm topics · SFX whoosh_fast · Resolve: Fusion "Spin"/"Circle Spin".
- **TR-094 Speed lines** (`TR.speedLines`, plate). Anime radial lines, stepped rotation every 2 f · 10–20 f with a smooth push · shock or realisation · SFX whoosh_fast (low).

### 3D
- **TR-030 Card flip** (`TR.cardFlip`). rotateY 0→90 `power2.in`, B −90→0 `power2.out`, the turning face darkens to 0.6 · 10–16 f · myth/fact, before/after, front/back of an idea · SFX paper · needs a stage colour behind (edges are exposed) · Resolve: Fusion "Flip 3D".
- **TR-031 Mirror flip** (`TR.mirrorFlip`). Flat scaleX through 0 · 6–10 f · "the opposite is true" · SFX paper (low).
- **TR-032 Cube** (`TR.cube`). Both faces rotate about an axis W/2 behind the screen · 12–18 f `power2.inOut` · switching between two apps/tools · never more than once per video (cheap tell) · stage colour behind · Resolve: Fusion "Cube".
- **TR-033 Page turn** (`TR.pageTurn`). Arabic book: hinge on the right edge, the page swings away into the screen and uncovers B from the left, shading 0.7 · 14–20 f · stories, "chapter 2", history · SFX paper · avoid Resolve "Page Curl" (cheap look).
- **TR-051 Camera dolly through an MG world** (`TR.dolly(tl, world, …)`). A preserve-3d world whose layers carry `data-z`. The camera travels `dz` px and layers fade 6 f before they pass the lens · 20–40 f `power2.inOut` · intro, "inside the AI", stacked concepts · SFX whoosh_soft (long) · HF only.
- **TR-052 Portal / zoom-through object** (`TR.portal`). A zooms about a screen/card rect until it fills the frame. B rides inside the rect from the start (exact same scale curve), with corner radius → 0 · 14–24 f `power3.inOut` · "open the app", "inside the prompt" · SFX whoosh_soft · Resolve: per-frame `z`+`tx/ty` spans for A only plus B as a picture-in-picture is too fiddly, so use a junction plate.

### Wipes & masks
- **TR-040 Edge wipe with bar** (`TR.wipe`, reference reel A). B is revealed by `clip-path: inset`, a 24 px bar in another palette colour rides the seam, optional 3 f peek, `power4.inOut`. Coverage per frame ≈ 2, 4, 11, 29, 67, 87, 96, 100 % · 7–9 f · MG→MG, panel changes, before→after (RTL) · SFX transition_swipe · Resolve: simple "Edge Wipe" (no bar).
- **TR-042 Cover wipe** (`TR.coverWipe`, plate). A stage-colour panel with bars on both seams crosses the frame and the hard cut hides under it · 8–12 f `power3.in` / `power3.out` · footage→footage section change · SFX transition_swipe.
- **TR-041 Iris from a UI element** (`TR.iris`, `o.at` = element or [x,y]). B grows from the send button, the caret, a dot in a letter, with a ring riding the edge · 8–10 f (`expo.in` like reference reel A with `soft:false`; `power3.inOut` by default) · prompt → result, "one idea" · SFX whoosh_soft (low) · Resolve: simple "Oval Iris" (no ring, centre only).
- **TR-046 Iris cover** (`TR.irisCover`, plate). A disc grows from a point to cover, the cut happens, then a hole opens from the same point (SVG mask, transform only) · 10–14 f · in/out of a full-frame cutaway from something in the speaker's frame (their phone, a logo pin).
- **TR-043 Doors / split panels** (`TR.doors`, plate). Two halves close on the centre, the cut happens, they open · 10–14 f · "two worlds", versus, entering the split stage · SFX impact_soft (low) · Resolve: simple "Barn Door"/"Split".
- **TR-044 Blinds** (`TR.blinds`, plate). 8 slats, 0.86 f stagger, close from the top and open to the bottom · 9–12 f · chapter change, page-turn feel when the grid continues across (reference reel A) · SFX transition_swipe · Resolve: simple "Venetian Blind".
- **TR-045 Colour bars** (`TR.bars`, plate). 3 palette bands sweep across 2 f apart, the cut happens, they sweep out · 10–14 f · brand chapter cards · SFX transition_swipe.
- **TR-047 Ink / liquid** (`TR.ink`, plate). Seeded blobs under a gooey filter grow from an edge, the cut happens, they recede · 14–20 f · creative, "ideas flow", art topics · SFX swoosh_reverse · Resolve alternative: a Mixkit or Envato ink matte with Composite "Alpha" (luma matte workflow, `craft/10`).
- **TR-048 Mosaic tiles / shatter** (`TR.tiles`, plate). Square tiles pop in by distance from a point with a slight seeded spin, the cut happens, they pop out · 10–14 f · tech, pixels, "rebuild" · SFX click_ui (low) · Resolve: Fusion "Mosaic Center Wipe" / "Shatter".
- **TR-095 Object pass** (`TR.objectPass`, plate). A phone silhouette (or `o.src` PNG: hand, card, the speaker's phone) crosses the lens at 125 % of frame and the cut hides behind it · 10–16 f `power2` · "on your phone", app topics; also the in-camera hand wipe when it is filmed · SFX whoosh_soft.
- **TR-060 Zoom into a letter** (`TR.typeZoom`). A word coloured like B's background scales ×60 about a point inside a stroke until it floods the frame · 14–20 f `power3.in` · the keyword is the door into the next scene · SFX whoosh_fast.
- **TR-061 Kashida wipe** (`TR.kashidaWipe`, plate; **our own**). The word pops, its kashida bar stretches R→L across the frame, thickens to cover (the cut), then collapses · 16–24 f · Arabic typographic chapter changes, "next" words (ثم / بعدين، الآن، الخطوة الثانية) · whole-word text, never split · SFX transition_swipe.

### Glitch / distortion (tech or error beats only)
- **TR-080 Glitch cut** (`TR.glitchCut`). Seeded x/skew jitter + contrast/hue every 2 f, hard swap on the cut · 6–8 f · AI fail, bug, hacking, "error" · never on emotional or premium beats · SFX glitch · Resolve: Fusion "Glitch" / "RGB Splitter" / "Block Glitch" 3–5 f.
- **TR-081 Glitch slices** (`TR.glitchSlices`, plate). Palette bars jumping every 2 f around a hard cut · 5–8 f · pair with TR-080.
- **TR-070 Ripple / heat wave** (`TR.ripple`). Displacement 0→60→0 peaking on the cut, 4 f crossfade · 12–18 f · dream, memory, "imagine…" · heavy on video, so prefer it on MG · SFX swell (very low) · Resolve: Fusion "Ripple Warp".

### Accents & MG-specific
- **TR-096 Shock rings** (`TR.rings`, plate). A ring expands 0.2→2 and fades · 6–10 f · lands a morph, an iris or a slam word · SFX pop (very low) or none.
- **TR-121 Push into colour** (reference reel A). A panel of the next stage colour pushes in, then the next metaphor builds on it · `TR.push` with B = colour stage.
- **TR-122 Headline carry-over.** The top headline persists across the transition and leaves last (reference reel A) · put the headline outside A/B so the transition doesn't touch it.
- **TR-123 Continuous grid.** The 90 px grid continues across the cut (inverted colour), so the wipe feels like a page turn, not a new world · build: grid on a layer above A/B, colour switched on the cut frame.
- **TR-124 Echo trail.** 3 ghost copies at 0.5/0.3/0.15 opacity, 1–2 f behind a moving object · fast MG moves without real blur · HF: duplicate elements with offset tweens.
- **TR-126 Caption-word hit.** On a key word, a 1.03 punch of the caption only plus a 2 f palette tint (no flash on the frame) · never more than 1 in 6 captions.
- **TR-127 Behind-speaker swap (our own; uses the speaker's matte).** The speaker stays put (matte layer) while the stage/background behind the speaker changes with any wipe from this list, so continuity holds through the transition · use: chapter change without losing eye contact · build: transition on the plate/stage track only, matte above · respects "nothing behind the speaker's back" only when the new background is the user's own plate or a colour stage, never cards.
- **TR-128 Park transition.** The speaker shrinks into the top half (split stage) over 27–30 f `ease_io` while the panel slides up · entering the split stage · baked in the MG segment, or LIVE Resolve `live.py camera` ty/z spans · SFX none.
- **TR-129 Lean-in dolly.** When the speaker leans toward the lens, continue the move with a 1.00→1.12 smooth push and morph into the full-frame cutaway · needs footage with the lean.
- **TR-130 Number roll.** The old number rolls up and out as the new rolls in (counter digits, Latin), 8–12 f `power3.inOut` · stats → next stat.

## 6. SFX pairing (quiet: −8…−12 dB under the voice, peak on the cut, clip start = cut − `peak_time_s` from `assets/sfx/manifest.json`)
| Family | SFX folder | Notes |
|---|---|---|
| whip, wipe, cover wipe, bars, blinds, kashida | `transition_swipe` | never the same file twice in a row |
| push, slide, portal, iris, object pass, dolly | `whoosh_soft` | low; skip on every 2nd list item |
| spin, speed lines, zoom into letter | `whoosh_fast` | hype only |
| card/mirror flip, page turn | `paper` | |
| doors | `impact_soft` | |
| ink | `swoosh_reverse` | |
| tiles | `click_ui` | very low |
| glitch | `glitch` | 1 per video ideally |
| burn, ripple | `swell` | very low |
| rings | `pop` | very low or none |
| zoom, blur cut, scale-in-place, morph, leak, colour flip, hard cuts | **none** | Default: no zoom whooshes, no shimmer, no flash crack |

## 7. QA per transition
1. It has a stated purpose (row in §3), sits on a sentence boundary or beat, and is not in the first 1–2 s.
2. Direction continues (RTL = forward), rotation keeps its sign, and peak velocity and blur sit on the cut frame.
3. Length is in spec (§1). Frame-step ±3 f: no black or transparent edges (3D, spin and cube need a stage colour behind), no wrong-clip flash.
4. Face visible while the speaker talks. Captions are not caught in a glitch or shake (put captions above the transition layer).
5. One family per video, the same preset ≤ 3×, at most 3–4 designed transitions per 60 s.
6. SFX ±1 f and quiet. No white anywhere (flash peak ≤ 0.4, palette colour).
7. Seeded: identical re-renders (`o.seed` fixed). `npx hyperframes@0.8.151 lint` gives 0 errors on the plate project.
8. On a phone at 1×: if you notice the transition before the content, cut its length or intensity by ~30 %.
