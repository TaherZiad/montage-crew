# Asset research & sourcing (step 7)

Every visual on screen is researched for THIS video's content. **Tool: `scripts/assets.py`.** It searches free-for-commercial sources without logging in, prints candidates, and downloads the one you pick. Each download is recorded in `assets/manifest.json`.

```bash
python scripts/assets.py search <kind> "<english query>" [--n 8] [--orientation portrait|landscape] [--set lucide]
python scripts/assets.py download <id> [<id> …] --to <work>/assets/<sub>     # also accepts a direct https URL
python scripts/assets.py kinds
```
- kinds: `photo video icon logo svg illustration lottie model3d texture overlay sfx ui`
- `--n` is the number of results **per source**. The ids from every search go into a cache at `%TEMP%/reel_assets_cache.json`, so `download` takes any id printed earlier.
- `--set` applies to icons only: it limits the search to Iconify prefixes (`lucide`, `solar`, `tabler`, `ph`, `mingcute`…). Use it to keep one icon family per video.
- `ui` takes a URL or domain as the query, e.g. `search ui "cursor.com"`. It returns the variants `mobile-dark|mobile-light|desktop-dark|desktop-light|desktop-full`, which are captured with Playwright (Python, Chromium already installed, 2× / 3× DPR).
- Manifest: the `--to` folder or its nearest parent named `assets` gets `manifest.json` entries of the form `{file,type,source,source_url,download_url,licence,author,title,added}`. Use `--no-manifest` for scratch tests. In delivery mode, keep the manifest outside the video folder if the user doesn't want it there.
- On download the tool prints image size, flagging anything under 1080 px on the long side. For Lottie it prints `vector lottie` or `RASTER LOTTIE`; drop raster ones.
- Optional keys come only from the user's own environment variables and are used when set: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`, `FREESOUND_API_KEY`, `SKETCHFAB_API_TOKEN`. Never store a key in a file (script, config, manifest, notes) or paste it into chat. All are free signups. **Pexels is the single biggest quality jump for photo and video B-roll.** Error output never prints keys.

## 1. Turning a beat into search queries
1. **Name the visual, not the sentence.** For «الذكاء الاصطناعي صار يكتب الكود بدلاً منك», search for what the eye should see: `robot hand typing keyboard`, `code on screen dark`, `ai chip glowing`. Search in English: every API indexes English.
2. **Pick the metaphor first, then the noun** (craft/11 §4). Speed → `rocket`, `lightning`. Growth → `chart arrow up`, `plant sprout`. Danger → `warning`, `fire`. Money → `coins`, `cash stack`. Thinking → `brain`, `lightbulb`. Time → `hourglass`, `clock`. Connection → `network nodes`, `plug`.
3. **Write three queries per slot:** literal (`laptop coding`), mood (`laptop coding dark neon`), metaphor (`rocket launch`). Use 1–3 words. Small catalogues (unDraw, Storyset, Fluent 3D, Mixkit tags) match single words, and the tool retries word by word automatically.
4. **Use style words that fit the reel's stage:** `dark`, `neon`, `isometric`, `3d`, `minimal`, `top view`, `close up`, `bokeh`, `vertical`. Search `--orientation portrait` for anything that fills the 9:16 frame.
5. **Named things go to the exact sources.** Brands → `logo`. Products and apps → `ui` (or the creator's own screen recording). Never use a stock lookalike for a named product.
6. Pick **2–3 candidates per slot** and open the `preview` or `page` links. Choose the one that matches the palette and concept.

## 2. Quality checklist (each asset, before it goes in)
- [ ] **Resolution**: at least 2× the on-screen size. Full-frame 9:16 needs ≥ 1080×1920, or a crop from 4K. SVG for icons, logos and shapes. PNG with alpha for cut-outs. Video at 1080p or more (Mixkit downloads try 2160 → 1080 → 720).
- [ ] **Style consistency**: one icon family (`--set`), one 3D style (all Fluent 3D, or all generated with the same prompt), one illustration style (all unDraw, or one Storyset style such as `cuate`/`rafiki`/`amico`/`pana`/`bro`), one photo grade.
- [ ] **Brand-accurate logos**: official mark, current version, correct colours. LobeHub `-color` or Simple Icons and the press kit win. Never redraw a logo or AI-generate one. Use it only when the video talks about that brand. Brand logos are trademarks: show them, never use one as the user's own mark.
- [ ] **Licence** is one of: CC0, Public Domain, CC BY (attribution in manifest), MIT/Apache/ISC, or the Pexels / Unsplash / Pixabay / Mixkit / unDraw / Lottie Simple licences. **No** NC, ND, SA, GPL, "editorial only" stock, or fair use. The tool already filters Openverse, Commons and Sketchfab to these.
- [ ] **No watermark**, no visible third-party brands or faces of real people unless that's the topic, no text baked in the wrong language.
- [ ] **Relevance**: the asset explains or strengthens its beat. If nothing fits, keep the beat typographic.

## 3. Sources: tested with Python requests, no login
| Source | Kinds in `assets.py` | Status | Licence | Notes / limits |
|---|---|---|---|---|
| **Pexels API** | photo, video | needs key (401 without one); Cloudflare blocks the website | Pexels (free commercial) | 200 req/h, 20k/month. Best B-roll quality. |
| **Pixabay API** | photo, video, overlay | needs key (400 without one); website 403 | Pixabay Content License | 100 req/min. Images come at 1280 px unless the key gets full-API approval. |
| **Unsplash API** | photo | needs key (`napi` returns 403) | Unsplash License | 50 req/h in demo mode. The tool pings `download_location` as the API rules require. |
| **Freesound API** | sfx | needs key (401 without one) | CC0 / CC BY filter | HQ mp3 preview. Original files need OAuth. Without a key, Openverse already covers Freesound. |
| **Openverse API** | photo, svg, sfx | works without a key | filtered to CC0 / PDM / BY | Anonymous use is rate-limited (fine for one reel; a free token raises it). Quality is mixed (Flickr, StockSnap, Wikimedia, Freesound audio). Some `url`s are 960 px thumbs, so check the printed size. |
| **Wikimedia Commons API** | photo, video (webm), svg, logo | works | only CC0 / PD / CC BY kept | Strong for logos (`Claude AI logo.svg`, PD) and 4K timelapses. Searches are noisy. |
| **Mixkit** (HTML scrape) | video, overlay, sfx | works | Mixkit Free License | Video: newer clips are 720p only, older ones have 1080/2160. `--orientation` maps to `?orientation=vertical`. Overlays: light leaks, flares, bokeh. SFX: full-length preview mp3. |
| **Iconify API** | icon, logo | works | per set (shown: MIT / Apache / CC BY / CC0) | 200k+ icons. Add `?color=%23D0B6A1` to recolour monochrome icons. Logo sets: `logos`, `simple-icons`, `devicon`, `skill-icons`. |
| **LobeHub icons** (jsDelivr) | logo | works | MIT set; the marks are trademarks | **Best for AI brands**: claude, claudecode, openai, gemini, cursor, copilot, githubcopilot, lovable, vercel, plus ~300 more, with `-color` / `-text` variants. |
| **Simple Icons** (jsDelivr/Iconify) | logo | works | CC0 (marks are trademarks) | Monochrome brand marks with the official hex in their data. |
| **unDraw API** | illustration | works | unDraw (free, no attribution) | Recolourable SVG: the accent `#6c63ff` swaps to your palette colour. Flat 2D style. |
| **Storyset API** | illustration | works | Freepik free licence, **attribution required** | 5 styles per concept. SVG plus transparent PNG previews. |
| **Fluent 3D emoji** (GitHub, MIT) | illustration | works (tree cached 30 days; GitHub API allows 60 req/h anonymous) | MIT | ~1500 glossy 3D objects, but **256×256 only**, so use them for ≤ 200 px slots. |
| **LottieFiles GraphQL** | lottie | works | Lottie Simple License | Some animations are raster image sequences; the tool flags them. Prefer `vector lottie`. Play with the pinned `lottie-web@5.12.2` **light** build (`build/player/lottie_light.min.js`, no expressions). |
| **Poly Haven API** | model3d, texture | works | CC0 | Models come as glTF and are packed into `.glb` with `npx gltf-pipeline` (auto). Textures: 4K diffuse jpg. HDRIs are there too (`t=hdris`), not wired into the tool. |
| **ambientCG API** | texture | works | CC0 | 2K zip, from which the tool extracts the `_Color` map. |
| **Sketchfab API** | model3d | search works; download needs `SKETCHFAB_API_TOKEN` (free account) | CC BY / CC0 filtered | Huge catalogue. Returns glb when available. |
| **Playwright** (`pip install playwright`) | ui | works (`playwright install chromium`) | real product UI, editorial use | Login walls and cookie/one-tap popups show up, so for logged-in app screens use the creator's own screen recording. `npx hyperframes@0.8.151 capture <url>` also works for a whole site as editable components. |
| Press kits | `download <url>` | reachable | brand guidelines | Anthropic `anthropic.com/press-kit` (zip) · OpenAI `openai.com/brand` · Cursor `cursor.com/brand` · Vercel `vercel.com/geist/brands` · Supabase `supabase.com/brand-assets` · GitHub `brand.github.com` · Google `partnermarketinghub.withgoogle.com` |
| Google favicon / unavatar / GitHub avatar | (manual URL) | work | trademark | `google.com/s2/favicons?domain=x&sz=256` (low-res), `github.com/<org>.png?size=400`. Last resort only. |
| NASA Images API | (manual) | works, no key | public domain | Space and rocket photos and video: `images-api.nasa.gov/search?q=`. |
| Google Fonts | (manual) | works | OFL | Fonts are already local in `assets/fonts/`. New ones come from `github.com/google/fonts`. |
| SVGRepo | none | **failed** (429 / Cloudflare) | — | Use Iconify, Openverse SVG or Commons instead. |
| Coverr API | none | **failed** (needs key); site scrape is 8 MB | — | Mixkit covers this need. |
| Clearbit logo API | none | **dead** (DNS fails) | — | Use LobeHub, Simple Icons or Commons. |
| Poly Pizza | none | needs key | CC0/BY | Low-poly models, optional. |
| theSVG | none | no public API (404) | — | The `media-use` skill (if installed) uses it internally. |

Other routes (if installed): an Icon MCP (`search_families` → `download_asset`), the `media-use` skill (`resolve image|icon|logo|sfx|bgm`), and the HyperFrames registry for effect blocks (glitch, grain, particles). Generated 3D icons (one fixed prompt for the whole video) are fine when no source fits.

## 4. Prep (after download)
- **Remove background**: `npx hyperframes@0.8.151 remove-background in.png` (u2net, stills only). For logos, prefer the SVG over cutting out a raster.
- **Recolour an SVG to the palette**: for Iconify, download with `?color=%23HEX` or replace `currentColor`. For unDraw, replace `#6c63ff` (accent), and optionally `#3f3d56` and `#2f2e41` (dark ink):
  `python -c "import sys,re;p=sys.argv[1];s=open(p,encoding='utf8').read();open(p,'w',encoding='utf8').write(s.replace('#6c63ff','#D0B6A1'))" file.svg`
  Keep the same stroke width across one icon family (`stroke-width` attribute, or CSS `vector-effect`).
- **Recolour a Lottie** (vector only; tested). It snaps every fill and stroke colour to the nearest palette colour:
  ```python
  import json, sys   # python recolor.py in.json out.json "#D0B6A1" "#1E2A44" "#F5EFE8"
  src, dst, *pal = sys.argv[1:]
  pal = [[int(h.lstrip("#")[i:i+2], 16) / 255 for i in (0, 2, 4)] for h in pal]
  fix = lambda c: min(pal, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, c[:3]))) + c[3:]
  def walk(o):
      if isinstance(o, dict):
          if o.get("ty") in ("fl", "st") and isinstance(o.get("c", {}).get("k"), list):
              k = o["c"]["k"]
              if k and isinstance(k[0], (int, float)): o["c"]["k"] = fix(k)
              else:
                  for kf in k:
                      for s in ("s", "e"):
                          if s in kf: kf[s] = fix(kf[s])
          for v in o.values(): walk(v)
      elif isinstance(o, list):
          for v in o: walk(v)
  d = json.load(open(src, encoding="utf-8")); walk(d); json.dump(d, open(dst, "w", encoding="utf-8"))
  ```
- **Upscale** (small photos, Fluent 3D): `ffmpeg -i in.png -vf "scale=iw*2:ih*2:flags=lanczos" out.png`. This is plain interpolation and works for at most 2×. Beyond that, find a bigger source (no AI upscaler is assumed).
- **Crop to 9:16**: photo `ffmpeg -i in.jpg -vf "crop=ih*9/16:ih,scale=1080:1920" out.jpg`. Video `ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920,fps=30" -c:v libx264 -crf 16 -an out.mp4`. Shift the crop with `crop=w:h:x:0` so the subject stays clear of the face/UI danger zones (`zones.py`).
- **Overlays** (light leak, flare, film burn on black): blend mode **Screen** or Add in Resolve, opacity 30–60 %, trim to the transition.
- **Textures**: tile or blur them as stage backgrounds, then grade them into the 3-colour stage.
- **3D (.glb)**: load in a HyperFrames page with `<model-viewer>` or three.js (the `threejs-webgl` skill, if installed), light it to the palette, and render with alpha.
- **Contact sheet before building**: `ffmpeg … tile`, or `scripts/sheet.py`, for one look at all picked assets.

## Rules
- **Licence**: free for commercial use only (§2). CC BY and Storyset need attribution, so note it in the manifest. Never rip images from Instagram, Dribbble, Behance or Pinterest; those are for inspiration only.
- **Relevance over decoration**: every asset must explain or reinforce the spoken idea of its beat.
- **Consistency**: one icon family, one 3D render style, one illustration style, one photo grade per video.
- **Folders**: `assets/img|icons|logos|vectors|lottie|3d|textures|fx|video|sfx|music/`.
