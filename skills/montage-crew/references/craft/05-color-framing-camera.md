# Footage treatment — grade, look, framing, virtual camera

Research: 23 transcripts (20 EN, 3 AR) + 6 contact sheets + 5 web. Denz Creates ×2, Brad West, Joris Hermans ×2, Casey Faris, Darren Mostyn (327K), Dante Pascarella (404K), Sankho's Cut, Gaku Lange, NaughtyyJuan (1M), Premiere Gal, Think Media, Olufemii, Dunna Did It (439K), Design Success Lab, Basic Filmmaker, Emberdyn, Junius Ong, Camilo Castañeda (1M), Ahmed Rizq (AR), MOHAMED ALI (AR 158K), Resolve!بالعربي (AR); ffmpeg haldclut guide, ffmpeg-cookbook, Frame.io skin tones, skin-tone line (123°), 4K-in-1080 zoom limits. All ffmpeg chains parse/run on 1080×1920 test source — verify on real footage. `[practice]` = not from a source.

**Default: keep the original pixels on faces** — no grade, no LUT, no sharpening or relight on the speaker unless the user asks for a look (or the brief/profile/`rules.md` says otherwise). Fix only what is broken (recipe F) when the scout flags it. Everything below is for when a look is requested.

## Principles
1. **Correct → then grade** (~10): exposure/WB → contrast → saturation → creative look → texture. LUT last at 50–60 %.
2. **Subtle beats strong** (~9): gentle S-curves; 8-bit phone H.265 bands when pushed; "expensive" = restraint.
3. **Protect skin** (~7): push background blues toward teal; skin stays on the ~123° line; brighten oranges rather than saturate.
4. **Pull attention to the face** (~6): feathered vignette, darker/desaturated edges, slightly brighter face zone, edge blur.
5. **One grade across everything** (~5): per-clip exposure/WB fixes, one look on top. Mismatch = cheap.
6. **Move the camera with a reason** (~6): punch-ins emphasise/hide jump cuts; slow push keeps interest (feels ~half as long); eased, with sound. Random zooms = top over-edit.
7. **Eyes stay on the same line across punch-ins/reframes** (~3): scale from an anchor at the eyes, not by moving position.
8. **Phone footage** (~5): denoise first, undo oversharpening, no big pushes, warm skin slightly after neutralising.

## ffmpeg recipes
Wrap: `format=yuv444p10le,<chain>,format=yuv420p`; encode `-c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -movflags +faststart`.

**A. Clean-bright (educational/business default)**
```
eq=contrast=1.06:saturation=1.08:gamma=1.02,
curves=all='0/0.02 0.25/0.23 0.5/0.52 0.75/0.79 1/0.98',
colorbalance=rh=0.02:bh=-0.02:pl=1,
unsharp=5:5:0.35:5:5:0,
vignette=a=PI/6
```
(unsharp only on non-phone footage.)

**B. Warm / golden (lifestyle, story, hospitality)**
```
colortemperature=temperature=5600:mix=0.6:pl=1,
eq=contrast=1.08:saturation=1.05,
curves=r='0/0.02 0.5/0.53 1/1':b='0/0.03 0.5/0.48 1/0.95',
vignette=a=PI/5,
noise=alls=4:allf=t+u
```

**C. Teal & orange (cinematic, tech, studio)**
```
curves=all='0/0.03 0.25/0.21 0.5/0.5 0.75/0.8 1/0.97',
colorbalance=rs=-0.06:gs=0.01:bs=0.08:rm=0.03:bm=-0.03:rh=0.05:gh=0.01:bh=-0.05:pl=1,
selectivecolor=blues='0.25 -0.05 0 0':cyans='0.15 0 0 0':reds='0 0 0.05 0',
eq=saturation=1.05,
vignette=a=PI/5,
noise=alls=5:allf=t+u
```
Faces going grey-green → halve gs/gh and bs (bs ≈ 0.03 keeps shadows neutral).

**D. Moody / low-key (serious topic, dramatic hook)**
```
eq=contrast=1.12:brightness=-0.03:saturation=0.85:gamma=0.95,
curves=all='0/0.04 0.2/0.14 0.5/0.47 0.8/0.82 1/0.94',
colorbalance=bs=0.05:gs=0.02:rh=0.03:pl=1,
vignette=a=PI/4,
noise=alls=7:allf=t+u
```

**E. Film look (premium) — needs -filter_complex**
```
curves=all='0/0.035 0.5/0.5 1/0.96',
colorbalance=rs=-0.03:bs=0.04:rh=0.03:bh=-0.03:pl=1,
eq=saturation=0.95,
split[a][b];[b]lutyuv=y='if(gt(val,200),val,0)',gblur=sigma=18[glow];[a][glow]blend=all_mode=screen:all_opacity=0.18,
gblur=sigma=0.6,
vignette=a=PI/5,
noise=alls=6:allf=t+u
```
(white halation on highlights only; gblur 0.6 removes the digital edge.)

**F. Fix bad phone footage (before any look)**
```
hqdn3d=2:1.5:3:3,                               # heavy night noise: nlmeans=s=2.5:p=7:r=15 (slow)
eq=gamma=1.10:contrast=1.05:saturation=1.05,    # lift gamma, not brightness
colortemperature=temperature=6000:mix=0.5:pl=1, # blue/LED cast; 7000+ for orange tungsten
unsharp=5:5:-0.25:3:3:0,                        # negative = soften phone oversharpening
deband,
noise=alls=3:allf=t
```
Green cast `colorbalance=gm=-0.04:gh=-0.03` · clipped highlights `curves=all='0/0 0.8/0.78 1/0.93'` · shaky: `vidstabdetect` → `vidstabtransform=smoothing=20:zoom=3` · VFR phone clips: `-fps_mode cfr -r 30` · LUT last at 55 %: `split[o][l];[l]lut3d=file=look.cube:interp=tetrahedral[g];[o][g]blend=all_mode=normal:all_opacity=0.55`.

## Skin-tone safety
1. Skin hue on ~123° line; move blues/cyans/greens freely, reds/yellows ±5° max.
2. Skin saturation 20–50 %; prefer `vibrance=intensity=0.1–0.2` over `eq=saturation`.
3. `[practice]` face YAVG ≈ 55–70 % (lighter skin) / 40–55 % (darker) — measure on a face crop with `signalstats`.
4. Contrast via gamma, not brightness; forehead YMAX < ~235 (8-bit).
5. Brighten orange luminance rather than saturation.
6. After any teal move, check the face for green/grey.
7. Grade identical across the video; only exposure/WB vary per clip.

## Virtual camera system (GSAP on the video wrapper, 30 fps)
Base: `transform-origin` at the **eyes** (e.g. `50% 32%`); stay within native resolution (4K→1080 up to 200 %; 1080 source ≈ 115 % before softness).
| Move | Scale | Duration | Ease | Use |
|---|---|---|---|---|
| Hard punch-in (cut) | 100 → 115–130 % | 0 f | — | hide jump cut, key line, reaction; wide/tight/wide, never two tights in a row |
| Snap emphasis zoom | 100 → 120–130 % | 8–10 f | `power3.out` / `expo.out` | hook, "here's the secret", a number (+ whoosh) |
| Smooth zoom | 100 → 125 % | ~30 f | `power2.inOut` (or `power3.out`) | entering a new idea / list item |
| Slow push-in | 100 → 106–112 % | 90–180 f (whole sentence) | `sine.inOut` / linear | explanations, emotional/story beats |
| Pull-back | 125 → 100 % | 20–30 f | `power2.inOut` | resolution, big picture, end of point |
| Bounce | 100 → 112 → 108 % | 6 + 6 f | `back.out(2)` | punchline / beat drop (rare) |
| Handheld drift `[practice]` | 104 % overscale | continuous | sum of sines | ±4–8 px @ 0.5–1.2 Hz + ±0.2–0.4°; never on text-heavy frames |
| Impact shake `[practice]` | 105 % overscale | 6–10 f decaying | — | ±15–30 px @ 8–12 Hz → 0 |
| Speed ramp | — | in 4–6 f, peak 300–500 %, out 4–6 f | S-curve | B-roll only, never on talking audio; same-direction pairs; motion blur (`tmix=frames=3`) |
| Whip pan | x ±100 % W + blur | 6–8 f out + 6–8 in | `power4.in` / `power4.out` | topic/location change + whoosh |
| 3D tilt | rotateY 6–10°, perspective 1200 | 20–30 f | `power2.inOut` | screen-in-screen variation, once per video |
Frequency: one camera event every 3–6 s (reels), 8–15 s (long YouTube); a static stretch ≥ 1.5 s after each move; every move has a trigger (word, beat, cut).
ffmpeg: push-in `zoompan=z='min(1+0.0017*on,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30` (jitters on small zooms — upscale 2× first, or do zooms in GSAP). Drift: `scale=iw*1.04:-2,crop=1080:1920:(iw-1080)/2+6*sin(2*PI*t*0.9)+3*sin(2*PI*t*2.3):(ih-1920)/2+5*sin(2*PI*t*0.7+1)`.

## 16:9 → 9:16 reframe
Crop `ih*9/16` centred on the face, track **X only**, heavily smoothed (following head bobs looks robotic). Eyes at 30–35 % from top. Two people: top/bottom split (1080×960 each) or cut on speaker changes. Must stay whole: blurred-fill background (`split; bg scale-to-cover + crop + gblur=sigma=40 + eq=brightness=-0.12; fg scale=1080:-2; overlay centred`).

## Idea bank
punch-in every jump cut 100/118 % eyes level · snap zoom + whoosh on hook word ≤ 1.5 s · slow push 100→108 % over emotional sentence · pull back on CTA/resolution · feathered spotlight (out −10 % bright −20 % sat, in +3 %) · radial edge blur via inverted feathered ellipse · halation 0.15–0.2 · soften phone sharpening · temporal grain 3–6 · blue→teal bg with skin locked · B&W for flashback/"old way" · desat 0.3 + slow zoom for "problem", snap to colour on "solution" · beat micro-bounce 108 % · handheld drift on tripod shots · impact shake on shocking stat · speed-ramped B-roll · whip between topics · blurred-fill for 16:9 · **segment person + blur background 12 px = biggest "expensive" upgrade for flat phone bg** · freeze + desat bg + callout · 3D tilt screen-in-screen · letterbox 2.39 only for cinematic story segment · +0.15 brightness 2 f flash on hook cut · cut on gesture then punch in · CTA slightly tighter + more saturated.

## Mistakes / QA
Mistakes: LUT 100 % or first · saturation on skin · teal in faces/shadows · pushing 8-bit · sharpening phone footage · random zooms / aiming zoom by moving position (black edges) · linear keyframes · scaling past native res · each clip graded differently · too much grain/vignette · speed ramps without blur · vertical head-bob tracking · grading someone who grades their own footage (ask).
QA: 1 blacks black/whites white, face YMIN > 16, YMAX < 235 · 2 face hue ~123°, sat 20–50 %, no green/grey · 3 no banding (deband + grain) · 4 identical grade across A-roll (`hstack` first/mid/last frames) · 5 punch-ins keep eyes ±2 % vertically, within native res · 6 every move eased + triggered, ≥ 1.5 s static between moves · 7 9:16 eyes at 30–35 %, captions outside UI zones · 8 no black edges at shake peaks · 9 ramps only on B-roll with blur, audio never ramped · 10 yuv420p, CRF ≤ 18, CFR at source rate, +faststart.
