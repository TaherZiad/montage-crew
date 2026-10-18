# After Effects, CapCut, Final Cut — importing the skill's edit

For users whose `profile.editor` is `after_effects`, `capcut` or `final_cut`. They always get `<title>.mp4` (already mastered, ready to post); this file is for when they want to keep working in their editor. Give the user the steps for THEIR editor only, in short Arabic.

What the project folder holds (`<out>/project/`):
| Editor | Files | Made by |
|---|---|---|
| After Effects | `ae_import.jsx` + `media/` (A-roll, speaker matte, captions, one MG clip per beat — ProRes 4444 with alpha — voice, music, SFX) | `compose.py … --ae` |
| CapCut / Final Cut | `layers/NN_<layer>_<name>.<ext>` (01 = bottom; video layers first, then audio: voice, music, SFX) + `order.txt` (one line per file: `file⇥start s⇥end s⇥track`) + `layers.csv` (file, kind, track, start_s, end_s, source_in_s, gain_db) | `compose.py … --layers-out` |

## After Effects
1. Open After Effects › New Project. **File › Scripts › Run Script File…** → choose `project/ae_import.jsx`.
2. The script imports `media/` and builds one composition (named after the video; 1080×1920 or 1920×1080, 30 fps, full duration) with every layer at its start and duration, bottom → top (plate → behind graphics → speaker → captions → motion graphics). The A-roll keeps its sound, other video layers are muted, music/SFX sit at their gain. Zooms come in as Scale/Position keyframes (linear; select them › F9 Easy Ease for softer moves). Missing media → one alert listing the files.
3. If a file shows as missing: right-click it in the Project panel › Replace Footage › File… and point to `project/media/` (names unchanged).
4. Export: Composition › Add to Render Queue (or Adobe Media Encoder) → H.264, AAC 48 kHz. For the same loudness as the skill's master: `{{PY}} {{SKILL_DIR}}/scripts/master.py <export.mp4> <final.mp4>` (−14 LUFS / ≤ −1.5 dBTP).
- The import does **not** need the preference "Allow Scripts to Write Files and Access Network" — leave it OFF. If After Effects asks for it, stop and tell the skill (the script only imports files and creates layers).
- The script contains only import and layer commands; it is generated fresh for each video. Run only an `ae_import.jsx` that the skill made for you.

## CapCut (desktop)
1. New project. Import the whole `project/layers/` folder.
2. Drag the files onto the timeline in the order of `order.txt` (first line = lowest track): the A-roll on the main track, then each `.mov` on its own overlay track from its start to its end time (seconds). Audio files on audio tracks; `layers.csv` gives each one's gain in dB.
3. The `.mov` layers have transparency; CapCut shows them over the video with no extra setting. If a layer looks black, it was imported as a plain video — re-import it from the folder.
4. Project ratio 9:16 (or 16:9), 30 fps. Export 1080p, 30 fps. The mastered `<title>.mp4` is already there if no changes are needed.

## Final Cut Pro
1. New Library/Event › File › Import › Media → `project/layers/`.
2. New project 1080×1920 (or 1920×1080), 30 fps. Put the A-roll in the primary storyline; connect each `.mov` above it at the start time from `order.txt` (highest number = top). Audio files as connected audio below.
3. Alpha: the ProRes 4444 layers keep their transparency. If one shows black, select it › Inspector › Info › Alpha Handling: Straight.
4. Share › Master File (H.264). For the skill's loudness run `master.py` on the export (as above).

## Notes (all three)
- Arabic text is pre-rendered in the overlay clips (correct shaping, kashida, RTL). Re-typing it in the editor's own titles loses kashida and can break letter joining — ask the skill to re-render a caption or MG clip instead (new file `_v2`; replace that one clip).
- To change a caption word: tell the skill; only the captions layer is re-rendered, timing stays the same.
- The `.srt` next to the final can be imported as a caption track for platforms that read sidecar captions.
