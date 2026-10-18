# Fairlight audio & subtitles (Resolve 20/21) — Arabic reels

> For users whose profile editor is DaVinci Resolve (free or Studio). The skill always delivers `final.mp4` + an FCP7 timeline XML to import (File > Import > Timeline); this file is for finishing/editing in Resolve after that import. Optional LIVE mode (driving Resolve directly): `references/resolve/00-control-architecture.md`. Features marked **Studio only** are missing or watermarked on the free edition.

Research: 20 transcripts (7 Arabic) + 4 frame grabs + 10 web. Jason Yadlovski ×5, Greg Edits Video, Casey Faris, That Media Prof, Cine, 3lemny (AR), Alex Pettitt, MrAlexTech ×2, ALHASHMI (AR), Katobee (AR), Tamawy_Editor (AR), Khaled MeGa (AR), Amr Atallah (AR); Resolve 20 / 20.2 / 21 New Features Guides, Newsshooter 21.1, xere.my, AutoSubs issues #847/#848, X-Raym API doc, Digital Production.

## Key facts
- Arabic auto-subtitles are **Studio only** (Resolve 20+: Extras Download Manager → Extended Transcription Language Support ~1.76 GB beta → Project Settings → Subtitles → Enable Extended Language Support). **Free: none.** Scripting constants have no Arabic.
- Built-in **Animated (word-highlight) subtitles**: **Studio only**; RTL reported broken for Arabic/Hebrew (MrAlexTech) — treat as broken.
- Resolve 21: import SRT + "Update/Synchronize Word Timings" (Arabic unverified); subtitle Find & Replace; subtitle fades; Font Browser.
- 21.1 free removed Python/advanced scripting → Workspace > Scripts plugins (AutoSubs, Caption Pro) broken on free 21.1.
- **Our Arabic caption path = external**: `scripts/transcribe.py` (faster-whisper word timestamps) → HyperFrames word-by-word captions rendered to alpha overlay (V2+) — or SRT import for plain line captions (free).

## Voice chain in Fairlight (order: clip gain → Voice Isolation → Dialogue Leveler → EQ → Dynamics → De-esser → DIA bus → Main limiter)
| Step | Setting |
|---|---|
| Gain staging | Normalize Audio Levels → Sample Peak, −10 dBFS (or AI Level Matcher); dialogue peaks −12…−10 |
| Voice Isolation (**Studio only**) | 40–60 normal, 80–90 heavy noise, never 100 (watery); also removes reverb |
| Dialogue Leveler (free) | defaults, output gain back to ~−10 dB |
| EQ (6 bands) | HPF 90–120 Hz · −3 dB @250–450 Hz Q≈1.4 · −2 dB @0.8–1.2 kHz only if nasal · +2–3 dB @3.5–5 kHz · +1.5 shelf @10–12 kHz only if dulled · optional LPF 16–18 kHz |
| Dynamics | **Expander** (not hard gate — protects soft ح خ ه ع): threshold −45…−40, range 10–12 dB; Compressor 3–4:1, attack 5–10 ms, release 80–150 ms, 3–6 dB GR, make-up to ~−10 dB peaks |
| De-esser | "Male S"/"Female S", −3…−6 dB around 5–8 kHz; check س ص ش ز |
| Dialogue Matcher (Studio only) | phone vs lav matching |
| Save | Presets Library → Global Track Preset "DIA-AR" |
AI Audio Assistant (Studio only): set track categories first, choose delivery standard, Auto Mix — a first pass only.
**Default:** keep the original voice (static gain + transparent limiter, craft/04) — it arrives already levelled in `final.mp4` and the XML audio; in Resolve just level/duck. Process only when the scout reports a noisy/clipped recording or the user asks: `scripts/audio.py voice` (ffmpeg chain from craft/04) before import on free, or the chain above (Voice Isolation is Studio only).

## Ducking, music, SFX
- Tracks A1 DIA (mono), A2 ROOMTONE, A3 MUSIC, A4 SFX; buses DIA/MUS/SFX → Main (limiter). 21: folder tracks.
- **Ducker** (music track Inspector; source = dialogue): Duck Level −12…−18 dB, Look Ahead 100–150 ms, Rise 150–250, Hold 300–500, Recovery 600–1000 ms.
- Sidechain compressor (MUS bus, source = DIA bus — one source only): 4–6:1, 8–12 dB GR, attack 10–20 ms, hold 200–400, release 400–800; Listen off.
- Music 10–20 dB under dialogue (~−28 dBFS under −10 dialogue) + EQ dip −2…−4 dB @1.5–4 kHz; automation for swells.
- SFX: free Fairlight Sound Library (~500 WAVs, Blackmagic Support download); whoosh 1–2 f before a cut, hits on the frame; peaks −18…−24 dBFS.
- Jump cuts: default 1.5 ms soft fades (20.2 toggle); clicks → 2–4 f audio-only crossfade (0 dB same voice, +3 dB different); Ripple Delete Silence (Edit page 20.2: Threshold, Pre Head, Post Tail, Minimum to Strip); room tone under gaps. J/L: linked selection off / Alt-drag; next line 3–6 f early on hooks.

## Loudness
Project Settings → Fairlight → Loudness Standard YouTube (−14 LUFS) (meter only); Main limiter ceiling −1.0 (−1.5 safe) dBTP; Analyze Audio Levels (Clip Operations) or play through; Main fader to −14 ±1 integrated, TP ≤ −1. Reels/TikTok: −14 safe (don't exceed −11). Normalize is per clip (not a mix master); Deliver Output Track = Main. Our pipeline: final `scripts/audio.py master` after render guarantees −14 / −1.5.

## Subtitles (native)
Create Subtitles from Audio (Studio only): language, preset, chars/line (reels 14–20; Arabic tutorial ~10), single line, gap 0. Styling (Track tab): Arabic font (Cairo/Tajawal/IBM Plex Sans Arabic/Noto Kufi/Almarai — confirm glyphs), 64–80 size at 1080×1920, background box black 60–75 % rounded or shadow, **stroke 0** (reported Arabic glyph loss), Y ~30–35 % from bottom; Fusion title template on subtitle track header overrides styling (20). Export: Deliver → Subtitle Settings → Burn into video / Separate file (SRT/WebVTT) / Embedded (IG/TikTok = burn in).
Free SRT route: external SRT (UTF-8) → File > Import > Subtitle or drag onto timeline → style → burn in; add RLM (U+200F) after trailing punctuation; check mixed Arabic/Latin/numbers.

## Scripting (LIVE mode only)
`timeline.CreateSubtitlesFromAudio({...})` (Studio only; no Arabic constant) · `SetVoiceIsolationState(track, {"isEnabled":True,"amount":50})` (Studio only) · SRT: `mp.ImportMedia([srt])`, `tl.AddTrack("subtitle")`, `AppendToTimeline` (forum-reported, test) · Text+ captions via `InsertFusionTitleIntoTimeline("Text+")` + `StyledText` · render burn-in `SetRenderSettings({"ExportSubtitle": True, "SubtitleFormat": "BurnIn"})` · 21.1 audio-normalization API (`NormalizeAudioLevel`).

## Mistakes / QA
Voice Isolation 100 % · hard gate chopping gutturals · normalizing clips instead of mixing Main · sidechain Listen left on · music & dialogue on one track · font without Arabic glyphs / stroke > 0 · assuming animated subtitles do RTL · upgrading free to 21.1 while relying on Python plugins (one-way DB upgrade — back up) · relying on API language constants for Arabic.
QA: −14 ±1 LUFS, TP ≤ −1 · phone speaker + earbuds · no clicks, room tone under gaps · ducking without pumping · captions joined, RTL, punctuation side correct, dialect words fixed, safe zone · watch the burned-in render end to end.
