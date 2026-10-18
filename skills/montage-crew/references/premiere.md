# Premiere Pro — importing and finishing the skill's edit

For users whose `profile.editor = premiere`. They always get `final.mp4` (already mastered); this file is for when they want to keep editing in Premiere.

## Import (give the user these steps in Arabic, short)
1. Premiere › New Project (any name). File › Import → `<out>/project/timeline.xml`. Premiere creates a sequence with the same layout as the skill's timeline:
   V1 plate (if any) · V2 behind-speaker graphics · V3 A-roll / speaker · V4 split stage · V5 captions + hook · V6 motion graphics (one clip per beat) · A1 voice · A2 music · A3+ SFX.
2. If clips show offline: select them › right-click › Link Media › point to `<out>/project/media/` (all files are there, names unchanged).
3. Check Sequence › Sequence Settings: 1080×1920 (or 1920×1080), 30 fps, square pixels. The overlays are ProRes 4444 with alpha — they composite over the A-roll with no extra setting.
4. Export: File › Export › Media → H.264, "Match Source – High bitrate", AAC 48 kHz 320 kbps. Then, for the same loudness as the skill's master: `{{PY}} {{SKILL_DIR}}/scripts/master.py <export.mp4> <final.mp4>` (−14 LUFS / ≤ −1.5 dBTP).

## Notes
- Arabic text is pre-rendered in the overlay clips (correct shaping, kashida, RTL). Re-typing it in Premiere's Essential Graphics loses kashida and can break joins in some fonts — ask the skill to re-render a caption or MG clip instead (it writes a new `_v2` file; relink that one clip).
- To change a caption word: tell the skill; only the captions layer is re-rendered, timing stays the same.
- The `.srt` next to the final can be imported as a caption track for platforms that read sidecar captions (YouTube); keep the burned-in captions off the export in that case only if the user wants platform captions instead.
- Premiere's Auto Reframe/Speech-to-Text are not needed: framing and Arabic timing already come from the skill.
