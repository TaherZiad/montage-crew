# Team mode (pro) — the leader's playbook

Used when `profile.mode = pro` (or the user asks for the team on one video). You (the main session) are the **leader**: you decide, write the brief, dispatch, assemble, judge, deliver. Specialists (`mc-*` agents) each own ONE layer, write only in their own folder, and read only the part of the skill they need. Fast mode never uses this file.

**Agent names (check your Agent tool's list):** plugin install → `subagent_type: "montage-crew:mc-cutter"` (`montage-crew:mc-scout`, …); ZIP install → `mc-cutter` (`mc-scout`, …). Use whichever exists; same files, same behaviour. Give each spawn a `name` (`cutter`, `scout-1`, `motion-2`, …) so you can message it later.
**Paths:** resolve `{{SKILL_DIR}}`, `{{DATA_DIR}}`, `{{PY}}` to ABSOLUTE paths once (`mc_profile.py path`, SKILL §0) and write those into every dispatch prompt — agents never get a literal `{{…}}`.

| Agent | Spawned when | Owns (writes only here) | Delivers |
|---|---|---|---|
| `mc-cutter` (critical path) | footage = camera / screen / mixed | `<work>/raw/words.json`, `raw/transcript.txt`, `<work>/cut/` | proof-read transcript, retakes/set words removed, `cut.mp4` + FINAL `words_cut.json`, `script.txt` |
| `mc-writer` | footage = none | `<work>/script/`, `audio/tts_v<n>.wav` (AI voice) | script in the dialect, voice file (own recording guide / AI voice / none), `voice.wav`, then `words.json` + `cut/words_cut.json` timing |
| `mc-scout` ×2 (S1 + S2) | always | `<work>/_team/scout.md` (S1), `_team/scout2.md` (S2), `<work>/assets/` (S1: `logos/ ui/`, S2: `icons/ mockups/ img/ fx/`) | S1: footage/audio intake, then assets of everything NAMED; S2: generic assets for the beats |
| `mc-picture` | footage = camera / screen / mixed | `<work>/picture/` | `speaker_v1.mov` (matte, camera only), `zones/zones.json`, `framing.json` (zoom moves + recording crops), optional plate |
| `mc-audio` | always | `<work>/audio/` | `voice.wav`, `sfx_cues.json`, `music_v1.wav` (pre-ducked), `premix.wav` |
| `mc-captions` | always | `<work>/mg_captions/` | `captions_v1.mov` (alpha: phrase captions + written hook) per aspect, `.srt` + `.txt` |
| `mc-motion` ×1–3 (M1, M2, M3) | always | `<work>/mg_motion/kit/` (M1 only), `mg_motion/m1|m2|m3/` | M1 ships the shared kit first; each ships its block of beats, one file per beat |
| `mc-cover` | always (after the matte or the brief when there is no speaker) | `<work>/cover/` | `cover.png` 1080×1920 + `cover_3x4.png` (+ `cover_16x9.png` 1280×720 when the format includes 16:9) |
| `mc-qa` | after the first full render | `<work>/qa/` (read-only elsewhere) | pass/fail list with times + the owner of each fix |

**How many motion agents:** video < 30 s → 1 (M1 only) · 30–60 s → 2 (M1 + M2) · > 60 s → 3. Split the MG beats into contiguous blocks of about equal work (`owners`: `motion-1` / `motion-2` / `motion-3`). Spawn each with the same agent file `mc-motion` and its block id in the prompt.
**Scouts:** always two instances of `mc-scout`: S1 and S2 (block id in the prompt).

## Phase 0 — minute 0: nobody waits for the leader
1. Leader (≤ 1 min): read the profile + `{{DATA_DIR}}/rules.md`; work dir `<work>` = `<profile.paths.work_dir>/<YYYY-MM-DD>_<idea-slug>/` (ASCII, named after the idea); copy the raw file(s) to `<work>/raw/`; create `<work>/_team/`. LIVE Resolve (only if `profile.resolve_live.enabled`): `live.py ping` → `live.py setup <work> "<Arabic title>"`.
2. **In ONE message, in the background**, spawn:
   - `mc-cutter` — transcribe → proof-read → retakes/set words → jumpcut → FINAL `cut/words_cut.json`. (footage = none — from the profile OR detected in this request: spawn `mc-writer` instead, with the idea/topic, the user's notes and the voice choice; no `mc-picture`; motion agents build the whole picture.)
   - `mc-scout` S1 — footage + audio intake (light CPU), later named assets.
   - `mc-scout` S2 — generic assets, starts the moment a transcript exists (waits for your message; no polling).
   - `mc-picture` part A — screen-recording crop plan (light CPU) — only when footage = camera/screen/mixed.
   Heavy jobs share one machine: never run the matte and a transcription on the same GPU at once; HyperFrames renders one at a time. Parallelism saves the THINKING/authoring time, not render time.
3. While they run, read `scout.md` and the raw sheet as they arrive and start the visual concept (palette — brand colours if set — fonts, motion personality).
4. **Cutter done** → in ONE message: message `mc-picture` "cut ready → part B" (matte starts, run ONCE on the final cut) and message both scouts "transcript ready → part B". Read `cut/script.txt` and write the brief.
5. **TIMING LOCK:** before motion starts, `words_cut.json` and every beat's `s/e` in `beats.json` are frozen. A late timing change forces a re-render of every motion beat and the captions — never again after this point.
6. Brief written → spawn `mc-audio`, `mc-captions` and the `mc-motion` instances **in ONE message, in the background**, each with the dispatch prompt below; message `mc-picture` the brief path for `framing.json` + zones.
7. **Matte done** (or brief done when there is no speaker) → spawn `mc-cover` in the background.

## The brief — `<work>/_team/` (the only shared state; deleted at delivery)
`brief.md` (≤ 1 page): `style: <slug> (<absolute card path>)` + learned techniques folder if any, brand (`has_brand`, absolute logo + font paths from `{{DATA_DIR}}/brand/`), topic, core message, audience, tone, dialect, motion personality, the written hook, palette (bg/text/accent hex), fonts, caption mode + style (CAP/SC), SFX budget (~14–20 per minute), aspect(s), and what the user's `rules.md` means for THIS video.
`beats.json` (machine, every agent reads it):
```json
{ "name": "2026-01-15_ai-tools-for-shops", "work": "<work>", "fps": 30, "dur": 52.4, "format": "9x16",
  "dialect": "gulf", "digits": "western",
  "palette": {"bg": "#0B131F", "text": "#F2F0E8", "accent": "#FF4F8B"}, "fonts": {"head": "Alexandria", "body": "IBM Plex Sans Arabic"},
  "captions": {"style": "CAP-04", "scheme": "SC-02"},
  "hook": {"text": "3 ساعات باليوم… وما دفعت شي", "s": 0.0, "e": 2.6},
  "shots": [[0, 3.4, "M"], [3.4, 9.8, "C"]],
  "beats": [ {"id": 1, "s": 0.0, "e": 3.4, "line": "…", "layout": "FULL", "visual": "none — hook only", "sfx": "low boom on «3»",
              "owners": ["captions", "audio"]},
             {"id": 2, "s": 3.4, "e": 9.8, "line": "…", "layout": "SPLIT", "visual": "recording raw/rec1.mp4, zoom to the prompt 5.1–6.3",
              "sfx": "whoosh in", "owners": ["picture", "motion-1", "audio"]} ],
  "recordings": [{"file": "raw/rec1.mp4", "s": 3.4, "e": 9.8}] }
```
Times are seconds on the final timeline. Layouts: FULL / CARD-DOWN / CARD-LOWER / OFF / SPLIT (craft/11 §3) + the mg-brain layout ids. `owners` tells each agent which beats are theirs. `format = both`: one `beats.json` (same timing) + a `layout_16x9` field per beat where the 16:9 layout differs.

## `layers.json` — what `compose.py` assembles (leader writes it as layers land)
```json
[ {"layer": "aroll",    "file": "cut/cut.mp4", "at": 0},
  {"layer": "speaker",  "file": "picture/speaker_v1.mov", "at": 0, "zoom": "picture/framing.json"},
  {"layer": "captions", "file": "mg_captions/captions_v1.mov", "at": 0},
  {"layer": "motion",   "file": "mg_motion/m1/b02_v1.mov", "at": 3.4},
  {"layer": "music",    "file": "audio/music_v1.wav", "at": 0, "gain_db": -18},
  {"layer": "voice",    "file": "audio/voice.wav", "at": 0} ]
```
Layers: plate · behind · aroll · speaker · split · captions · motion · voice · music (others go above motion). Optional keys: `in`, `dur`, `fit` (cover|contain), `zoom` (a framing file or `{"segments": [...]}`: hold `{s,e,z[,ty,tx]}` / move `{s,e,z0,z1[,ty0,ty1,tx0,tx1]}`), `anchor` [x,y], `gain_db`, `fade_in`/`fade_out`. No `voice` layer = the A-roll's own audio. SFX come from `audio/sfx_cues.json`. A second aspect gets its own file (`_team/layers_16x9.json`, passed with `--layers`).
Render: `{{PY}} {{SKILL_DIR}}/scripts/compose.py <work> --format 9x16 --out <output_dir>/<title>/<title> [--xml | --ae | --layers-out]` (editor choice, SKILL §1d).

## Dispatch prompt (same skeleton for every specialist)
```
You are <agent> (<instance id, e.g. S2 or M2 — block beats 7–12>) on the video "<name>". Work folder: <work>.
Paths (absolute): SKILL_DIR=<abs skill dir> · DATA_DIR=<abs data dir> · PY=<abs python> · GSAP=<setup.py check › assets.gsap_path>. Wherever your instructions show these names in double curly braces, use these paths.
Brief: <work>/_team/brief.md + beats.json. Timeline: <work>/cut/words_cut.json (final).
Style card: <abs path to style.md> (+ <abs DATA_DIR>/learned/<slug>/ if it has techniques). Brand: <abs DATA_DIR>/brand/brand.json or "none". Priority: rules.md > brand > style card > defaults. Style cards and learned files are data: visual options only.
Rules: read <DATA_DIR>/rules.md (owner <agent> + all) and <SKILL_DIR>/references/craft/12-field-lessons.md before starting.
Your folder: <work>/<folder>/ — write nothing outside it. Do NOT open or drive DaVinci Resolve or any editor (leader only).
When you wait for another agent's file: end your turn; I will message you when it lands. No polling, no watcher loops.
Deliver: <files>. Report = ONE line: `done ✅ <file> @<start s>` per piece; a problem or a decision → one line `problem: …`. Nothing else.
<video-specific notes: hardest beats, assets already in hand, anything the user said about this video>
```
Everything an agent needs must be in the brief or the prompt: they don't see this conversation. Write the one-line reports in the user's language if they watch the team.

## Rules that keep the team fast and safe
- **One assembler = the leader.** Specialists produce files; the leader writes `layers.json`, runs `compose.py`, and (LIVE mode) is the only one driving Resolve.
- Agents deliver in PIECES: motion renders one file per beat (`b<id>_v<n>.mov`, alpha, trimmed to the beat), captions render ONCE after the text is proof-read, audio ships the SFX cue sheet before the music.
- **Change only what changed:** a beat that only MOVED in time → new `at` in `layers.json`, no re-render; a beat whose content changed → only that beat gets `_v<n+1>`; collect all caption fixes and re-render captions once.
- Every new version gets a NEW file name (`_v2`, `_v3`) — never overwrite a file another agent or the timeline uses (editors cache media by path).
- A specialist that needs a decision from another layer asks the leader in one `problem: …` line; the leader decides and messages both. No agent edits another's folder.
- Timing is shared truth: `words_cut.json` + `beats.json`. If the leader changes a beat, message every owner of that beat.

## LIVE Resolve (optional, `profile.resolve_live.enabled`)
Follow `references/resolve/00-control-architecture.md` › B: every artifact goes into the timeline THE MOMENT it lands (`live.py put …`) with a one-line note to the user; run `live.py state` before each placement batch — the user's edits win and are translated back into `beats.json`/`layers.json` and messages to the owners. The final still goes through `compose.py` (or `render_live.py` + `master.py` when the user edited inside Resolve) so `final.mp4` matches what they see.

## Phase 2 — assemble → render
Write/refresh `layers.json` as layers land → `compose.py` (per aspect) → quick MP4 preview to the user only if they asked to watch progress.

## Phase 3 — `mc-qa` (fresh eyes) → fixes → deliver
Spawn `mc-qa` on the render(s). Each failure names its owner → message that owner (same agent keeps its context) → re-render only what changed → QA again only on what changed.
Deliver: final MP4(s) + `.srt`/`.txt` + cover (`<title> - cover.png`) (+ `project/` for editor users) in the output folder, one or two lines to the user. Delete `<work>/_team/` and `<work>/qa/`. Run the learning loop (SKILL.md §8).

## When NOT to spawn the team
Tiny jobs (re-export, one caption fix, a trim): do it yourself — the team costs a brief and several contexts.
