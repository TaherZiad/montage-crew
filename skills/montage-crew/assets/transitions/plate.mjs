#!/usr/bin/env node
// plate.mjs: make a ready-to-render HyperFrames project for one transition (montage-crew, tr-kit.js).
//
//  OVERLAY plate (alpha .mov over a hard cut):
//    node plate.mjs coverWipe --dur 0.4 --o '{"dir":"rtl","color":"#181813"}' --out <work>/tr/t01 [--render]
//  SCENE junction (mp4 that replaces the cut; needs the two shots):
//    node plate.mjs whip --dur 0.33 --a cutA.mp4 --a-out 12.40 --b cutB.mp4 --b-in 0 --out <work>/tr/t02 [--render]
//      --a-out = time in A where the edit is, --b-in = time in B where the edit is. Handles are cut automatically.
//  Common: --cut 0.5 (fraction of dur where the edit sits; default from the kit) --pre/--post s (padding)
//          --w 2160 --h 3840 (4K plate; alpha cannot use --resolution 4k, so we render natively)  --fps 30
// Prints where to put the result on the timeline (layers.json `at`) (record start = edit - pre - dur*cut) and the SFX cue.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const assets = resolve(here, "..");
const argv = process.argv.slice(2);
const fn = argv[0];
const opt = (k, d) => { const i = argv.indexOf("--" + k); return i < 0 ? d : argv[i + 1]; };
const has = (k) => argv.includes("--" + k);
if (!fn || fn.startsWith("--")) { console.log(readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").slice(1, 13).join("\n")); process.exit(1); }

const kit = readFileSync(join(here, "tr-kit.js"), "utf8");
const isOverlay = new RegExp(`OVERLAY = \\{[^}]*\\b${fn}\\b`).test(kit);
const isScene = new RegExp(`SCENE = \\{[^}]*\\b${fn}\\b`).test(kit);
if (!isOverlay && !isScene) { console.error(`unknown plate transition "${fn}" (morph/dolly/typeZoom are used inside MG compositions)`); process.exit(2); }

const dur = +opt("dur", 0.4), pre = +opt("pre", 0), post = +opt("post", 0), fps = +opt("fps", 30);
const o = JSON.parse(opt("o", "{}"));
if (has("cut")) o.cut = +opt("cut");
const cutFrac = o.cut ?? ({ flash: 0.25, kashidaWipe: 0.55, colorFlip: 0, speedLines: 0, rings: 0 }[fn] ?? 0.5);
const W = +opt("w", 1080), H = +opt("h", 1920), total = +(pre + dur + post).toFixed(4), cutT = pre + dur * cutFrac;
const out = resolve(opt("out", `tr_${fn}`));
const gsapFile = join(assets, "gsap.min.js");
if (!existsSync(gsapFile)) { console.error("GSAP غير منزّل — شغّل: setup.py install\nGSAP not downloaded: run setup.py install (or scripts/fetch_assets.py gsap) with the skill's python, then retry."); process.exit(1); }
mkdirSync(out, { recursive: true });

let html = readFileSync(join(here, "plate.html"), "utf8")
  .replace(/\/\*CFG\*\/.*\/\*\/CFG\*\//, `const CFG = ${JSON.stringify({ fn, dur, pre, post, o })};`)
  .replace('data-width="1080" data-height="1920" data-duration="1"', `data-width="${W}" data-height="${H}" data-duration="${total}"`)
  .replace('content="width=1080, height=1920"', `content="width=${W}, height=${H}"`);

if (isScene && (opt("a") || opt("b"))) {
  if (!opt("a") || !opt("b")) { console.error("scene junction needs both --a and --b"); process.exit(2); }
  // A: from (edit - cutT) for `total` s (frames after the edit = handle for crossfades); B: from (edit - cutT) likewise.
  const cut = (src, edit, name) => {
    const ss = Math.max(0, edit - cutT);
    execFileSync("ffmpeg", ["-y", "-v", "error", "-ss", ss.toFixed(4), "-i", src, "-t", String(total), "-an", "-r", String(fps),
      "-vf", `scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H}`, "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", join(out, name)]);
    if (edit - cutT < 0) console.warn(`⚠️ ${name}: not enough frames before the edit (${(cutT - edit).toFixed(2)} s short)`);
  };
  cut(opt("a"), +opt("a-out"), "a.mp4");
  cut(opt("b"), +opt("b-in", 0), "b.mp4");
  const v = (id, f) => `<div id="${id}" class="scene"><video src="${f}" data-start="0" data-duration="${total}" muted playsinline></video></div>`;
  html = html.replace(/<!--SCENES-->[\s\S]*<!--\/SCENES-->/, `${v("A", "a.mp4")}\n  ${v("B", "b.mp4")}`);
} else if (isOverlay) {
  html = html.replace(/<!--SCENES-->[\s\S]*<!--\/SCENES-->/, "");
}
writeFileSync(join(out, "index.html"), html);
copyFileSync(join(here, "tr-kit.js"), join(out, "tr-kit.js"));
copyFileSync(gsapFile, join(out, "gsap.min.js"));
if (existsSync(join(assets, "fonts", "Alexandria-VF.ttf"))) copyFileSync(join(assets, "fonts", "Alexandria-VF.ttf"), join(out, "Alexandria-VF.ttf"));
if (o.src && existsSync(o.src)) copyFileSync(o.src, join(out, o.src.split(/[\\/]/).pop()));

const fmt = isOverlay ? "mov" : "mp4", file = join(out, `${fn}.${fmt}`);
const sfx = { whip: "transition_swipe", wipe: "transition_swipe", coverWipe: "transition_swipe", bars: "transition_swipe", blinds: "transition_swipe",
  kashidaWipe: "transition_swipe", spin: "whoosh_fast", speedLines: "whoosh_fast", glitchCut: "glitch", glitchSlices: "glitch",
  cardFlip: "paper", mirrorFlip: "paper", pageTurn: "paper", doors: "impact_soft", flash: "impact_soft", ink: "swoosh_reverse",
  tiles: "click_ui", burn: "swell", ripple: "swell", rings: "pop" }[fn] ?? (["zoom", "blurCut", "scaleInPlace", "leak", "colorFlip", "morph"].includes(fn) ? "none" : "whoosh_soft");
console.log(`✅ ${out}  (${fn}, ${isOverlay ? "overlay alpha .mov" : "scene junction .mp4"}, ${W}x${H}, ${total}s = ${Math.round(total * fps)} f)`);
console.log(`   Resolve: record start = EDIT − ${cutT.toFixed(3)} s (${Math.round(cutT * fps)} f)  ${isOverlay ? "on a track above the cut" + (["leak", "burn"].includes(fn) ? ", Composite Mode = Screen" : "") : "on V1, replacing [EDIT−cut, EDIT−cut+dur]"}`);
console.log(`   SFX: ${sfx} (quiet, −8…−12 dB under the voice), peak on the edit frame (clip start = edit − peak_time_s)`);
if (has("render")) {
  execFileSync("npx", ["hyperframes", "render", out, "--format", fmt, "--fps", String(fps), "--output", file], { stdio: "inherit", shell: true });
  console.log(`   → ${file}`);
} else console.log(`   render: npx hyperframes@0.8.151 render "${out}" --format ${fmt} --output "${file}"`);
