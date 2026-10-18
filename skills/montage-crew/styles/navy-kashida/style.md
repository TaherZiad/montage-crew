# navy-kashida — painted navy, cream kashida titles, glass arch and liquid tag
best for: authority/explainer talking heads, finance, education, calm premium
kind: look · source: built-in (style-dna B) · learned: built-in · learn focus: whole edit

## Look
palette: bg #00213C (navy) · text #D0B6A1 (cream) + white · accent steel-blue 3D (measured)
type: IBM Plex Sans Arabic 300/700 · animated kashida on the key word · outline hook + small Latin subline
layout: tilted 3D UI card rises centre, arch blur panel (round bottom), liquid tag beside the head · depth: ghost letters at 10 % behind, blurred paper blobs in front

## Pacing
24.3 s @60 · W/MCU 180 % cuts every 2–5 s · 3–10 % push-in per shot, last shot pulls out · one 5 s graphics-free breather (measured)

## Captions
closest CAP-26 Kashida Stretch or CAP-01 Soft Phrase · cream text, steel accent · reveal RTL 2 f stagger, kashida grows after

## Motion graphics
| what | enter | hold | exit | SFX | id |
|---|---|---|---|---|---|
| kashida title | head rises f0–6 → bar scaleX f4–16 quart.out → tail f14–22 | beat | cut | soft whoosh | T-KASHIDA |
| tilted 3D card | rotateX 25→12° rise 12 f | beat | cut | whoosh | C-3D-EDGE-CARD |
| liquid tag word-swap | swap 6–8 f | per word | cut | tick | C-LIQUID-TAG |
| glass slab + icon | slides in while speaker shifts aside, icon tumbles | beat | cut | slide + pop | C-GLASS-SLAB |
| tracking-collapse, dotted kashida → solid | 10–14 f | — | — | — | T-TRACK-COLLAPSE |

## Transitions
hard cuts; ends with lockup + tagline, hard cut to black

## Sound
calm bed, sparse SFX (≤ 3 per 10 s), dry last line

## How to use it
- Take the kashida-as-hero idea and the calm cream-on-navy world; one hero word per screen.
- Kashida only at legal positions (`rtl-kit.js kashida()`).
- Keep the breather: one stretch of ≥ 3 s without graphics.
