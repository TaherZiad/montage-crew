# SFX library (montage-crew)

84 cleaned one-shots in 27 category folders. **All of them are CC0 1.0**: 71 come from Freesound.org and 13 from Kenney packs. Credits are in `CREDITS.md`, and each file's source is in `manifest.json`.

All files are MP3 at 48 kHz: stereo files are 192 kbps and mono files are 128 kbps. Each file was trimmed of leading and trailing silence below -50 dBFS, with a 10 ms pre-roll kept. Each file is peak-normalized to -1 dBFS, so every file peaks at the same level. Set the level on the timeline, not in the file. Long sources were cut to a usable length (typing beds 4 s, swells 6 s, risers 2 s ending on their peak).

`manifest.json` lists every file with `file, category, source_page_url, file_url, licence, author, source_title, duration_s, peak_time_s, loudness_db, loudness_type, channels, note`.

## How to place a sound

`peak_time_s` is the time of the loudest 10 ms RMS window, which is where the ear hears the hit.

```
clip_start = visual_hit_time - peak_time_s
```

- Risers, reverse swooshes and the UI "maximize" swipe have a late peak, near the end of the file. Put the peak on the cut or on the word, so the build plays before it.
- Impacts, pops, clicks, ticks and dings have a peak close to 0. They start on the frame.
- Beds (room_tone, drone_tension, clock, typing) have a peak that means little. Start them at the section start and fade them in and out over 0.3–0.5 s.
- `loudness_db` is integrated LUFS for files of 0.4 s or longer, and RMS dBFS for shorter files (see `loudness_type`). Use it to compare files: two files at the same fader setting can still sound different (for example `transition_swipe_06_fast-swipe` is spiky and reads quiet).

## Categories

| folder | use | count |
|---|---|---|
| whoosh_soft | gentle movement, B-roll in, soft text slide (10/11 = long cinematic pass) | 5 |
| whoosh_fast | hard cuts, whip pans, fast punch-ins | 4 |
| swoosh_reverse | suck-in before a cut or reveal (the peak is at the end) | 4 |
| transition_swipe | UI/screen swipes, card slides, paper slides | 4 |
| riser_short | 2 s lift into a punchline or reveal (ends on its peak) | 3 |
| riser_long | 2–6 s build into a big reveal or hook payoff | 2 |
| impact_sub | boom / sub hit on a hero word, logo or number | 3 |
| impact_soft | soft thud for text landing, stickers, captions | 3 |
| click_ui | button presses and toggles in screen recordings | 3 |
| tick | counters, checklist items, rapid list beats | 2 |
| pop | emoji, sticker, bubble or icon pop-ins | 3 |
| typing | prompt typing, code, search bars (4 s beds) | 4 |
| mouse_click | cursor clicks in screen demos | 3 |
| camera_shutter | screenshot or freeze-frame moments | 2 |
| paper | document, notes or page reveals | 2 |
| glitch | tech errors, AI "hallucination", hard stylised cuts | 4 |
| shimmer | magic moments, "AI did it", sparkle reveals | 3 |
| ding | success, notification, "done" | 5 |
| error | wrong answer, fail, denied | 3 |
| swell | cinematic swell or breath under a big line | 3 |
| drone_tension | low bed under a problem or suspense section | 2 |
| scan | laser, scanner or data analysis visuals | 3 |
| bass_drop | drop after a riser, "and then..." moments | 3 |
| cash | money, pricing, revenue, "free" beats | 2 |
| clock | time pressure, deadlines, heartbeat tension | 3 |
| text_reveal | airy, light whoosh or breath for single words | 3 |
| room_tone | 8 s quiet room beds that fill gaps and J-cuts | 3 |

File numbers have gaps on purpose. Names are kept stable so they can be traced to their source.

## Recommended level vs voice (voice mixed at about -14 LUFS / dialogue peaks around -6 dBFS)

These numbers are fader gain applied to the -1 dBFS-peak file.

| category | gain | note |
|---|---|---|
| whoosh_soft, whoosh_fast, transition_swipe, swoosh_reverse | -10 to -14 dB | lower (about -16) when under speech |
| text_reveal | -14 to -18 dB | should be felt more than heard |
| pop, click_ui, tick, mouse_click, typing, camera_shutter, paper | -12 to -18 dB | typing beds -20 dB |
| ding, error, cash | -10 to -14 dB | -16 on top of words |
| shimmer, scan, glitch | -12 to -16 dB | glitch can reach -8 in a gap |
| impact_soft | -10 to -14 dB | |
| impact_sub, bass_drop | -3 to 0 dB in a gap; about -8 dB on words | high-pass the voice or duck it by 2–3 dB around the hit |
| riser_short, riser_long | automate a ramp from about -24 dB to -8 dB at the peak | cut or duck it right after the peak |
| swell | -12 to -16 dB | |
| drone_tension | -22 to -28 dB | duck it under speech |
| clock (ticking or heartbeat bed) | -20 to -26 dB | single heartbeat-sub: -8 to -12 |
| room_tone | -25 to -35 dB | only to fill cuts or silences |

Rules of thumb: use no more than one hero SFX per sentence, and never stack two impacts inside 300 ms. Riser plus impact or drop is one gesture.

## Adding your own sounds

Only add a sound whose licence lets you **put it inside a package**. CC0 (Freesound filtered to "Creative Commons 0", Kenney) is safe. Don't add Mixkit, Pixabay or Sonniss GDC files to a copy you share: their licences forbid redistributing the files, even for free. You can still use them in your own videos.
