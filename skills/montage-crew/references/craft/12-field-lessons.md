# craft/12 — field lessons (defaults learned on real deliveries)

Each lesson below was paid for on a real video: a correction from the creator or a defect QA found. They are the skill's DEFAULTS. The user's own `{{DATA_DIR}}/rules.md` wins over anything here (newest rule wins). Owner in brackets = the agent (pro mode) or step (fast mode) that applies it; `check:` = how QA verifies it.

## Cut (cutter)
- **Never cut into a word.** Cut edges sit where the voice energy has fallen to the noise floor (< −45 dB, or floor + 5 dB), never on Whisper end-times; extend the tail in 20 ms steps until quiet. check: RMS at every join and removal edge ≥ 40 ms below speech level on both sides.
- **Remove every retake, repeat, fragment, cough, set word and aside; keep the best (usually last) complete take.** A single "word" longer than ~0.9 s is a suspect hidden repeat (Whisper merges a doubled phrase into one long word): split at the energy dip and re-transcribe. Also remove any hum, throat-clear or «احم» before the FIRST word — the video opens on the first word. check: re-transcribe the render and search for doubled phrases.
- **Cut eye-glances / look-aways between sentences** (glancing at notes or off camera before speaking). check: one eye sheet of the 0.6 s before every sentence start.
- **Sentence joins across takes need ≥ 0.2 s of room tone; level-match takes before the master.**
- **Tight joins by default: ≤ ~0.12 s of air between sentences**, also at hook ends, section changes, before the CTA and between CTA lines; keep a longer pause only where it is a chosen dramatic beat. check: `silencedetect -45 dB, d ≥ 0.15 s` on the voice = 0 hits except chosen pauses.
- **End on the last spoken word — no tail, nothing on any track runs past it** (unless the brief has an outro). The last word must decay NATURALLY: no fade over the word itself, keep ~0.25–0.3 s of room tone after its true end and fade only that. check: the last word's final 100 ms decays ≥ 20 dB over ≥ 60 ms (no cliff) and ≥ 0.25 s of floor follows.
- **Finish the cut, then report once.** Never rewrite `cut/` after other agents started using it — a late re-cut desyncs the matte and every layer.

## Picture (picture)
- **Keep the ORIGINAL pixels of the speaker** by default: no grade, relight, retouch, sharpen or denoise on the face. A cut-out over a plate only. check: face-crop mean difference vs `cut.mp4` < 2/255, measured ONLY on opaque speaker pixels (alpha ≥ 254). A composite must reuse `cut.mp4`'s own pixels where alpha = 1 (a re-encode alone costs ~1.5/255) and keep any rim light off the face box.
- **Main frame: the speaker at FULL size 1.00 — never scale below 1.00, never extend/inpaint/invent pixels at the frame edges** (scaling down always exposes edges; fake fills and shadows don't hide it). Free space by placement, not scaling.
- **Background = the original footage** unless the user asks for a replacement in that video (craft/09 §8).
- **Measure face landmarks** (hair top, eyes, chin) on a full-resolution frame with a 100 px grid before the brief — never estimate them from a scaled contact sheet (a guessed chin 270 px off gave every agent wrong bands).

## Layout (motion + leader)
- **"PiP rect/circle" means the SPEAKER's video shrinks into the shape and the MG takes the screen** — not the MG in a small shape. Circle: face + neck + shoulders, hair fully inside. Rect: a bit more of the body. Never a face-only crop.
- **Mix layouts**: ≥ 3 modes per video (small split, PiP rect/circle, FULL with overlay, takeover); never every beat in a half split. A split stage ≤ ~40 % of the height; no side-by-side split in 9:16.
- **Nothing on the eyes, face or hair — including during layout transitions** (a 0.8 s layout move can sweep across the face); nothing decorating the speaker's card.
- **MG size MEDIUM; one hero object per beat filling its stage; real, detailed UI; never small icons in an empty panel; the stage is never empty.**
- **Every tile/card different** in walls/grids/feeds: no repeated image or title side by side, each matching what is said.
- **When the user points at another video as a reference for "how", they mean how it is PRESENTED (layout, pacing), not its graphic style** — keep this video's own MG look. Ask one short question with 2 concrete options when unclear.
- **No stray elements**: rings/sparks/particles must not render before their moment. check: a 6-frame sheet per beat including frame 0.
- **9:16 platform rails**: every MG and caption pixel inside x 190–890 for y 700–1480; in split layouts every MG element ends at y ≤ 1470. **No emoji glyphs in HyperFrames renders** (headless Chrome draws some as dots) — use inline SVG icons (e.g. Lucide). check: zoom crop of every bubble/label; `overlay_check.py` bottom band.
- **Background change on a gesture** (snap/clap) = a HARD CUT on the exact frame of the gesture's sound — no flash, wipe or delay. check: the change lands within the frame holding the transient.
- **Smooth camera by default**: zooms are eased (in-out ~0.9–1.0 s), no snapped punch-ins and no white flashes unless the brief picks a snappy personality.

## Captions (captions)
- **Default: captions of everything said**, 2–3 words, on the chest (9:16 ≈ y 1220; under the chin in split/PiP beats), never before the word is spoken.
- **Hook, captions and logos never overlap**: the hook is gone before the next element enters its band; never caption a word a logo on screen already shows.
- **Keep real spaces around highlighted words** (a glued «علىتحميل» shipped once). check: a sheet of every highlighted word.

## Audio (audio)
- **The creator's ORIGINAL voice by default**: static gain + a transparent limiter only, no processing chain, no time-stretch (a chain sounded "robotic, hissy, not my voice"). Clean-up only for a noisy/clipped recording or on request.
- **SFX: few and varied** (~14–20 per minute-long video) on real motion hits only; no whoosh on every zoom; a quiet pocket before the payoff; master −14 LUFS / ≤ −1.5 dBTP.

## Leader / process (leader)
- **Reply to the user in their language/dialect**, short.
- **A new project/work folder per video, named after the video's IDEA** (ASCII slug for folders, the Arabic title for the final file) — never v001-style codes.
- **Ambiguous request → ONE short question with 2 concrete options** before dispatching; never redo parts the user didn't criticise.
- **Speed**: agents in parallel, nobody waits for another; show one sheet of a new direction before rendering everything.
- **Waiting agents stop**: an agent waiting on another's file ends its turn — no polling or watcher loops; the leader messages it when the input lands.
- **Never overwrite a file another agent or the timeline already uses** — every new version gets a new name (`_v2`, `_v3`).
- **One final render per video**: one timeline, one render job, one output name; revisions re-render the same job/name.
- **Place pieces frame-exact** (`--at f/30`), and check a render sheet before delivery.
- **Screen recordings of the editor or desktop for a video: capture ONLY the app window, never the whole desktop** — private chats and windows get caught.
