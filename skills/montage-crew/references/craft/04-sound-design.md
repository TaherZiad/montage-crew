# Sound design & audio post

Research: 27 transcripts + 8 web; every ffmpeg chain verified to parse/run on ffmpeg 9.0.1. Herman Huang (1M), Joseph ×3, Clumzzy, Simply Put, Justin James, Tim Runia, Epidemic/Kyle Lexter, Jacob Nordin (1.08M), James Prince, Adventures in Video, Doctor Mix, Sam Smyers, Claricast, Standard Story Co., Filmmaker IQ, Fandor, Ray Ortega, Derek Lieu, Amuse Cinema, Nerdwriter (Spielberg), Serge Morgotch, Audio Toolshed (TikTok), Austen Menges, Lazy Lakshay; Critical Listening Lab, APU, DaVinci Resolve Club, EBU R37/ITU BT.1359, licensing pages.

## Principles (ranked)
1. Voice is king; everything serves intelligibility (phone speakers keep ~1–4 kHz).
2. Every on-screen motion gets a sound; SFX **peak** on the motion's fastest/blurriest frame.
3. Three families: movement (whoosh) · texture (click, typing, UI, gear, data, highlighter) · emotion (riser, hit, drone).
4. Layer across bands (low+high whoosh; rumble+cymbal riser; whoosh+impact).
5. Carve a pocket for the voice (mid dip, low-pass, de-esser keyed on mids) instead of only lowering music.
6. Tension → release; silence is a tool (riser → impact / silence / "downer"; drop music before a key line).
7. Music by target emotion → style → instruments → tempo → density; switch per section, keep one factor constant.
8. Cut music to the story (loops, drop-outs, ring-outs, reversed-beat entries).
9. One SFX style per video; no riser without payoff; no SFX on every caption.
10. J/L cuts, room tone and 1–3 f fades hide edits; never digital-silence gaps.
11. Compress, then limit, then loudness-target. 12. Check on a phone speaker.

## Levels (voice stem = 0 dB ≈ −14…−16 LUFS short-term, peaks −6…−3 dBFS)
| Element | vs voice |
|---|---|
| Music bed under speech | −18…−24 dB (dense rock/metal −26…−28) |
| Music bed with EQ pocket (−3…−6 dB @1–3 kHz, Q≈0.8) | −14…−18 dB |
| Music in gaps / intro | −6…−10 dB (rises 6–10 dB) |
| Small whoosh | −10…−14 | Big whoosh (in a speech gap) −6…−10 |
| Pop/click/UI | −12…−18; repeats step −12 → −18 → −22 |
| Typing/data/gears | −16…−22 |
| Riser | ramp −30 → −8 at the peak (≤ −14 if over speech) |
| Impact/boom | −3…0 in a gap; −8 if on a word |
| Glitch/shutter/flash | −10…−14 | Shimmer/ding −14…−18 |
| Ambience/room tone | −25…−35 |

## Sync (30 fps, 1 f ≈ 33 ms; audio early > ~40–45 ms is noticed, late tolerated to ~60–125 ms)
- Whoosh: peak on max-velocity frame (file starts 4–10 f earlier), tail fades 3–6 f after stop.
- Pop/click/impact/text slam: transient on the appear/contact frame, 0 to +1 f late, never > 1 f early.
- Hard cut on a music beat: picture 1 f before the beat.
- Riser / reverse suck: ends exactly on the hit/cut; risers 1–3 s, reverse cymbal 0.5–1.5 s.
- Typing: first char → last char, 2 f fade tail.
- J-cut 6–15 f (talking head), 1–2 s for section bridges; L-cut 0.3–1 s.
- Music drop / sound-up: first frame after a sentence ends, or on the B-roll cut.

## Ducking
- Static bed −18…−22 dB + dynamic duck 3–6 dB (2–3 chill, 8–10 dense). Attack 20–50 ms, release 300–700 ms (slow swell back). Duck ~150–300 ms **before** the first word.
- Deterministic envelope from word timestamps (preferred): ramp down 0.3 s before first word, up 0.5–0.8 s after last; treat gaps < 1.2 s as speech. Example duck to 0.4 between 1.2–4.8 s:
  `volume='1-0.6*clip(min((t-0.9)/0.3,(5.4-t)/0.6),0,1)':eval=frame`
- Sidechain (tested):
```
[voice]asplit=2[v][vsc];
[music]volume=-20dB,equalizer=f=2000:t=q:w=0.8:g=-4[m];
[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=450:knee=4:link=maximum[md];
[v][md]amix=inputs=2:normalize=0:duration=first
```
  Lookahead variant: delay program 250 ms (`adelay=250:all=1` on voice+music, undelayed voice to sidechain), then `atrim=start=0.25`.
- Frequency ducking: automate music low-pass open (12–16 kHz) in gaps/titles, 2.5–4 kHz under speech (450 Hz only for a muffled lo-fi feel).

## Voice chain — phone/lav Arabic (48 kHz mono)
**Default: keep the original voice** — static gain to the level target + a transparent limiter (`volume=…dB,alimiter=limit=-1.5dB:level=0`), no EQ/NR/compression, no time-stretch. Use the chain below only when the scout reports a noisy/clipped recording or the user asks for processing.

Arabic: dense sibilants (س ص ش ز ث ذ, 4–9 kHz) + emphatics/pharyngeals (ع ح ق ص ض ط) living at 1–3 kHz → de-ess moderately, never scoop 1–3 kHz.
```
aformat=sample_rates=48000:channel_layouts=mono,
highpass=f=80:poles=2,
afftdn=nr=12:nf=-42:tn=1,
agate=threshold=-45dB:range=-10dB:ratio=2:attack=5:release=250,
equalizer=f=120:t=q:w=1:g=1.5,
equalizer=f=350:t=q:w=1.4:g=-3,
equalizer=f=3200:t=q:w=1.2:g=2.5,
highshelf=f=10000:g=2,
deesser=i=0.4:m=0.5:f=0.5,
acompressor=threshold=-21dB:ratio=3:attack=10:release=150:knee=4:makeup=4dB,
acompressor=threshold=-10dB:ratio=6:attack=2:release=60:knee=2,
alimiter=limit=-2dB:attack=3:release=60:level=0
```
- Noisy phone: afftdn `nf=-35 nr=15–20` (max ~20, else watery). AI NR: `arnndn=m=cb.rnnn:mix=0.8` (model from GregorR/rnnoise-models; mix 0.7–0.85).
- 120 Hz boost only for thin lav (skip if boomy); lav under clothes: +3…+4 dB at ~4 kHz; skip high shelf if already sibilant; harsh س/ش → deesser i 0.5–0.6. Mouth clicks: `adeclick` before EQ. Very uneven levels: `speechnorm=e=6.25:r=0.00001:l=1` instead of compressor 1.
- `deesser f` is normalised 0–1 (not Hz). `amix` always `normalize=0`.
- Master (mix bus): pass 1 `alimiter=limit=-1.5dB:level=0,loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json`; pass 2 with measured_* values and `linear=true`.
- Targets: one master at **−14 LUFS, TP −1.5 dBTP, LRA 6–7** works for YouTube/Reels/TikTok. Don't master hotter than −12 (TikTok's in-app limiter pumps); trim < 60 Hz.

## SFX map
| Event | Sound |
|---|---|
| Text/caption slide | light whoosh (short, high) |
| Punch zoom | deeper whoosh (+ sub thump on hard zoom); not every zoom |
| Big camera move / full-frame | low + light whoosh layered |
| Whip / fast transition | whip whoosh (+ glitch if digital) |
| Section transition | whoosh → impact, or reverse suck → impact on cut |
| Keyword pop / sticker | click / pop / bubble, descending on repeats |
| Keyword slam / big number | impact (+ small riser before), pitch-matched to beat |
| Typewriter | keyboard ticks (hook only) |
| Number counter | fast ticks / data; coins/cash register for money; ding on final number |
| Underline / circle / arrow draw | marker/highlighter scribble |
| Mechanical letters / dotted line | gears, ratchet |
| UI card / notification | UI beep, notification, mouse click |
| Glow / checkmark / aha | shimmer, bell ding |
| Glitch / RGB | glitch/data burst + camera flash |
| Flash / screenshot | camera shutter |
| Split / door reveal | slide / door mechanical |
| Build-up | riser (rumble + cymbal) ending on reveal |
| Reveal / key stat / punchline | impact, OR silence |
| Fake drop | riser → downer → riser → impact |
| Timer / urgency | clock ticks, heartbeat |
| Mood / location B-roll | ambience −25…−35 dB, J/L-cut edges |
| Comedy | meme SFX, record scratch, whip (brand-permitting) |
Density: hook ≤ 6–8 SFX / 10 s; body ≤ 3–5 / 10 s; risers ≤ 1 / 15–20 s; impacts ≤ 1 / 8–15 s; ≤ 2–3 layers per event; keep 150–200 ms between unrelated transients; no transient on a stressed syllable — use micro-gaps.

## Music
| Content | Mood | Genre | BPM |
|---|---|---|---|
| Hook / hype | high energy | trap, EDM, hybrid percussion | 120–150 |
| Tech/business explainer | modern minimal | lo-fi hip-hop, minimal trap, pads | 90–110 |
| Tutorial / calm | chill focused | lo-fi, soft keys, ambient | 70–95 |
| Success / reflection / CTA | uplifting | piano + strings build, indie-pop | 90–120 |
| Money truth / warning / story | dark tense | dark synth, drones, pulses | 60–110 |
| Setback / emotional | sad | solo piano, cello — or silence | 60–80 |
| Big reveal | cinematic | orchestral hybrid, braams | 90–130 |
| Comedy | goofy | pizzicato, ukulele, 8-bit | 100–130 |
| Arabic religious / sensitive topics | — | many audiences prefer no instruments: ambience, drones, SFX only — **ask the user** | — |
- Match BPM to speech pace (80 / 100–110 / 120–130). Instrumental only under speech; mute clashing stems.
- Cut at the track's own section boundaries, on downbeats (picture 1 f early); loop whole bars with 2–4 f crossfade offset 1 f; drop on the payoff line or first B-roll after a sentence; mute one word before the punchline and return on the next beat.
- Enter: fade 0.5–1 s, swell, or the track's own first beat reversed as a riser (in key). Transitions between tracks: riser, reversed tail, whoosh, record scratch, tape-stop/pitch-down.
- End: back-time the real ending; or ring-out (cut before next beat, long reverb `aecho=0.8:0.7:60|120:0.4|0.3` or IR, fade 1–2 s); or impact + silence. Never a random fade or mid-bar stop.
- Legal sources: YouTube Audio Library (YouTube only; some CC-BY), Pixabay Music (keep certificate for Content ID), Uppbeat free tier (credit), Meta Sound Collection (IG business), TikTok CML (business); SFX: the bundled CC0 SFX library `assets/sfx/` first (see its `manifest.json`); extra: Freesound (check CC0/BY), Sonniss GDC. Avoid BBC SFX commercially.

## Idea bank
reversed first beat as intro riser · ring-out reverb on last hit · riser → silence (smash cut) · fake drop · 2-riser stack · 3-band whoosh · impact pitch-matched to snare/kick · descending pop levels · automated music low-pass (open on titles) · 1–3 kHz EQ pocket · pre-ducking before first word · J-cut next sentence 6–10 f under B-roll · L-cut last words over reveal · next section ambience 1 s early · non-literal "emotional realism" sounds · phone/radio voice for quotes (`highpass=f=400,lowpass=f=3400` + slight distortion) · underwater memory (`lowpass=f=600` + reverb) · cash register/clock/heartbeat · pan whooshes ±30 % with motion · tape-stop interruption · room-tone patch + 2 f fades · cut inside words to hide intonation jumps · section-based music with one constant factor · silence on the most important sentence · ambience bed −30 dB so jump cuts feel continuous.

## Audio QA
1 voice peaks −6…−3 dBFS pre-master, no clipping · 2 every word clear at 30 % phone volume with music/SFX · 3 bed 18–22 dB under voice, rises only in gaps, duck anticipates first word, no pumping · 4 SFX peaks 0…+1 f on motion (scrub 5 biggest moments) · 5 ≤ 5 SFX/10 s in body, none on stressed syllables · 6 room tone under cuts, 1–3 f fades, no clicks · 7 music edits clean; ending rings out / back-timed · 8 no harsh س/ش (6–9 kHz check) · 9 nothing needed < 60–80 Hz, no plosives · 10 `ebur128=peak=true`: I −14 ±0.5, TP ≤ −1.5, LRA ≤ 7 (≤ 6 short-form) · 11 listen on phone speaker, earbuds, laptop; mono fold `pan=mono|c0=0.5*c0+0.5*c1` · 12 licences logged per track/SFX.
