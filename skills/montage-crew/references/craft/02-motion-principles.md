# Motion-design fundamentals → GSAP @30 fps

Research: 26 transcripts + 4 contact sheets + 6 web sources. Ben Marriott (×7), Jake In Motion, MotionXP, Motion By Scott, Joshua Craigie, Envato Tuts+, Nowack Design, Alex Grigg (×2), olly, Stephan Zammit, SonduckFilm (×2), Blaze Pate (Apple), School of Motion; NN/g, Material 1/3, Val Head, Derek Lieu, GSAP docs. `[src]` = stated by a source, `[synth]` = our conversion.

## Principles (ranked)
1. **Custom easing/spacing > everything** (12+). Timing = how long; spacing = where in-betweens fall. Default easy-ease is a starting point; linear = robotic. The eye reads acceleration as force/mass.
2. **Anticipation** (7): small opposite move first — directs the eye, signals energy; 3 hold frames sell a move; wind-up can be 3× the main move; can live on another property.
3. **Hierarchy of motion — don't move everything** (6): motion promotes. Lead the eye to where the next element appears. Stillness makes intensity land.
4. **Follow-through / overlap / offsets** (6): nothing stops at once; paired layers offset 5–10 f; overshoot + settle.
5. **Secondary action** (5): rings, particles, a reacting neighbour, camera nudge.
6. **Block first, polish later** (5): poses as holds → breakdowns → easing.
7. **Design first** (5).
8. **Transitions hide changes at peak speed** (4): ease out of A, max velocity at the cut/swap, ease into B.
9. **Consistency / one motion personality** (3): Apple = same curves everywhere.
10. **Arcs, squash & stretch, weight** — in moderation.
11. **Restraint with effects** (4): no motion blur by default in 2D, no wobble everywhere.

## AE curve → GSAP
| AE / description | GSAP | cubic-bezier |
|---|---|---|
| Easy ease (33 %) | `sine.inOut` / `power1.inOut` | (0.33,0,0.67,1) |
| Pulled S-curve 70–90 % ("pro") | `power3/4.inOut`, `expo.inOut` | (0.7,0,0.1,1) / (0.87,0,0.13,1) |
| First handle vertical (impact rings, morph spike) | `expo.out` | (0.16,1,0.3,1) |
| Strong ease-out in, snappier ease-in out | `power3.out` / `power2.in` | — |
| Material standard | ≈ `power2.inOut` | (0.4,0,0.2,1) |
| Material enter / exit | `power2.out` / `power2.in` | (0,0,0.2,1) / (0.4,0,1,1) |
| M3 emphasized-decelerate (premium enter) | ≈ `expo.out` | (0.05,0.7,0.1,1) |
| Accelerate into a cut | `expo.in` / `power4.in` | (0.7,0,0.84,0) |

## Durations
| Element | Frames | s |
|---|---|---|
| Micro (tick, icon pop, dot) | 3–6 | 0.1–0.2 |
| Small enter (badge, icon, word) | 6–10 | 0.2–0.33 |
| Exit | 5–8 (≈20 % shorter than enter) | 0.17–0.27 |
| Medium move (card, panel, headline) | 10–15 | 0.33–0.5 |
| Large / full-screen | 15–24 | 0.5–0.8 |
| Overshoot settle | +3–4 | |
| Elastic | keys 6 f apart: 120 → 95 → 102 → 100 | |
| Anticipation | 3–8 (up to 3× main for drama) | |
| Scene transition | 10 before + 10 after cut | 0.67 |
| Impact ring | ~20 | |
| Morph | fastest 3 f in middle of 8–15 f | |
| Hold after resolve | ≥ 0.75–1 s (+ reading time) | |

## Overshoot / anticipation / stagger
- Scale pop 0→110 %→100 % (+4 f) = `back.out(1.7)` (~10 %). Premium `back.out(1.1–1.2)`; playful `back.out(2.5)` / `elastic.out(1,0.4)` — elastic never on body text.
- Position overshoot 1–3 % of travel.
- Anticipation: pull back 5–15 % of travel (or −10…−15°), then fire: `tl.to(el,{x:-20,duration:.2,ease:"power2.inOut"}).to(el,{x:600,duration:.35,ease:"expo.out"})`, or `CustomEase "M0,0 C0.3,-0.15 0.3,1 1,1"`.
- Stagger: letters 1–2 f · words 2–4 f · list/cards 3–5 f · blocks 5–10 f · cap total ~0.5–0.6 s (`stagger:{amount:.5}`). `from:"start"` reading order, `"center"` symmetric, `"edges"` collapse. Overlap chained tweens (`"-=60%"`).
- Motion blur: off for flat 2D; on for whips (directional blur ~100 only around peak frames), objects crossing > 20 % frame in 1–2 f. HTML: SVG `feGaussianBlur stdDeviation="X 0"` ramped 0→peak→0, or render 60 fps and frame-blend (`tmix`) to 30.

## Personalities
| | Snappy / energetic | Smooth / calm | Premium / luxe |
|---|---|---|---|
| Enter ease | `expo.out`, `power4.out` | `power2.inOut`, `sine.inOut` | `expo.out`, (0.16,1,0.3,1), (0.22,1,0.36,1) |
| Duration | 6–12 f | 15–24 f | 18–30 f |
| Distance | 100–300 px + scale | medium | 20–60 px, scale .96→1, blur 8→0, opacity |
| Overshoot | back 1.7–2.5 + anticipation | none | none / back 1.1 |
| Stagger | 2–3 f | 4–6 f | 4–8 f, long overlap |
| Holds | short, beat-cut | medium | long — stillness is a feature |
| Transitions | whip, zoom-through, spin + blur | crossfade, slide, soft wipe | match cut, mask reveal, slow push 1→1.05 per shot |
Premium = one ease family, small distances, no bounce, perfect alignment, slow camera drift, fewer moving things.

## Kinetic typography
- Reading: 3–4 words/s; hold ≈ chars/12 + 0.5 s AFTER the build (7-word line → 1.8–2.5 s). +30–50 % for stylised type/second language.
- Build word by word for sentences (x:50 or y:20–40 + opacity, 8–12 f, `power3/expo.out`, 2–4 f stagger or synced to word timestamps). Letter-by-letter only for hero words ≤ 12 chars (Latin), `yPercent:100` inside overflow mask.
- Drift the line to stay centred while it builds. One emphasised word per line (scale 1→1.1→1, colour, weight, underline).
- Exit ≈ 70 % of entry duration, `power2.in`, mirror the entry or match-move into next scene.
- Never move text while it must be read (≤ 1 %/s drift OK); no elastic on body copy; don't pop the next line before the hold ends.

## Transitions
| Type | Recipe | Params |
|---|---|---|
| Match cut | out: scale 1→1.05 `power3.in`; in: 1→1.05 `power3.out`; direction continues | 3–5 % max; 8–12 f each side |
| Speed-ramp cut | property at peak velocity on the cut frame | |
| Whip / tile slide | A out, B in same direction, blur ramp | 10+10 f, blur ~100 on travel axis, `expo.inOut` |
| Zoom-through | A 1→2 + radial blur 0→100 `expo.in`; B .5→1 `expo.out` | 10 f each |
| Spin | 0→180° at cut, →360° after, radial blur peak on cut | 10+10 f |
| Shape/mask wipe | clip-path grows from hero element; lead with 2nd colour shape offset 2–4 f | 12–18 f `expo.inOut` |
| Morph | designed in-between blob, matched first vertices, swap at fastest frame | 8–15 f, hold ~0.75 s |
| Hero carry-over | last element of A becomes container/bg of B (FLIP) | 15–24 f `power3.inOut` |
| Hidden cut | cut when frame is filled (colour block, object near lens) | 1–2 f |
Continuity: exit right → enter from left; new focal point appears where the eye already is; loops end on first frame.

## Idea bank
hold-key blocking · opposite-direction anticipation 3–6 f · cross-property anticipation (rotate −10° before move) · overshoot 110→100 +4 f · decaying elastic 120/95/102/100 · impact rings (stroke circle ×3–4, fade over 20 f `expo.out`) · impact squash 100→70→20 % · gravity fall `power2.in` 10 f + 3 f settle · invisible-wall bounce (no ease on contact key) · swap at peak speed · morph through blob · circle↔rounded rect via border-radius · animate size not scale for stroked shapes · fade with colour · offset pairs 5–10 f · stagger from centre · wrapper-null drives cluster · parallax loop (copy at 75 % slower) · spinners · micro-shake 12 Hz 1 px + scale 1.01 · reactive light/shadow · match-cut push · 10+10 f whip/zoom/spin · eye-lead · keyword-only emphasis · line-drift centring · Ken Burns 1→1.04–1.06 · stillness beat 0.5–1 s before payoff · neighbours nudge 2–6 px / 2–4° when hero lands · misregistration 2–4 px retro · loop closure · hide cuts in full-frame wipes.

## Mistakes
default/linear ease everywhere · everything moves · same duration/ease for all · everything stops at once · wobble/squash overuse · motion blur everywhere · off-centre alignment · polished intro, rushed rest · trendy trick that doesn't fit · scaling stroked shapes · morph point-order errors · random spacing · text moving while read / too short · transition peak not on the cut.

## QA per scene
1 stepped key poses tell the story · 2 exactly one attention point at a time, each move leads the next · 3 hierarchy by motion size/order · 4 no linear on organic moves; enters `out`, exits `in`, moves `inOut`; one ease family · 5 durations in table; exits shorter; nothing important < 6 f · 6 overlap 30–60 % · 7 settle on hero landings · 8 anticipation on major moves · 9 secondary action on impacts · 10 transition peak on cut, direction continues · 11 text hold ≥ chars/12+0.5 s, ≤ 1 emphasised word · 12 ≥ 1 rest beat per 5–8 s · 13 pixel-exact alignment · 14 only transform/opacity (+clip/filter when needed), round final values, scrub for 1-frame pops · 15 clean first/last frames · 16 same ease tokens, stagger unit, distance scale across scenes.
