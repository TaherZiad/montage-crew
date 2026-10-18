# Fusion motion graphics (Resolve 19/20/21) — incl. Arabic & programmatic comps

> For users whose profile editor is DaVinci Resolve (free or Studio). The skill always delivers `final.mp4` + an FCP7 timeline XML to import (File > Import > Timeline); this file is for finishing/editing in Resolve after that import. Optional LIVE mode (driving Resolve directly): `references/resolve/00-control-architecture.md`. Features marked **Studio only** are missing or watermarked on the free edition.

Research: 29 transcripts + 7 frame sheets + 9 web. Casey Faris ×6, Jake Wipp, bdsCovered, JayAreTV, Video Knowledge, MrAlexTech ×2, Core and Blue, Filmic Footprints, VideoEditingCentral ×4, rystal, SamResolve, Devon McLaughlin, Chris' Tutorials, Tudor Baba, Socratica FX, MotionEpicFX, Muslim Resolve, Haytham Hassan (AR), Resolve!بالعربي (AR); BMD forum RTL threads, Resolve 20/21 New Features Guides, Fusion 8 Scripting Guide, JayAreTV Text+ reference.

## Fundamentals
- Coordinates normalised 0..1, origin bottom-left, centre {0.5,0.5}; sizes relative to width. Timeline must be 1080×1920 before creating comps. Comps start at frame 0. Reel safe text zone Y 0.22–0.82, X 0.08–0.92.
- Inputs: yellow = Background, **green = Foreground (on top)**, blue = Effect Mask. Shift+Space add tool; F2 rename; 1/2 → viewers; Ctrl+G guides.
- Core tools: MediaIn (Media Source = Background in a Fusion Composition to see the track below), MediaOut, **Merge** (Center, Size, Angle, Blend, ApplyMode Normal/Screen/Add/Multiply), **Background** (TopLeftRed/Green/Blue/Alpha, gradients), **Transform** (Center, Pivot, Size, Angle, Edges), **KeyframeStretcher** (templates survive trimming).
- Text: **Text+** (`TextPlus`: StyledText, Font, Style, Size, CharacterSpacing, LineSpacing, HAnchor/VAnchor, **Reading Direction** (Auto/LTR/RTL), Line Direction, Write On Start/End, Layout Point/Frame/Circle/Path, Transform by chars/words/lines, Shading Elements 1–8, Motion Blur). **MultiText** (R20+): one layer per word with own font/colour/transform; R21 adds pivot, alignment, CSV import.
- Text modifiers: **Follower** (key its own fields; Order L→R, **R→L**, Inside Out, Random; Delay per character only), Character Level Styling, Text Scramble, Text Timer, Time Code; R21 Krokodove **Write** (typewriter + caret), **Juggle**.
- Shapes (`s*`, must end in **sRender**): sRectangle (CornerRadius), sEllipse, sStar, sNGon, sPolygon, sText, sMerge, sBoolean, sTransform, sDuplicate, sJitter, sGrid, sOutline, sExpand.
- Masks: Rectangle (CornerRadius, SoftEdge), Ellipse, Polyline (open path + Border Width = stroke), BSpline, Wand, Ranges; chain with paint modes + invert.
- Tracking: Tracker (Match Move/Steady), **PlanarTracker** (Set reference time, Perspective, both ways → Corner Pin, match aspect), **Magic Mask** (Studio only), DeltaKeyer.
- Looks: SoftGlow (Threshold, Gain, Glow Size), Glow, Highlight, Rays, ColorCorrector (shine through mask), Emboss (glass edge), DropShadow, TV (grain), FastNoise, DirectionalBlur, Blur, VectorMotionBlur.
- Particles: pEmitter (Number, Lifespan, Velocity, Angle, Region Sphere/Bitmap, Style) → pDirectionalForce/pTurbulence → **pRender**.
- 3D: Text3D (Extrusion, Bevel) + lights → Merge3D → Camera3D → **Renderer3D** (Lighting/Shadows on).
- Modifiers: BezierSpline, XY Path, **Anim Curves** (auto-fits clip length), Shake (Min/Max/Smoothness/Seed), Perturb, Expression, Publish/Connect; R21 **Fairlight Animator** (audio drives values).
- Spline editor: **F** flatten (ease), **S** smooth, **L** linear, **T** numeric Ease In/Out, **V** reverse, copy/paste keys.
- Expressions: `Transform1.Size*2`, `time`, `sin(time/5)`, `Point(x,y)`, `iif(a,b,c)`; `:` prefix for multi-line Lua with `return`; `self.Control`.
- Templates: select nodes → Macro → Create Macro → publish controls (colours need R, G, B **and** A) → save `.setting` into Resolve's Fusion `Templates\Edit\Titles` folder (or Effects/Generators/Transitions; find it via Effects → Templates → right-click → Show Folder). R21 Macro Editor: live preview, **Save to Edit Template**. Custom UI via Edit Controls; keep all controls on one "ControlCenter" node linked by expressions.

## Recipes (1080×1920 @30; EO = ease-out, Snap = first key ease-out ~100)
1. **Kinetic word reveal**: MultiText one layer/word (or sText×N → sMerge → sTransform → sRender); word i at 4·i f: size 0→1.12 (+6 f)→1.0 (+10 f), Y −0.03→0, opacity 0→1 over 4 f; camera Transform re-frames every 12–14 f (size 1→0.85, centre); motion blur Q5 shutter 180.
2. **Glow title**: Text+ → SoftGlow (Thr 0.4, Gain 1.2, Size 12) → Merge; Write On End 0→1 over 18 f EO; Gain 3→1.2 over 20 f; flicker = Shake on Gain (0.9–1.3).
3. **Glass panel**: MediaIn(Background) → Blur 20–30 → tint Background (white 10–15 %) masked by RectangleMask (CornerRadius 0.15–0.25) → Merge; Emboss Over ×2 (top ~90°, left ~150°) + TV grain masked + DropShadow + Text+; animate only the mask: width 0.05→0.8 (0–12 f Snap), height 0.02→0.18 (4–14 f).
4. **Text behind subject**: MagicMask (Studio only; blur 1.5, slight negative dilate) → Merge1 (text BG, masked subject FG) → Merge2 over plate. Free: BSpline/Polyline roto + Tracker, DeltaKeyer, or **external alpha matte** (HyperFrames remove-background) as MediaIn. Text size 1.3→1.0 over 15 f EO, blend 0→1 over 6 f.
5. **Lower third**: Background(α0) + brand Background masked by Rectangle → Shadow → Merge; Text+ (HAnchor Left/Right for Arabic) → Merge; KeyframeStretcher. Rect width 0→final 0–10 f Snap (centre X keyed so it grows from the edge); text 6–16 f; mirrored out over last 10 f (copy, paste, V). Build ~1 s, stretch middle.
6. **Highlight box**: sRectangle (CornerRadius .02) → sTransform → sRender → Merge **under** Text+; width 0→w over 3–11 f EO (grow from the right for RTL); height 1.2→1.0 squash 8–12 f.
7. **Counter**: Edit Control `Counter` (slider, integer); StyledText expression `:local n=math.floor(self.Counter+0.5); local s=tostring(n):reverse():gsub("(%d%d%d)","%1,"):reverse():gsub("^,",""); return Text("$"..s)`; keys 0 @6 f → target @60 f, T: ease out 100 / ease in 50; HAnchor Left or tabular font. Eastern digits: `:gsub("%d", function(d) return ({"٠","١","٢","٣","٤","٥","٦","٧","٨","٩"})[d+1] end)`.
8. **Icon pop**: Transform size 0→1.15 (7 f)→0.95 (11 f)→1.0 (14 f), angle −12→0 (0–10 f), blend 0→1 3 f; ring burst sEllipse border .01 scale 0.5→1.6 over 4–14 f, opacity 1→0.
9. **Callout arrow**: open Polyline mask (Solid off, Border .004) on coloured Background, Write On 0→1 over 0–12 f; head sNGon(3) pops 10–14 f; label 12–18 f; planar-track for moving targets.
10. **Blur transition**: Merge blend 0→1 over 8–12 f + DirectionalBlur length 0→0.15→0 (0–10–20 f) + Transform 1→1.08→1; save as Transitions template.
11. **Light sweep**: ColorCorrector (gain +0.5) masked by thin Ellipse (w .05, h .8, 25°, soft .02) moving X −0.2→1.2 over 10–30 f; second mask = text alpha (subtract/invert) to keep it inside glyphs.
12. **Particle burst**: pEmitter (Sphere, Number 400@0 → 0@2, life 20±10, vel .08±.05, angle var 360, size-over-life →0, colour brand) → weak pDirectionalForce → pRender → SoftGlow → Merge Screen.
13. **3D text**: Text3D (extrude .2, bevel .02) + LightDirectional (−35° X) + Ambient .3 → Merge3D → Renderer3D; Z −3→0 and rotY 60→0 over 0–20 f.
14. **Split screen**: two MediaIns filled into rounded Rectangle masks (h 0.5, Y .75/.25, radius .04) + divider sRectangle; A slides 1.25→.75 (0–12 f Snap), B −.25→.25 (4–16 f), divider width 0→1 (10–18 f).
15. **Freeze-frame outline**: freeze + duplicate on V2; Magic Mask (Studio only) → "Outer Stroke" template (width .01 white) or matte → ErodeDilate(+) − original matte → white; below: monochrome plate + ink texture (Darken) + title; subject zoom 1→1.1 (0–8 f), title from X −0.1 (4–14 f), flash at start.
16. **Scramble swap**: Text Scramble randomness 1→0 over 10 f (`01#%`) + chromatic offset; R21 Juggle.

## Arabic / RTL in Fusion
- 17.4+ Text+ shapes & joins Arabic and supports RTL; R20/21 add nothing new. Old basic Text title is worse — use Text+/MultiText. **Never use a "reshaper"** on 17.4+ (double reversal).
- Must choose an Arabic font (default Open Sans has no Arabic → empty/boxes): Cairo, Tajawal, Almarai, IBM Plex Sans Arabic, Noto Kufi/Naskh Arabic, Readex Pro, El Messiri, Lalezar, Reem Kufi. On Windows install fonts **for all users** and restart Resolve.
- Reading Direction Auto/RTL; anchor & justify Right for right-aligned blocks.
- Gotchas: (1) **R21 tashkeel bug** in the edit field → disable spell check (Preferences > User > Language and Spelling). (2) **Stroke may make Arabic vanish on Windows** (16.2–18.6 reports) → use Shading Element 2 Outline, or ErodeDilate copy underneath, or shadow/border. (3) Draw text paths left→right. (4) Follower/per-glyph scale breaks joins mid-motion → only opacity/blur/small Y per glyph, Order R→L; for per-word effects use MultiText one layer per word. (5) Write On reveals in logical order (right→left) but letters change form mid-reveal → cleanest reveal = soft Rectangle/Crop wipe moving right→left. (6) No kashida justification → insert U+0640 manually (our `kashida()` helper output can be pasted as StyledText). (7) Mixed Arabic/Latin/digits: wrap runs with RLM/LRM or split into layers. (8) Character Level Styling crash report — save first.
- **Default policy**: simple static/word-level Arabic titles may use Text+ (Arabic font + RTL); anything kinetic, per-letter, tashkeel-heavy, glass/kashida-animated → pre-render in HyperFrames (ProRes 4444 alpha / PNG sequence) and composite (MediaIn/Loader or track V2+). R21 can also import Lottie/OGraf (OGrafLoader node).

## Programmatic Fusion
- Get exact IDs: build by hand → select nodes → **Ctrl+C** → paste into a text editor = `.setting` Lua table; or `tool:GetInputList()`, `tool:GetAttrs().TOOLS_RegID`.
- `.setting` structure: `{ Tools = ordered() { Name = MacroOperator { Inputs = ordered(){ X = InstanceInput{SourceOp="Txt", Source="StyledText"} }, Outputs = { MainOutput1 = InstanceOutput{SourceOp="Glow", Source="Output"} }, Tools = ordered(){ Txt = TextPlus{Inputs={...}}, TfSize = BezierSpline{KeyFrames={[0]={0, RH={2,0.8}}, [7]={1.12, LH={5,1.12}, RH={9,1.12}}, [12]={1, LH={10,1}}}}, Tf = Transform{Inputs={Input=Input{SourceOp="Txt",Source="Output"}, Size=Input{SourceOp="TfSize",Source="Value"}}} } } }, ActiveTool = "..." }`. Connections are `Input{SourceOp=..., Source="Output"}`; animated input → BezierSpline `Source="Value"`; handles are **absolute** time/value (ease-in-out: RH at t0+d/3, LH at t1−d/3; snap: RH at t0+0.15d with 70 % of the value change). `.comp` = same wrapped in `Composition{}`.
- Scripting (LIVE mode only — see `00-control-architecture.md`; Lua or Python):
```python
item = tl.InsertFusionTitleIntoTimeline("Text+")   # or InsertFusionCompositionIntoTimeline()
comp = item.GetFusionCompByIndex(1)                  # item.ImportFusionComp(path) / ExportFusionComp(path,1)
comp.Lock(); comp.StartUndo("AI")
txt = comp.FindToolByID("TextPlus") or comp.AddTool("TextPlus", -32768, -32768)
txt.SetInput("StyledText", "مرحبا"); txt.SetInput("Font", "Cairo"); txt.SetInput("Style", "Bold"); txt.SetInput("Size", 0.08)
tf = comp.AddTool("Transform", 2, 0); tf.ConnectInput("Input", txt)
tf.AddModifier("Size", "BezierSpline"); tf.SetInput("Size", 0.0, 0); tf.SetInput("Size", 1.12, 7); tf.SetInput("Size", 1.0, 12)
glow = comp.AddTool("SoftGlow", 3, 0); glow.ConnectInput("Input", tf)
comp.FindToolByID("MediaOut").ConnectInput("Input", glow)
tf.Angle.SetExpression("sin(time/6)*2")
comp.EndUndo(True); comp.Unlock()
```
  Lua extras: `comp:Paste(bmd.readfile(path))` inserts a .setting; `tool:LoadSettings(path)`; `tool:SetAttrs({TOOLB_NameSet=true, TOOLS_Name="Title"})`; BezierSpline `SetKeyFrames({...}, true)`.
- If the `resolve-fusion` skill is installed, it offers offline `.comp` generation and live `safe_add_tool` / `safe_set_inputs` / `safe_connect_tools` — probe input availability first.

## Ideas
Arabic MultiText word captions popping from the right with highlight boxes · Eastern-digit counter with glow · glass stat card rising from the bottom · title behind speaker 1.3→1.0 · planar-tracked callout on a phone · calligraphy logo shine · neon flicker (Shake) on outline · audio-reactive title (Fairlight Animator) · particle dust ring behind a word · 3D brand word fly-in · sBoolean crescent morph (Ramadan) · split-screen before/after · freeze-frame intro · RTL marker highlight · scramble reveal for numbers/English · progress bar tied to a percent control · kinetic typography with a camera sTransform · blur-zoom transition pack · OGraf/Lottie icons (R21) · Fusion-template subtitle style (R20) · circle-layout text ring around the head · FastNoise light leak + Rays · RTL typewriter via mask wipe + blinking caret · CSV MultiText "Top 5".

## Mistakes / performance / QA
No sRender/Renderer3D → nothing shows · swapped Merge inputs · Follower without keyed fields · macro colours without all 4 channels · templates without KeyframeStretcher · planar corner-pin aspect mismatch · Arabic: font lacks glyphs, reshaper on 17.4+, paths drawn R→L, spell-check tashkeel bug, stroke on Windows · centred-anchor counters jitter · linear keys · Magic Mask assumed on free.
Performance: proxy viewer, HiQ/motion blur off while designing; shapes over big masked Backgrounds; blur a downscaled copy; cache heavy comps (Render Cache / Render in Place); macros over many Text+; keep 1080×1920; `comp:Lock()` while scripting.
QA per graphic: safe zones · eased curves · motion blur on for final · Arabic correct (RTL, anchors, tashkeel) · trim test 2 s and 8 s keeps in/out · clean alpha (Background α = 0) · real-time or cached.
