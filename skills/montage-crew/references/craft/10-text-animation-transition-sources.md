# Where text animations and transitions come from

Basis: 387 HyperFrames registry items tested (about 60 snapshots on real talking-head frames), all 417 templates shipped with Resolve, marketplace packs (Envato, Lottie, GSAP plugins) tested on Arabic, and 22 text styles + 12 transitions from 19 recent tutorials (5 of them Arabic).

## Rules that decide everything
- **Arabic breaks under per-letter animation.**
  - Anything that wraps letters in spans or uses per-character animators (AE, Resolve Text+ Follower, SplitText `chars`, scramble, matrix-decode, typewriter-by-letter, and Latin Lottie text) breaks the letter joins.
  - Always animate by **word, line or clip mask**. Stretch with **kashida** (U+0640) or with variable-font weight/width axes. Both keep the joins intact.
- **Paid text packs are not worth buying.** Every marketplace pack is Latin and per-character. Build text moves ourselves (see below).
  - Buy or download only **real-footage overlays** (light leaks, film burns, glitch) and **whoosh/transition SFX**.
- **GSAP on Arabic, tested in Chrome:**
  - TextPlugin with defaults types correctly from the right; `delimiter:" "` gives word-by-word typing.
  - TextPlugin `rtl:true` and ScrambleText `rightToLeft:true` go the **wrong** way for Arabic. Leave them off.
  - SplitText `type:"words"` is safe, and its default stagger already runs right to left.
- **Tracking does nothing on Arabic.** Chrome ignores letter-spacing inside Arabic words, so tracking animations are a no-op.
- **Outlined text:** `-webkit-text-stroke` shows seams where letters join. Use `paint-order: stroke fill`.
- **Soft only (craft/09).** Reject any caption or lower-third component that has a box, pill or card.

## Text animations: sources in priority order
1. **Our kits**:
   - `assets/rtl-kit.js`: wipeRTL, wordsIn, kashidaIn, softIn/softOut, captionSwaps and more.
   - `assets/ta_kit.js`: 9 more soft, word/line-level RTL styles, including blur rise, gradient/shine fill, glow, hand-drawn underline (SVG attribute), karaoke tint, rolling 3-line stack, mask-rise and centred build.
2. **HyperFrames registry** (`npx hyperframes@0.8.151 catalog --query <x>`, `npx hyperframes@0.8.151 add <name>`, Apache-2.0). Arabic-adapted copies are in `assets/templates/ar/`:
   - `ar-clip-wipe.html`: per-word RTL wipe, keyword tint, spoken words dimmed, no box. Takes a `words.json` list.
   - `ar-weight-shift.html`: two-line bold/light captions.
   - `ar-lt-mask-reveal.html`: soft lower third with a mask reveal.
   - Safe as-is when mounted with `dir="rtl"`, `--bg: transparent`, a local Arabic `@font-face` and word split only: `per-word-rise` (split=word), `kinetic-type-swap`, `line-swap`, `text-match-cut`, `headline-slam`, `marker-highlight` (style=circle), `vox-annotate`, `typewriter` (clip reveal), `streaming-text`.
   - Reject: `caption-highlight`, `caption-pill-karaoke`, the card lower thirds (boxes), anything with split=char, and `kinetic-center-build` (breaks under RTL).
3. **Resolve built-in Fusion Titles** (107 ship in Resolve's `Templates.drfx`, free and Studio). Only for users whose editor is Resolve. 75 animate the whole layer, so Arabic joining survives.
   - You **must** set `ReadingDirection` (RTL) and `UseLigatures` (Non-Latin) on every Text+ you insert; no template sets them.
   - Use only for Latin words, numbers, or quick tests. Arabic hero text stays in HyperFrames.

## Transitions (≈95 % of cuts stay hard or punch; one family per video; peak velocity on the cut)
- **Overlay transitions** (render standalone to ProRes 4444 alpha, put on a track above a hard cut in the editor):
  - `ar-organic-light-leak-overlay`: soft, the best fit for premium.
  - `ar-editorial-flash-overlay`: white flash, the hit peaks at 58 % of its duration.
  - `ar-hw-scribble-transition` and `ar-mk-clone-wall-transition` (tiles an Arabic word): full cover for 0.6–1.9 s; cut underneath them.
  - Edit each block's internal `data-duration`. The last two only render standalone, not when mounted in a host.
- **Two-scene transitions with footage:**
  - `ar-whip-pan-cut.html`: put `<video>` elements into its before/after slots and render the 1.2 s junction.
  - The same pattern works for iris, chromatic wipe, and the blur/scale/push/light recipes.
- **Shader transitions** (14 in the registry; the installed demo cards show nothing on footage):
  - Lift the GLSL into a portrait canvas harness that samples from `<video>`.
  - Best: light-leak, cinematic-zoom and whip-pan. Glitch only on "error" beats.
- **Resolve built-in:** 32 simple transitions (Cross/Additive Dissolve, Dip to Color, Blur Dissolve, Push/Slide…) — they need handles — plus 67 Fusion transitions (free). **Studio only:** Smooth Cut and animated AI subtitles.
- **ffmpeg xfade** (58 transitions): for pre-renders. Screen/Add blends of light leaks must run in **RGB (gbrp)**, or everything turns magenta.
- **Free footage overlays:** royalty-free/CC0 stock sites — check each licence for commercial use and attribution.
- **Envato Elements** (only if the user has a subscription): the user downloads while logged in; we shortlist the URLs.

## Which transition, when
- **Hard cut + punch:** the default, inside a section.
- **Zoom-blur or whip** (8–15 f): a section or topic change.
- **Light leak** (15–30 f): a premium or emotional chapter change.
- **Flash strobe** (13 f, W1/A1/W1/B1/W1): cinematic chapter looks (craft/09 §7).
- **Glitch:** only on error, tech or AI-fail beats.
- **None:** on serious lines, the first 1–2 s of the hook, or testimonials.

Every transition gets its sound: whoosh peak on the cut, crack on the flash, sub hit on the first frame of the new shot (craft/09 §4).
