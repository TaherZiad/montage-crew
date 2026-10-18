# Motion graphics on talking-head video — technique catalog

Research: 22 transcripts (19 EN, 3 AR) + 15 contact sheets + 4 web. Joseph|Video Editing (Hormozi, Iman Gadzhi ×3, Devin Jatho, SaaS, Ali Abdaal, IG talking head ×2), TomsProject (Hormozi, Ali border, Kallaway), Istvn, Usman Explains, Simply Put (podcast motion reels), VerticDesigns (3D tracking), bentomotion (Apple Liquid Glass), Editing Empire (screenshots), Mihai (lower thirds), Hudayfa Luai (AR glass reels, 92K), Muhamd Helal (AR, "90 % is the shoot"), Abdelrahman Ibrahim (AR course); HyperFrames caption docs, safe-zone guides.

**Global motion grammar**: entrances 10–15 f `power3.out`/`expo.out`; exits 8–10 f `power2.in`; camera moves `expo.inOut` ("steep mountain"); pops `back.out(1.7)`/elastic for bouncy UI; stagger 2–4 f per word/item, 1 f for grid waves; never linear; blur on fast moves.

## 1. Text behind subject (matte sandwich)
- Earned peak: hook or single climax word per section; 1–2 per video. Never for running captions.
- Layers: video → (optional blurred vignette: video copy `blur(10px) brightness(.55)` masked `radial-gradient(ellipse 55% 45% at 50% 40%, transparent 60%, #000 100%)`) → text → subject RGBA matte → captions/UI → grain.
- Word spans 80–95 % W (240–360 px condensed/serif); baseline at 28–38 % H so the head overlaps 10–25 % of the letters.
- Motion: text y +80→0, scale 1.15→1, blur 14→0, opacity 0→1, 14 f `expo.out` (letter stagger 1.5 f for Latin serif). Simultaneously `#cam` scale 1→1.06, y 0→−30 over 20 f `expo.inOut`, peaking as the text lands. Exit opacity→0, y→−40, 8 f `power2.in`.
- Matte edges feather ~0.6 px; if edges chatter hold < 2.5 s. Cards/icons behind shoulders use the same sandwich.

## 2. Fake 3D tracking in 2D
- Locked-off talking head → fake the plane: parent `perspective:1400px`, element `rotateY(-22deg) rotateX(6deg) translateZ(-200px)` + drop-shadow in wall colour.
- Moving camera → per-frame offset from matte bbox centroid or ffmpeg vidstab transforms × parallax factor (0.6–0.8 background plane, 1.0 on subject).
- Handheld realism: sum of two sines ~1 Hz, 3–5 px, ±0.3° rotation (AE `wiggle(1,5)`).
- Push-parallax depth multipliers: bg ×1.0, text-behind ×1.03, matte ×1.05, fg UI ×1.10 from one `progress` tween.
- 3D extruded tiles (Ali Abdaal): side face via pseudo-element or 6–10 stacked `translateZ` copies, edge highlight sweep, enter rotateX 60→10, rotateY −30→−12, y +200→0, 18 f `expo.out`, then float.

## 3. Glassmorphism (bentomotion recipe)
```css
.glass{background:rgba(255,255,255,.12);backdrop-filter:blur(18px) saturate(140%) brightness(1.08);
border:1px solid rgba(255,255,255,.35);border-radius:40px; /* 30–70; pills 999 */
box-shadow:inset 0 1px 0 rgba(255,255,255,.55),inset 0 0 24px rgba(255,255,255,.10),0 24px 48px rgba(12,20,60,.35);} /* tinted shadow, never pure black */
```
- Refraction: copy of the video inside the panel clip at scale 1.08 + blur 18; "liquid" rim via SVG feDisplacementMap (scale 20–35) from a blurred white-stroke map.
- Rim lights: 1 px white 20 % + 6 px border blurred 4 px at 40 % screen; diagonal top-left highlight.
- Liquid bounce entry: height 0→H in 3 f, width circle→W over 4 f from f2 `back.out(2)`/`elastic.out(1,.5)`, y +20→0; inner text blur 20→0 + opacity 10 f from f4.
- Arabic variant (Hudayfa Luai): half-circle glass rises from bottom (100 % W, top edge ~62 % H), content = video blurred 22 px, 2–5 px tapered white stroke, words rise inside staggered by word, panel 14 f `expo.out`.
- Use for premium/Apple/SaaS/tech, lower thirds, definition cards, legibility over busy video.

## 4. Icons & UI cards beside the speaker
- One card 28–40 % W; icon trio 120–160 px circles; radius 30–60 px. Free side of head at 18–40 % H or chest band; or behind shoulders.
- Items stagger 4–6 f: y +60→0, opacity, rotate −6→0, 12 f `power3.out`; exit reverse 8 f `power2.in` stagger 3 f. Bouncy: scale 0→1 `back.out(2.2)` 10 f.
- House presets: 2-tone accent gradient fill; long soft shadow `drop-shadow(-18px 24px 30px rgba(0,0,0,.35))`; light sweep `::after linear-gradient(105deg,transparent 40%,rgba(255,255,255,.45) 50%,transparent 60%)` translateX −120→120 % over 22 f `power2.inOut` screen; subtle deep glow `drop-shadow(0 0 18px accent@.45)`; one icon family, white + one accent hero icon.
- Curiosity: cards pixelated + `saturate(.5) brightness(.6)`, clear on the reveal word.

## 5. Callouts
- Highlighter box: accent rect behind word, pad 8–14, radius 6–10, `transform-origin:left; scaleX 0→1` 8 f `power3.out`, starts 2 f before the word.
- Underline/circle draw: SVG dashoffset length→0, 12–18 f `power2.out`, stroke 6–10 round caps; hand-drawn fonts or wobbly paths.
- Dashed connectors `stroke-dasharray:14 12` + marching dashoffset.
- Arrow wipe: `mask-image: linear-gradient(90deg,#000 45%,transparent 55%)`, mask-size 250 %, position 100→0 % over 10 f.
- Kallaway guide line: glowing path draws 30–45 f; each pill's bright outline fades in 4 f when the tip arrives; group pans down `expo.inOut`.
- Arrows point toward (not onto) the face; label on the far side.

## 6. Lower thirds
Name bold 44–56 px (optionally `mix-blend-mode:difference`), role thin 26–32 px 70 %; glass or none; x 60 px, y 64–72 % H. Per-char x +20→0, rotate 8→0, letter-spacing .3em→0 (Latin), stagger 1 f, 14 f; backing scaleX 0→1 from left 10 f starting 3 f earlier; hold 2.5–4 s; exit 8 f. Summarise to ≤ 5 words — don't transcribe.

## 7. Typography system
- Two styles per video: **simple** sans white (#FFF→#D9D9D9) + soft shadow `0 4px 12px rgba(0,0,0,.35)`; **special** serif/heavy with accent gradient + glow + light sweep, 1.6–2× simple.
- Word reveal preset: y +30→0, blur 10→0, opacity, fill flashes accent then settles white; stagger 3–6 f `power3.out`; optional quantise to 15 fps ("cinematic" stepped).
- Captions 2–3 words, y 50–58 %, ≤ 28 chars, ≥ 48 px (target 64–80); colour-coded keywords; emoji 90–120 px sparingly.
- One read at a time: hide captions during hook box/title/list.
- Hook box (IG-native): top band 14–26 % H, black text on white rounded box (radius 14, pad 10/18), 1–2 lines + emoji, 1.5–2.5 s, scale .9→1 6 f.

## 8. Speaker-in-a-card / zoom-out reveal
- Canvas flat/paper (#E9E6E1, off-white, navy); video `scale(.5–.62)` in rounded rect radius 60–75, white border card 105 %, `drop-shadow(0 20px 40px rgba(0,0,0,.18))`; words laid out around the card in a loose grid, key word 2× in a gradient sampled from footage, mixed fonts per word; small outline shapes drift.
- Out-of-screen zoom-out: `#cam` 1→0.70 over 15 f `expo.out` onto solid canvas, text in new margins; back in 12 f `expo.inOut`.
- Never a dead frame: `#cam` 1–3 % slow scale, scene pans `expo.inOut` 20–30 f; match cut by scaling a shape to fill the screen; playful head wobble ±3° 1 s period.

## 9. Full-screen MG takeover
- Backgrounds: dark premium #0B1026 + 3 blurred blobs (blur 120 px at 1080) drifting/morphing at 0.4–0.5 Hz; 1 px grid 6–10 % with radial fade; pastel SaaS blobs.
- Always mono grain 3–6 % (feTurbulence baseFrequency .8, re-seeded per frame) + optional vignette.
- Content: centred text, one 3D object PNG with long radial shadow 35 % + blurred depth copies, consistent AI illustration scenes, camera flying across one big canvas.
- In/out: blur whip (blur 0→40→0, x ±300, 10 f, whoosh at peak blur) or zoom-through a shape.

## 10. Screenshots / tweets / charts / UI — rebuild, don't paste
- Rebuild in HTML with real fonts; animate parts: avatar `back.out`, name types, numbers count up (`gsap.to(o,{v:target,snap:{v:1},duration:1.2,ease:"power2.out"})` + K/M suffix), button press 1→.92→1 6 f, cursor curved path 18 f `power3.inOut` + click ripple.
- Real screenshot: slice into pieces, stagger in; or tilt `perspective 1200px rotateX(18deg) rotateY(-14deg)` drifting flatter over 3 s with far-edge DOF blur.
- Reveals: brush/ink luma matte, page turn, FOV zoom 1.3→1.
- Charts: bars scaleY from bottom stagger 3 f 14 f `power3.out`; line draw 24 f; final value highlighted + glow.
- Calendar: grid lines trim-path offset, numbers 1 f wave stagger, event card slide + cursor click.

## 11. Sticker / cut-out (Ali Abdaal, Hormozi long-form)
- Subject matte `grayscale(1) contrast(1.1)`, 6–10 px white/neon (#39FF6A) outline (8 stacked drop-shadows or feMorphology dilate), glow, on crumpled/dark paper + dust.
- Mystery: black silhouette `brightness(0)` + neon outline + big "?" → real person on the name.
- Flanking stats either side of torso (180–240 px condensed, yellow/red), slide from own side 10 f `expo.out`.
- Paper tear: mask points stepped every 2 f + paper SFX. Objects pop from behind the back y +200→0 12 f `back.out`.

## 12. Finish
Glow subtle (`text-shadow:0 0 6px accent@.6, 0 0 30px accent@.35`); global glow = blurred copy 40 px screen 8–15 %; light leaks/halftone on B-roll/backgrounds (not face) 30–60 %; grain 3–6 % over everything incl. graphics; vignette 20–35 %; chromatic aberration 1–2 px only on glowing display text; palette derived from the set's practical light.

## 13. Sound mapping
Moves/cards/camera → whoosh at peak velocity · UI/icons → pop/ding · text → soft click/tick · typewriter → typing · paper → paper · photo blur → shutter · Hormozi style → game SFX + trending music ducked.

## GSAP skeleton
```js
const f=n=>n/30, tl=gsap.timeline({paused:true});
tl.from(".w",{y:30,filter:"blur(10px)",opacity:0,color:"#FFB36B",duration:f(12),ease:"power3.out",stagger:f(4)},f(0))
  .fromTo("#cam",{scale:1},{scale:1.06,y:-30,duration:f(20),ease:"expo.inOut"},f(6))
  .from(".hl",{scaleX:0,transformOrigin:"left center",duration:f(8),ease:"power3.out"},f(10))
  .from(".card",{y:60,opacity:0,duration:f(12),ease:"power3.out",stagger:f(5)},f(24))
  .to(".card",{y:40,opacity:0,duration:f(8),ease:"power2.in",stagger:f(3)},f(120));
```

## Layout (1080×1920, 9:16)
- 16:9 (1920×1080): keep text inside x 96–1824, y 54–1026; nothing important in the bottom 140 px (player controls).
- Safe: superseded by craft/09 §3 (top 290, bottom 1480, 190 px both sides for y 700–1480).
- Bands (eyes ≈ 30 % H): 12–26 % hook/titles/text-behind-head · 22–45 % face — nothing opaque on eyes/mouth; side gutters ≤ 35 % W for icons · 50–62 % captions/titles · 62–74 % lower thirds, glass half-panels, CTA pills · > 77 % clear.
- Density: 1 focal + ≤ 1 supporting; sets of max 3; one read at a time; new idea every 3–7 s; graphics 30–50 % of runtime in "motion" styles, < 10 % in text-only styles.
- Elements enter from the side the speaker faces/gestures, move away from the face.
- Tight footage → shrink speaker into a card, zoom-out to 70 %, or full-screen MG. Advise the creator: shoot wide, subject 2.5–3 m from the wall, coloured light on the wall (Helal).
- Depth: bg plate → blurred vignette → behind-subject graphics → matte → captions/UI → grain. Something always moves (camera drift 1–3 %, floats ±4 px).

## Asset choice
Icons (one family) → abstract concepts, lists, features · photos (desaturated, key object in colour, circle/rounded mask) → concrete nouns, examples, social proof · 3D object → the one hero noun per section · rebuilt UI → proof (tweets, profiles, dashboards, search, calendar) · AI illustrations (consistent style) → metaphor/story beats · B-roll → situations, hide cuts · textures (paper, grain, leak, halftone) → always, low opacity.
Consistency kit per client: 3–4 hex (60-30-10 from set lighting), 2 fonts + 2 text presets, one radius family (30–70), one shadow/glow/light-sweep preset, one entrance/exit preset, one SFX library with fixed event mapping → encode as CSS tokens + 5–6 GSAP preset functions.

## Idea bank (content → MG)
Stat: count-up behind speaker + highlighter on unit · two flanking stats · glass-pill ratio bars · ring/donut draw around icon.
List: 3 icon circles lit when named · Kallaway guide line lighting pills · triangle bullets by word.
Process: dashed path between numbered nodes on grid + camera flies · calendar wave + event card + click.
Comparison: split red ✕ / green ✓ cards, loser desat → 0.9 · before/after card wipe with divider · B&W photo → colour on "after".
Quote: full-screen serif italic + giant 10 % quote mark · rebuilt tweet with counting likes.
Question/hook: IG hook box 2 s · silhouette + "?" reveal · giant "?" behind speaker + push.
Warning: red glass pill "❌" + x shake ±6 px 6 f + red vignette pulse 15 % + buzz · strike-through hand-drawn line.
Tip: highlighter under rule word + lightbulb icon pop.
Definition: glass half-panel with serif term + thin definition.
Product: liquid-glass app tile bounce + 3 feature icons · recreated UI demo with cursor, fanned in 3D.
Social proof: 3 pixelated reel cards clearing on "results" · recreated profile header, followers count up, Follow pressed.
Money/growth: line chart up + coin pop at peak. Time: clock + light sweep + countdown.
Emotion/story: full-screen AI illustration scenes, camera flies between 3. Name: lower third (difference blend) at 66 % H. Location: perspective text on wall during B-roll. Chapter: zoom-out to 70 % with title in margins. Emphasis word: matted behind head + push + whoosh. Two traits: speaker card on paper, traits in different fonts. Cause→effect: icon A → arrow wipe → icon B, match cut. CTA: pill button press with cursor, "comment X" in top band.

## Amateur tells
matting every caption · graphics not tied to script · two reads at once · covering face / UI zones · text crammed in pills, sizes changing card to card · non-uniform scaling · linear, identical timing, no stagger/blur, slow exits · dead frames · harsh glow, pure-black shadows · mixed asset styles, > 2 fonts · raw screenshot with basic tilt · bad roto edges held long · tight framing with no room · no SFX / misaligned SFX · verbatim long lower thirds · copying a template 1:1 · emoji overload.

> Default: every recipe here that puts text in a pill/card/dark box is superseded by craft/09 (soft text only), unless the brief, the profile or the user's `rules.md` says otherwise.
