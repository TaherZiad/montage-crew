# Resolve 20/21 Edit & Cut pages — pro vertical-reel workflow

> For users whose profile editor is DaVinci Resolve (free or Studio). The skill always delivers `final.mp4` + an FCP7 timeline XML to import (File > Import > Timeline); this file is for finishing/editing in Resolve after that import. Optional LIVE mode (driving Resolve directly): `references/resolve/00-control-architecture.md`. Features marked **Studio only** are missing or watermarked on the free edition.

Research: 24 transcripts + 5 contact sheets + 7 web. Ryan Herrick ×2 (535K), Think Media, Victor Grubbe, Jason Yadlovski ×2, Team 2 Films, Primal Video, Creative Video Tips ×2, MrAlexTech ×2, DaVinci Dojo, Casey Faris, Andrew Cooper, Joris Hermans ×2, Luca Epifani, Matt Johnson, Stanislav Rassokhin (IG re-encode tests), Resolve!بالعربي (Arabic client reel), كريم ربيع (white minimal Arabic reels), عمرو عطالله, Camilo Castañeda; Resolve 21 New Features Guide, 21.1 notes, API docs.

## Workflow (UI steps; the imported XML already carries the cut — use the steps you still need)
0. **Organise**: bins Footage/Timelines/Assets/SFX; Power Bin for reusable hooks, zoom macros, overlays.
1. **Project settings (Shift+9)**: 1080×1920, tick **Use vertical resolution**; frame rate = A-roll (lock BEFORE import; Arabic creator: lowest clip fps when mixing); Image Scaling → Mismatched resolution = **Scale full frame with crop**; optional color: DaVinci YRGB + DWG timeline, output Rec.709 2.4; proxies for 4K/H.265 (Prefer Proxies; Deliver uses originals).
2. **Timeline**: New Timeline (Ctrl+N), untick Use project settings, Format → Use vertical resolution (20+ switches to vertical layout; View → Stacked Timelines).
3. **Rough cut**: manual (split Ctrl+B or rebind "/", ripple delete Shift+Backspace, Ripple Trim Start/End to playhead Ctrl+Shift+[ ]); cut breaths; keep small pauses at pivots. Text-based editing / Remove Silent Portions / IntelliCut / IntelliScript = **Studio only** (and transcript misses false starts → external word-level transcript is better). Polish in Trim mode (T), dynamic trim (W + J/K/L).
4. **Reframe 16:9**: Smart Reframe (Studio only) or manual Zoom/Position; Paste Attributes (Alt+V) → Zoom & Position to all.
5. **Audio**: delete B-roll audio; dialogue +6 dB if quiet; Normalize Audio Levels (~−14 LUFS); Ducker in track inspector (source = dialogue); Voice Isolation/Audio Assistant = **Studio only**; J/L-cuts 3–4 f.
6. **Hook**: Text+ hook animated in Fusion (Transform, Ease Out Cubic); adjustment-clip zoom-out 2.0→1.0 over 60 f + blur + motion blur; riser/whoosh −20 dB.
7. **Punch-ins**: 100 % ↔ 115–125 % per jump cut, eyes on the same line; Dynamic Zoom (Inspector; green box start, red end, Swap, Ease In/Out) for slow pushes; snap zooms via Inspector keyframes + Keyframe Editor curve → Ease; free **Magic Zoom** macro (MrAlexTech).
8. **B-roll**: video-only on V2 over jump-cut seams; fill frame; split screen = Position Y + Crop.
9. **Titles**: Text+/Fusion titles; save macros as Edit templates (21 Macro editor → Save to Edit Template); 21.1 Inspector presets.
10. **Captions**: Create Subtitles from Audio = **Studio only** (8–12 chars/line, single line, gap 0); style via Track tab + "Save track as preset"; Animated subtitles (Word Highlight etc.) dropped on the subtitle track header; Caption tab → Update Word Timings (21). Arabic → see 00-control-architecture (overlays / SRT import).
11. **Music**: Show Music Beats + snapping (N); Music Editor (Studio only) fits length; duck under dialogue.
12. **Safe-zone check**: platform UI PNG on the top track, toggle with D.
13. **Deliver**: custom preset — MP4 **H.264, 1080×1920, timeline fps, restrict 12–35 Mb/s** (IG re-encodes to ~14 Mb/s HEVC anyway; HEVC uploads showed a slight magenta tint → prefer H.264), AAC 320 kb/s 48 kHz, Force sizing + debayer highest, tags Rec.709 / gamma 2.4 (or 709-A on Mac), subtitles Burn into video or SRT sidecar; save as render preset. Instagram app: Upload at highest quality; transfer via Drive/AirDrop, not WhatsApp.

## Free vs Studio (21)
Free: vertical timeline/layout, all trimming, multicam, Keyframe Editor (bezier, multi-clip, Step), bezier retime keyframes (21), Dynamic Zoom, Optical Flow (Enhanced Better), manual/imported SRT + styling, Ducker/Normalize/Dialogue Leveler (≈), font browser, spell check, emoji in Text+, macro editor, Krokodove, new transitions/titles/generators, Inspector presets (21.1), HTML/Lottie import (21).
Studio only: Speed Warp, Smart Reframe, transcription/text editing, auto subtitles, animated subtitles (need AI timing), IntelliScript, IntelliCut/Remove Silence, Audio Assistant, Voice Isolation, Music Remixer, Music Editor/Beat Detector (≈), SmartSwitch, Magic Mask 2, Depth Map, Face Refinement, Set Extender, all 21 AI tools (IntelliSearch, Speech Generator, CineFocus, Face Age/Reshaper, Blemish, UltraSharpen, Motion Deblur), scripting + built-in MCP (21.1). Free edition = UHD 60p max, 8-bit H.264/H.265 encode (≈).

## Parameter recipes
- Punch-in: Zoom 1.00 / 1.15–1.25 / 1.00; adjust Position Y so the eyes stay level (4K on a 1080 timeline → up to ~2.0 clean).
- Slow push: Dynamic Zoom red box 8–12 % tighter; or Zoom 1.00→1.08 eased.
- Snap zoom: 1.0→1.3 in 6–10 f, eased, motion blur (Fusion Transform or Magic Zoom).
- Hook zoom-out: adjustment clip 0–60 f, Fusion Transform Size 2.0→1.0, Out Cubic (long first handle), motion blur; optional Blur high→0.
- Text pop-up: Transform Center Y −0.1 → 0.5 over 15–20 f, Ease Out Cubic, ~4 f handles; per-char Latin: Text+ Follower opacity 0→1 over 20 f + delay.
- Speed ramp (21): Ctrl+R, trim to beat length, first key Ease Out, last Ease In; S-curve (fast-slow-fast) or ∩ (boomerang); Optical Flow + Speed Warp (Studio only)/Enhanced Better; 100→300–500→100 % only on B-roll; add Motion Blur over the fast part.
- Captions: 8–12 chars, 1 line, bold sans (Arabic: Cairo/Tajawal/Almarai Bold) ~70–90 pt at 1080 wide, white + 4–8 px black stroke/shadow, just above the chin (~60–65 % H), never bottom 20 %.
- Audio: dialogue −14 LUFS / −1 dBTP; music −18…−24 under speech; SFX ~−20.

## Scriptable vs UI-only (21.1; LIVE mode only)
Scriptable: timeline setup, `AppendToTimeline` keep-lists, `DeleteClips(ripple)`, FCPXML/OTIO import, static `SetProperties` (Zoom, Pan/Tilt, Rotation, Crop, Opacity, RetimeProcess, MotionEstimation, DynamicZoomEnabled/Ease), `SetSpeed`, `SetFades`, `AddTransition`, markers, compounds, Fusion titles/comps, render. **Studio only** AI calls (Smart Reframe, subtitles, transcription) — skip on free.
UI-only: Inspector keyframe animation (use FCPXML/Fusion instead), retime curves, audio automation, Normalize via menu (API has `NormalizeAudioLevel`), Voice Isolation, Remove Silence, subtitle track styling, Paste Attributes, beat snapping.

## Idea bank
hook zoom-out 200 % + motion blur + riser · 100/120 % punch-ins with eyes locked · slow push through the value section · snap zoom + whoosh on the claim word · stacked-word hook (Light/Regular/Bold Italic) · brand-colour word highlight captions · difference-blend hook title · split-screen before/after · B-roll over every seam · J-cuts at section changes · S-curve speed-ramped B-roll + motion blur · boomerang ramp on product reveal · beat-snapped montage cuts · music edited to 30/45/60 s · ducker + music swell at outro · green-screen overlay (Delta Keyer) on keyword · white-minimal Fusion scene with texture + cut-outs + kinetic Arabic text (كريم ربيع style) · looping glow via Duplicate > Loop keyframes · progress bar generator · subtitle fades (21) · designed hook title instead of captions over the hook · UI overlay PNG toggled with D · Power Bin + Inspector presets + subtitle track preset = one-click brand kit.

## Mistakes / QA
Mistakes: fps set after import / 24-vs-30 mismatch · "Scale to fit" black bars · exporting 4K vertical · Backspace (lift) instead of ripple delete · trusting AI transcripts · editing animated-subtitle text in the Track box · text under platform UI · Speed Warp on while editing / ramps on dialogue · linear keyframes, no motion blur on fast zooms · not duplicating the timeline before destructive AI · opening 21.1 projects in 20.x · WhatsApp transfer · HEVC tint / wrong gamma tags.
QA: 1080×1920 at target fps, no black bars (B-roll too) · no gaps (Timeline > Select Gaps), no flash frames · hook reads in 1–3 s, no double text · every jump cut covered, eyes aligned · captions spell-checked, word timing updated, safe zones (overlay on/off) · −14 LUFS, TP < −1, no clicks, music ducked, no stray B-roll audio · ramps artefact-free · Deliver settings as above, subtitles burned or SRT · watch the render on a phone.
