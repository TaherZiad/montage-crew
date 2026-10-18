# Resolve Color page — talking-head reels

> For users whose profile editor is DaVinci Resolve (free or Studio). The skill always delivers `final.mp4` + an FCP7 timeline XML to import (File > Import > Timeline); this file is for finishing/editing in Resolve after that import. Optional LIVE mode (driving Resolve directly): `references/resolve/00-control-architecture.md`. Features marked **Studio only** are missing or watermarked on the free edition.

Research: 23 transcripts + 6 frame sheets + 6 web. Cullen Kelly ×3, Darren Mostyn ×4, Waqas Qazi ×7, Casey Faris, Jamie Fenn, Russell Wofford, Danny Gan ×2, MrAlexTech, Team 2 Films, Amr Atallah ×2 (AR); API gists (X-Raym v21.0.4, mhadifilms), Blackmagic Studio/what's-new, Resolve Club. (verify) = unconfirmed.

Default: keep the original pixels on faces — grade only when the user asks for a look (craft/05).

## Color management (recommended: node-managed)
- Project: **DaVinci YRGB**; timeline **DaVinci Wide Gamut / DaVinci Intermediate** (needed for HDR palette, Warper, ColorSlice); output Rec.709 **Gamma 2.4** (calibrated) or **2.2** (uncalibrated sRGB laptop).
- Deliver tags Rec.709; never set project output 709-A under RCM (gamma shift). Mac only: viewer options "Use Mac display profiles" + "match QuickTime".
- Input CST (→ DWG/DI): iPhone SDR = Rec.709/Rec.709 (8-bit: small moves) · iPhone HDR = Rec.2020 / Rec.2100 HLG (tone map, lower exposure) · Apple Log = Rec.2020/Apple Log · Apple Log 2 (verify menu) · S-Log3 = S-Gamut3.Cine/S-Log3 · V-Log = V-Gamut/V-Log · DJI D-Log M = D-Gamut/D-Log M.
- Output CST: DWG/DI → Rec.709 2.4/2.2, Tone Mapping DaVinci, Gamut Mapping **Saturation Compression**, OOTF Auto.
- Cullen Kelly structure: input CST at **group pre-clip**, output transform + look at **timeline level**; clips carry only shot grades.
- Pure phone Rec.709 only: may skip management but then timeline must be Rec.709. Long-GOP H.265 → ProRes/DNxHR proxies.
- DWG/DI middle grey pivot **0.336**; **1 stop ≈ 0.073 Offset**.

## Fixed node tree (label every node; save empty as PowerGrade)
```
01 IDT CST → 02 NR → 03 BAL/EXPO → 04 CONTRAST → 05 SAT
  ┌ 06 HUE CURVES ┐
  ├ 07 SKIN       ├ parallel → 10 TRIM
  ├ 08 WARPER     │
  └ 09 HIGHLIGHTS ┘
→ 11 FACE LIGHT (window) ∥ 12 VIGNETTE (inverted window)
→ 13 SKIN REFINE → 14 LOOK (compound, key-mixed) → 15 TEXTURE → 16 ODT CST
```
| Node | Values |
|---|---|
| 02 NR (Studio only) | Temporal 2 frames Better, luma/chroma 6–10; Spatial/UltraNR 4–8; off on clean footage; cache |
| 03 BAL | neutral whites (Offset or HDR Temp/Tint; linear-gamma node for true WB); face ~60–70 IRE fair, 50–60 medium, 40–50 dark |
| 04 CONTRAST | 1.05–1.15 pivot 0.336; blacks 2–5 %, speculars < 95 % |
| 05 SAT | ColorSlice/HDR sat 1.05–1.15 (subtractive, saturation depth) |
| 06 HUE CURVES | greens → yellow, green/cyan sat −10…−25 %, Lum-vs-Sat −10 % deep shadows |
| 09 HIGHLIGHTS | HDR highlight exposure −0.2…−0.5 |
| 11 FACE LIGHT | tracked soft circle (25–50): gamma +0.01–0.03 or exposure +0.15–0.3 |
| 12 VIGNETTE | inverted oval, Offset −0.02…−0.05, sat 0.9, softness 40–60 |
| 13 SKIN REFINE (Studio only) | Face Refinement smoothing 0.1–0.25 |
| 14 LOOK | Film Look Creator (Studio only) or LUT in CST sandwich, key output gain 0.3–0.7 |
| 15 TEXTURE | grain 35mm 0.1–0.2 (bigger size for IG), sharpen Blur-tab radius 0.47–0.49 |
Looks sit right before the output transform. Toggle each node to prove it helps.

## Six looks (node deltas)
| | Clean bright | Warm | Teal/orange | Moody | Film | Luxury |
|---|---|---|---|---|---|---|
| Bal/Expo | +0.2–0.4 stop, neutral | Temp ≈ +300, tint +2 mag | neutral | −0.2 stop | slight warm R+.005/B−.005 | neutral, cool mids |
| Contrast | 1.08, lift blacks slightly | 1.10 | 1.15 | 1.20–1.25 pivot .30 | 1.05 | 1.15, deep not crushed |
| Sat | 1.12 | 1.10 | 1.05 | 0.85–0.90 | 0.95 | 0.85–0.90 |
| Hue | greens −15 % | yellow→orange +3–5°, blue −20 % | green/cyan→teal, blue→cyan, greens −25 % | non-skin −20 %, highs −15 % | greens→olive, blue −15 % | only gold/skin/neutral, others −30 % |
| Skin | on line, slight warmth | a touch warmer | protect, +5 % | 5–10 % more sat than bg | film shapes it | creamy: reds→orange −3°, sat −5 % |
| Highlights | −0.3 | warm (Light zone +200) | warm/orange | roll off −0.4 | print roll-off | gold-kissed (hue ~40°) |
| Shadows | neutral | neutral/warm | teal (hue ~190°, sat .1–.2) | teal-blue, matte black .03–.05 | slight matte .02, green-cyan | clean cool, no matte |
| Windows | face +0.2 | face +0.2, vig −0.03 | face +0.2, vig −0.03 | face +0.3, vig −0.05…−0.07, bg sat 0.8 | vig −0.03 | face +0.2, vig −0.04 soft 60 |
| Look | none | warm film LUT @0.3 | FLC Cinematic / LUT @0.4 | FLC Nostalgic @0.5 | **Kodak 2383** in sandwich (→ Cineon Film Log) @0.4–0.6, or FLC Default 35 ~40 % | FLC Default 65 ~30 % |
| Texture | sharpen 0.48 | grain .08 | grain .1 | grain .15–.2, halation .1 | grain .15–.25, halation .2–.3, bloom .1 | glow .05–.1, grain .05 |

## Skin workflow
1 correct input CST/WB first · 2 balance before skin; never desaturate globally · 3 vectorscope skin line (~11 o'clock), isolate face to read it, ±5° · 4 compress don't shift: Hue-vs-Hue red→orange slightly, yellow→orange slightly (or ColorSlice skin) · 5 broad curves over keys; key one channel only, never hard on 8-bit; RGB Mixer small red-from-blue to warm magenta skin · 6 Magic Mask (Studio only) person/feature, Better, both ways, outside node for bg · 7 Face Refinement subtle (Studio only) · 8 shape light: tracked window or Relight (Studio only) + Depth Map key · 9 compare to hero still.

## Free vs Studio (21)
Free: nodes, primaries, HDR palette, curves, qualifiers, windows, tracking, scopes, LUTs, CST, groups, stills/PowerGrades, HDR grading, 21 Multi-Master Trim/layer list/group versions (Waqas: free), Color Warper/film grain/glow/sharpen (verify). **Studio only:** temporal/spatial NR & UltraNR, Magic Mask, Face Refinement, Relight, Depth Map, **Film Look Creator**, CineFocus/face AI/Blemish, SuperScale, Speed Warp, Smart Reframe, Deflicker, Dehaze, DCTL, HDR nits scopes. ColorSlice / Chroma Warp: verify.

## Scripting grades (LIVE mode only)
API: `item.GetNodeGraph(1)` → `ApplyGradeFromDRX(path, 0|1|2)`, `SetLUT(nodeIdx, path)` (needs `project.RefreshLUTList()`; silent fail on missing node), `SetNodeEnabled`, `ResetAllGrades`, `GetNodeLabel`; `item.SetCDL({"NodeIndex":"3","Slope":"1 1 1","Offset":"0 0 0","Power":"1 1 1","Saturation":"1"})` (strings, 1-based); `CopyGrades`, `AddVersion`, `AssignToColorGroup` + group `GetPreClipNodeGraph/GetPostClipNodeGraph`; `Gallery` PowerGrade albums `ImportStills([.drx])`; `ExportCurrentFrameAsStill`. Cannot: add/rewire nodes, set wheels/curves/qualifiers/windows/OFX (FLC, NR, Relight).
**AI approach**: build a DRX library once (inputs iphone_sdr/iphone_hlg/applelog/slog3/vlog/dlogm × looks clean/warm/tealorange/moody/film/luxury, identical node indices: 03 BAL, 05 SAT, 14 LOOK…) → `ApplyGradeFromDRX` per clip (or pre/post-clip group graphs) → per-shot `SetCDL` trims from ffmpeg measurements (face luma, neutral chroma; Offset 0.024 ≈ ⅓ stop; warm +0.004 R / −0.004 B) → `SetLUT(14, lut)` to swap looks, `SetNodeEnabled` to toggle NR/texture → QA via exported stills. Without LIVE mode or a DRX library: bake an ffmpeg look (craft/05) into the clips before export, or the user hand-grades once in Resolve after importing the XML and saves a still.

## Mistakes / QA
LUT on unbalanced footage / log LUT without sandwich · DWG tools in a Rec.709 timeline · wrong input gamma (HDR as 709) · 709-A output under RCM · global desat for skin · hard keys on 8-bit · pushing 8-bit (banding) · ad-hoc unlabeled trees · visible/untracked windows · too much grain/sharpen/smoothing · heavy AI nodes without cache.
QA: correct IDT/ODT for camera & display · DWG/DI timeline · neutral greys, skin on line ±5° · face 50–70 IRE, blacks ≥ 1–2 %, no clipped face · sat compression on · no banding/key chatter/window edges · shots match hero still, look at group/timeline level · every node earns its place, look mix ≤ 70 % · no Studio nodes on free (watermark) · tags right, 1080×1920 high bitrate · check on real phones.
