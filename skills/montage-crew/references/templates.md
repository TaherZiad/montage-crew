# Template catalog — exact parameters

30 fps. `f` = frame (0.0333 s). Sizes: % of H (1920) / W (1080). Helper names refer to `assets/rtl-kit.js`.
Eases (GSAP): quart.out = `power3.out`, expo.out = `expo.out`, back = `back.out(1.4)`.

## Text

### T-KASHIDA — the signature (Yellow Neon / Pink Palace looks)
Font 700–900, 6 %H, accent colour. `kashida(word, n)` inserts n×ـ between two joining letters.
- f0–6 head wipe RTL + rise 12 px · f4–16 kashida grows 0→n (`kashidaGrow`) · f14–22 tail lands. Optional f40–70 shrink to 60 %.
- Subline 300 weight, 2.8 %H, words +3 f each from f18.
- Helper: `kashidaIn(tl, el, t, {n:6})`.

### T-GLOW-TITLE (Espresso Glow)
Alexandria 800, 9–12 %H, `#F9E2CA`, `text-shadow: 0 0 12px rgba(249,226,202,.8), 0 0 60px rgba(231,184,148,.45)`; at y 8 %.
In: RTL wipe with scale 0.4→1 from bottom + blur 8→0, 6 f back.out(1.4) (≈2.5 f per letter visual). Subline weight 200, 2.6 %H, types from f5. Hold: group scale 1→1.04.
Hero variant (torso, 13–15 %H, bloom 30 px 60 %): scale 0.3→1 then 1→1.08 over hold, + glass pill from f20.

### T-NEON-PAIR (Blue Neon look)
Lead: 700, 2.8 %H, #FFF, glow 8 px .35. Keyword: 800, 6 %H, fill `linear-gradient(180deg,#6FA8FF,#3A86FF 55%,#2F6BFF)` clipped to text, `filter: drop-shadow(0 0 10px #2F6BFF) drop-shadow(0 0 28px rgba(25,55,205,.8))`. Gap .15× keyword. Centre y 55 %.
Word in: opacity 0, blur 12, y +12, (keyword scale 1.1) → rest, 5 f power3.out. Out: blur 10 + fade 3 f, overlap next pair 1–2 f. Keyword-swap variant: lead stays, keyword blur-crossfades 3 f. Helper: `wordsIn`.
Add a permanent bottom gradient `#0B131F` 0→.95 from 60 %H to 100 %.

### T-NEON-YELLOW (Yellow Neon look)
Black 900, 6 %H, `#F7D100`, `text-shadow: 0 0 4px #FFE45C, 0 0 18px #FFC400, 0 0 40px rgba(255,170,0,.6)`, kashida.
Variants: (a) drop y −120 %→0 12 f expo.out (combine with camera zoom-out) · (b) blur-pop scale 1.4→1 blur 12→0 7 f · (c) hard pop 1 f + glow 1.6→1 over 4 f.
Neon tube variant: white core `#FFFDF0`, halo `0 0 6px #FFF, 0 0 22px #F7D100, 0 0 48px #FF9F00`, glow ramps 12 f.

### T-SLAM (Teal Eco)
17 %H; first letter gradient accent, rest white→grey. scale 1.8→1, opacity .3→1, 15 f expo.out, on a zoom-out frame. Speaker matte above it.

### T-WORD-STACK (Pink palace)
After punch-in (speaker to x 62 %W): column right edge 45 %W, top 18 %H; first word 9 %H, rest 4 %H. Each word on its timestamp: opacity, y +10 px, blur 6→0, 5 f.

### T-COUNTER
0→N over 19–45 f `expo.out` (integer rounding), font shrinks 45→27 %H (hero) or fixed 13 %H skewX −10° (stat). Unit word kashida-justified to number width, RTL wipe 8 f at f10. Tick SFX loop. Helper: `counter`.

### T-VERTICAL-ARC (Yellow Neon look)
SVG arc (r≈W, 1.5 px, white 50 %) rotates 30° in, 10 f; region inside blurred 6 px + warm tint. Two 90°-rotated columns on the edge (yellow + white); kashida draws upward 14 f then letters fade; col 2 +4 f.

### T-TRACK-COLLAPSE / T-BASELINE-POP (Latin)
Collapse: letter-spacing .6–.8em→0, 15 f power3.out, letters fade 1.5 f apart (for Arabic use per-word x only). Baseline pop: per letter scale 0.2–0.3→1 from bottom, 6–8 f back.out(1.3–1.6), 2–3.5 f stagger L→R. Helpers: `trackCollapse`, `baselinePop`.

### Outline doc titles (Outline Doc look)
Anton 150–175 px `#FFFBF0`, `text-shadow: 5px 7px 2px rgba(58,39,35,.7)`; per word opacity/blur 10→0/scale 1.12→1, 6 f, 4 f stagger; post-settle drift −48 px over 24 f sine.out.

## Containers

### C-GLASS-PILL
70–75 %W × 5–9 %H, radius 999, `backdrop-filter: blur(12px)`, fill `rgba(30,16,14,.55)` (tint to look), 1–1.5 px border `rgba(255,235,220,.18–.55)`. In: opacity + scale .9–.95→1, 6–7 f. Text 300–400 weight 2.5–3 %H types RTL. Empty-pill-first variant: pill 15 f before keyword.

### C-FROSTED-ARCH
Round-top (Espresso) or round-bottom (Navy) shape running off frame edge; 60 %W corner or 65–90 %W centred; `backdrop-filter: blur(18–24px)`, fill `rgba(40,22,20,.35)`, border 1.25–1.5 px `rgba(255,235,220,.35–.45)`. In: translateY +45 % (or X +60 %) → 0, 7–12 f expo/quart.out + whoosh. Content from f4–10: headline 800 5–7 %H letters RTL, lines 400 2.4 %H 5 f apart.
Dual-arch variant: A hangs top-left (flipped), B bottom-right, B +2 f, vertical 90° text inside.

### C-LIQUID-TAG (Navy)
33 %W × 5.2 %H, radius 999, fill `#02172B`, `box-shadow: inset 0 0 0 3px rgba(255,255,255,.85), inset 0 2px 6px rgba(255,255,255,.6), 0 6px 18px rgba(0,0,0,.35)`, anchored right bleeding 8 % off frame beside head. In from (+10 %W, −8 %H) scale .9→1, 10 f. **Word swap**: old y 0→−60 %, scale →.6, fade 8 f in; new y +60 %→0 scale 1.3→1 10 f back.out(1.2), overlap 3 f. Helper: `wordSwap`.

### C-DARK-NAME-PILL (Teal Eco)
86 %W × 24 %H (of panel), radius 22 %, fill `#061312F2`, rim `box-shadow: -2px 2px 0 #3CC8DC, 0 12px 30px #0008`, rotate −8°. In from (x +60 %, y +10 %, −25°, .8) 10 f back.out(1.4); old text → opacity .4 grayscale .6 scale 1.08 over 10 f (`pushBack`). Hold drift −8→−3°. Out blur 10 + fade 8 f.

### C-GLASS-SLAB + ICON (Navy)
0–40 %W full height, blur 14 px, white 4 %, 2 px right border 70 %. In x −100 %→0 14 f expo.out while speaker layer shifts +8 %W over 20 f. Icon from f8: rotate −60→0, scale .6→1, 18 f back.out(1.4). Word list 3 × 4 %H white 35 % drops in 8 f apart.

### C-GLASS-TRANSCRIPT (Teal Eco)
Panel x 5–40 %, y −2–62 %, cyan gradient `rgba(40,190,235,.45)→rgba(20,120,170,.15)`, 2 px `#6FE6FF`, glow 12 px. In clip `inset(0 0 100% 0)`→0 10 f. Words right-aligned 1–2/line 3.5 %H: opacity + blur 6→0 + brightness 1.6→1, 4 f on timestamp. Avatar 36 %W ring 3 px `#29B6E8` rolls in (x +60 %, rot 90°) 10 f.

### C-3D-EDGE-CARD (Yellow Neon look)
White face `#F6D1A6`/#FFF, radius 16, `transform: perspective(800px) rotateX(15deg) rotateZ(-8deg)`, `box-shadow: 0 18px 0 #E06A00`. In: flip up rotateX 60→15°, y +40 %→0, 10 f back. Text types word by word.

### C-STACK-LIST (Yellow Neon look)
≡ icon + 3 white bars radius 12, h 4 % card, widths 45/40/60 %, glow `0 8px 20px #FF8A00`. Build bottom→top 3 f apart, scaleX 0→1 from centre 5 f + glow flare. Labels type 1 char/f. Exit reverse: un-type, bars→15 % pill→dot, 20 f power2.in.

### C-GLASS-CALLOUT (Pink palace)
70 %W, y 58 %H, radius 12, `rgba(135,48,100,.72)` blur 18, 1 px border .25, gloss `linear-gradient(135deg,rgba(255,255,255,.35),transparent 40%)`. Pop scale .2→1 7 f `back.out(1.7)`; text word by word; height grows 8 f per new line.

### C-OUTLINE-BARS + HUD (Outline doc)
Bars 32 px, x 29–91 %W, flat colours hook #FD0000 lead #FEC928 body #3291C4/#166AE4/#1E3BE0 cta #00F913; scaleX from left 8 f, line 2 +2 f, label blur-in +5 f; stack scrolls one item 8 f. Behind matte. HUD over chest (64–78 %H): tabs 12 px cream, fill = playback progress, rings pop at open loops. In front of matte.

## Depth
- **D-NUMERAL-BEHIND**: white heavy numeral 30–40 %H centred on speaker, bottom at knees. Slam (.8→1.6 in 6 f, →1.0 by f15) / drop (−120 %H, `cubic-bezier(.34,1.56,.64,1)` 9 f) / fade (.92→1, 13 f). Layer under matte.
- **D-GHOST-TEXT**: outline letters 20–25 %H, `-webkit-text-stroke: 2px`, 8–12 % opacity, fade 12 f, slow drift.
- **D-FG-BLOBS**: 2–3 blurred shapes (brand-tinted), blur 30–60 px, .6–.9 opacity, drift 2–4 %W/s + rotate 3°/s, from corners. Orange-tile variant: 40–55 %W rounded squares gradient, blur 18–24, fly in 12 f expo then drift/tumble.
- **D-3D-UI-CARDS**: extruded cards (`#7A4A40`-type tint of accent), rotateX 15° rotateZ ±25°, cropped off top corners behind speaker; enter 24 f quart.out stagger 4 f; serpentine SVG line draws 45 f, toggles pop when reached; bokeh 6–10 dots rising.
- **D-BEHIND-PLATE**: hex grid / circuit HUD between footage and matte, 6 f in, flicker ±15 %, ~1 s.

## Camera & transitions
- **X-PUNCH**: cut: alternate scale 1.0 / 1.55–1.85 anchored (50 %, 42 %). Animated: `punch(tl, cam, t, {to:1.85, dur:.5})` power2.inOut; zoom-out `.2–.3 s expo.out`. Foreground graphics scale ×2.5 + fade during push-in.
- **X-PUSH**: within shot scale 1→1.06 linear over the shot (last shot reversed 1.08→1).
- **X-BLUR-CUT**: blur 20/40/20 px on frames t−1,t,t+1 + incoming punch 1→1.06 12 f. Whoosh on ~1/3 cuts.
- **X-SILHOUETTE-FLASH**: last 2–3 f before cut, matte filled #FFF (`filter: brightness(0) invert(1)` on matte layer).
- **X-WHIP-SCROLL**: group y 0→−600 px 8 f power2.in + vertical blur + 3 ghosts; hard cut; whoosh −4 f.
- **X-FLASH/LEAK**: white wipe 2 f + RGB split ±6 px; cyan bloom 5 f up/3 f down; film burn screen-blend 3+2 f.
- **X-ZOOM-INTO-LETTER**: type group scale 1→4 into a letter's counter 5 f power2.in → cut.
- **X-CIRCLE-WIPE** (outro): cursor path 20 f → click squash → `clip-path: circle(0→130vmax)` 20 f inOut, blurred gold-tinted footage inside, ring ripple.

## Outro
- **O-BRAND-LOCKUP**: name letters baseline-pop, tagline RTL word type 1 word/3 f, +10 f. Optional sheen sweep 30 f.
- **O-CTA-FOLLOW**: "احفظ" / "الريل" slide from left with motion blur 6 f (+9 f), then "Follow" tracking-collapse, sub-lines +0.5 s; fade to black 36 f.
- **O-CURSOR-CLICK** (see X-CIRCLE-WIPE) → logo stroke reveal 10 f → wordmark L→R 6 f → hold 4 s.

## Before/After portfolio board (for showcase posts only)
Bg `#0B0004` or `#110F10` + blurred diagonal accent beams. Before card ≈ 35 %W at (x 6–37 %, y 29–56 %), After card 9:16 ≈ 50 %W at (x 41–91 %, y 18–67 %), radius 32–40, 1 px grey border. Serif or Anton labels above each. AE/PR timeline screenshot `perspective(1200px) rotateX(38–48deg)` below with linear playhead. Both cards play the same take in sync; fade to black 12–20 f.
