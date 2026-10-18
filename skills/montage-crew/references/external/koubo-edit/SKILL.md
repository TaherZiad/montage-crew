---
name: koubo-edit
description: Analyze and assemble Chinese talking-head or spoken-content footage with repeated takes. Use when Codex needs to transcribe a folder of raw videos, group semantically equivalent content, select the best take for each idea, arrange selected ideas into a coherent order, remove boundary pauses, generate precisely timed subtitles, or produce an auditable edit manifest before rendering to FFmpeg or JianYing.
---

# 口播剪辑

Treat this skill as the editorial decision layer. It decides *what* to keep and exactly where every cut and subtitle belongs. A renderer or the JianYing adapter decides *how* to create the project and export media.

## Requirements

- Use Python 3.9 or newer and install `ffmpeg`/`ffprobe` for media inspection and audio analysis.
- Treat Volcengine as an optional bundled ASR adapter. Copy `.env.example` to `.env` only when using it; never commit `.env`. Confirm service access against the [official flash-ASR API documentation](https://www.volcengine.com/docs/6561/1631584?lang=zh).
- Supply any other ASR provider by normalizing its output to [data-contract.md](references/data-contract.md).
- Install `jianying-editor` separately only when creating a JianYing draft. Pass its root with `--jianying-skill-root` or `JIANYING_EDITOR_SKILL_ROOT`.

## Workflow

1. Read [data-contract.md](references/data-contract.md) before creating or changing project artifacts.
2. Inventory the source files with stable IDs and immutable fingerprints.
3. Transcribe every source before attempting content understanding. Require verbatim, word-level timestamps; preserve fillers, repetitions, and obvious false starts.
4. Cache the normalized transcript for each unchanged source. Preserve provider word confidence when available; treat zero-only confidence as unavailable rather than low confidence.
5. Run `analyze_speech_islands.py` to create candidate speech islands and acoustic evidence. A long pause is only a candidate boundary, never an automatic split.
6. Read the complete transcript corpus and create `topic_map.draft.json` before applying relevance filtering. Recover every intentionally recorded subtopic, its narrative purpose, supporting sources, and intended order.
7. Classify every island as `valid`, `invalid`, or `needs_review` inside its assigned subtopic. Use loudness, relative level, SNR, and ASR confidence only as supporting evidence; no acoustic metric may auto-reject content by itself.
8. Allow a long-pause split only when both adjacent islands are valid, independently meaningful, and not a false-start/correction or duplicate pair. If only one side is valid, keep that side and remove the other side plus the unused gap.
9. Create a compact, time-addressable transcript view, then split valid speech into semantic beats. A beat is one intended idea or shot, not necessarily a whole source file or a sentence.
10. Group candidate takes by equivalent meaning. Near-verbatim wording is not required. Do not merge ideas merely because they share keywords.
11. Choose one candidate per beat using the selection policy in [editorial-policy.md](references/editorial-policy.md). Escalate to short visual/audio evidence only for uncertain cases; do not run multimodal review across every source by default.
12. Create `edit_manifest.draft.json` with source ranges, reasons, topic membership, output order, boundary settings, and playback policy. Present the topic map and editorial strategy, explicitly ask whether playback speed should remain `1.0` or use a user-approved multiplier, and wait for approval before copying assets, creating a draft, or rendering.
13. After approval, copy the draft manifest to `edit_manifest.json`, set `status` to `approved`, record the approved playback/pitch settings, create selected-asset copies, calculate output-timeline word and subtitle timestamps, and send only that approved manifest to the renderer or JianYing adapter.
14. For a macOS JianYing draft, stage selected media in JianYing's own `User Data/ImportedMedia/<project>/` directory before building the draft. Prefer hard links; copy only if linking is unavailable. Preserve the original path in `source_original_path` and use the staged path in the JianYing manifest.
15. Generate subtitle cues from word timestamps using the adaptive policy in [editorial-policy.md](references/editorial-policy.md): combine semantic completeness, punctuation, source pauses, display length, display duration, and lexical-boundary protection. Use sentence-by-sentence captions only when the user explicitly requests that mode. Remove punctuation only after segmentation when requested, and time every cue from its first to last spoken word on the final output timeline.
16. Verify every cut boundary, staged-media reference, subtitle offset/text, subtitle position, duration, and expected output file. Keep source files untouched.

## Non-negotiable rules

- Use word-level ASR as evidence. Never make a cut inside a spoken word.
- Do not normalize transcript text before grouping or selection; fillers and retakes are editorial signals.
- Do not equate a long pause with two usable scenes. Both adjacent speech islands must pass the semantic gate before the pause can become a split.
- Do not treat low volume, low SNR, or low ASR confidence as proof that a shot is invalid. Combine acoustic evidence with semantic completeness, topic relevance, and speaker role.
- When provider confidence is missing or zero-only, mark it unavailable. Never treat placeholder zeros as genuine low-confidence words.
- Prefer the later complete correction over an earlier false start, but preserve genuinely additive follow-up information.
- Preserve every intentionally recorded subtopic by default. Apply relevance filtering and case limits within each subtopic, not across the entire video.
- Never delete a complete, coherent subtopic merely because it is less related to the title or dominant topic. Require an explicit user instruction or approval to remove an intentional subtopic.
- Treat the ASR engine as a provider, not part of the workflow. Normalize every provider into the schema in `data-contract.md`.
- Select by semantic beat, never by source file alone.
- Preserve an auditable reason for every selected and rejected finalist.
- Recalculate subtitle cues in output-timeline coordinates after every selected range and order change.
- Keep playback speed at `1.0` unless the user explicitly requests or approves another multiplier. Ask about playback speed as part of manifest approval; never inherit a previous project's speed. Record speed and pitch-preservation policy in the approved manifest, then recalculate all output video and word timings.
- Never make a macOS JianYing draft reference selected source media under Desktop, Documents, Downloads, removable volumes, or other user-granted locations. Stage it under JianYing's imported-media root first, then verify every draft media path exists.
- Do not use an ASR paragraph/utterance as one subtitle cue merely because it has one timestamp range. Split the display into natural Chinese sentence/clause cues while retaining word-derived start and end times.
- Do not split captions by sentence boundaries alone. When a spoken sentence is too long, prefer a meaningful clause boundary supported by punctuation, a real source pause, a discourse connector, or semantic completion. Enforce the approved character and duration limits without cutting inside protected words or leaving avoidable grammatical fragments.
- When the requested subtitle style omits punctuation, remove punctuation only from display text after timing and sentence splitting. Never delete timing words or use proportional timing as a substitute for word timestamps.
- For `position_y` supplied in JianYing UI pixels, set `ClipSettings.transform_y = position_y / project.height`. Example: on a 2160×3840 project, UI `-1900` is `-0.4947916667`, not `-0.9895833333`.
- Do not rely on model judgment alone for an ambiguous visual or audio tie. Generate a short evidence view of only the finalists.
- Do not render or modify a JianYing draft until the user approves the draft manifest, unless they explicitly request automatic execution.

## Default editorial policy

Use the following priority order unless the user changes it:

1. Preserve the intended information completely and in a logically coherent order.
2. Prefer natural delivery with no false start, verbal mistake, or unwanted repetition.
3. Prefer intelligible, clean audio.
4. Prefer stable, well-framed visuals.

Playback speed is project-specific, not a universal enhancement. If the user has not specified it, ask during plan approval and use `1.0` unless another value is approved. Preserve pitch unless the user requests otherwise.

For seamless talking-head assembly, trim each selected range at word boundaries with a small configurable safety pad and apply a short audio fade at the exposed edges. The pad, fade, playback speed, and pitch policy belong in the approved manifest; do not silently invent or reuse them from another project.

## Output contract

Keep every generated artifact under `<project>/edit/`:

```text
edit/
├── source_index.json
├── transcripts/
├── speech_islands.json
├── takes_packed.md
├── topic_map.draft.json
├── beats.draft.json
├── edit_manifest.draft.json
├── edit_manifest.json
├── selected/
├── subtitles.srt
├── subtitles.ass
├── preview.mp4
└── validation.json
```

Use `edit_manifest.json` as the only handoff contract to a renderer or the JianYing adapter. Do not encode editorial decisions directly in a rendering script.

## Prototype scripts

- `scripts/scan_media.py <source_dir> --project-dir <project_dir>`: index only original source media; write dimensions, display rotation, frame rate, duration, audio presence, and the dominant project profile.
- `scripts/transcribe_volcengine.py <source>`: transcribe one source with the configured Volcengine flash ASR provider.
- `scripts/transcribe_batch_volcengine.py --index <source_index.json> --project-dir <project_dir>`: transcribe every indexed raw source, cache unchanged results, and never scan `selected/` or render-output folders.
- `scripts/analyze_speech_islands.py --index <source_index.json> --project-dir <project_dir>`: find candidate long-pause boundaries, calculate relative loudness/SNR evidence, and emit semantic gates that must be resolved before splitting.
- `scripts/pack_transcripts.py --index <source_index.json> --project-dir <project_dir>`: create `takes_packed.md` from every completed transcript; refuse to produce a partial corpus.
- `scripts/compile_editorial_plan.py --plan <editorial_plan.json> --project-dir <project_dir>`: validate word-boundary selections, resolve semantic gates, and compile `beats.draft.json`, `edit_manifest.draft.json`, and draft validation without rendering.
- `scripts/adaptive_subtitles.py`: reusable, dependency-light dynamic-programming caption segmenter used by render adapters.
- `scripts/stage_jianying_media.py --manifest <approved_manifest>`: stage selected sources under JianYing's imported-media root and write a separate JianYing manifest; accept `--media-root`, `--output`, and `--project-name` overrides.
- `scripts/build_jianying_from_manifest.py --manifest <jianying_manifest>`: generate adaptive word-timed subtitles and create an editable JianYing draft. Run with `--dry-run` first to validate timing and emit SRT/validation without requiring JianYing; omit `--overwrite` unless replacing a draft is explicitly authorized.
