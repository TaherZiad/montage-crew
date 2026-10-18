/* tr-kit.js: transition kit for HyperFrames (GSAP 3, paused timeline, seek-safe). Catalogue: references/transitions-library.md
 *
 * Every function ADDS tweens to `tl` and returns tl.  t = start (s), d = total length (s), cut = t + d*o.cut (default .5).
 *  SCENE  fn(tl, A, B, t, d, o)  A = outgoing full-frame element, B = incoming (B is hidden at build, shown by the kit).
 *  OVERLAY fn(tl, root, t, d, o) builds its own DOM inside `root` (a transparent full-frame layer) = an alpha plate
 *         that covers a hard cut in Resolve. Never touches footage.
 * Rules kept: transform / opacity / filter / clip-path only (+ SVG transform and feGaussianBlur/feDisplacementMap attrs,
 * which are filter parameters tweened natively, no onUpdate). Seeded random only (o.seed). No repeat:-1.
 * Every call pushes {id, cut, sfx} to TR.cues (sfx = folder in assets/sfx; keep it quiet, peak on `cut`).
 * Defaults: smooth eases, no white flashes, peaks small. o.soft:false unlocks the snappier editorial values.
 */
(function (G) {
  const F = 1 / 30;
  const $ = (x) => (typeof x === "string" ? document.querySelector(x) : x);
  const V = { rtl: [-1, 0], ltr: [1, 0], up: [0, -1], down: [0, 1] }; // travel direction of the motion
  const cues = [];
  const cue = (id, cut, sfx) => cues.push({ id, cut: +cut.toFixed(4), sfx });
  let uid = 0;

  function rng(seed) { // mulberry32
    let a = (seed ?? 7) >>> 0;
    return () => { a = (a + 0x6d2b79f5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  const size = (e) => { // layout size; before the runtime stamps the root, fall back to the composition's data-width/height
    e = $(e); let w = e.clientWidth, h = e.clientHeight;
    if (!w || !h) { const r = e.closest("[data-width][data-height]"); if (r) { w = w || +r.dataset.width; h = h || +r.dataset.height; } }
    return [w, h];
  };
  const k = (e) => size(e)[0] / 1080; // px scale vs the 1080 design grid (4K plates = 2)
  function div(root, css) {
    const e = document.createElement("div");
    e.style.cssText = "position:absolute;pointer-events:none;" + css;
    $(root).append(e);
    return e;
  }
  function svgDefs() {
    let s = document.getElementById("tr-defs");
    if (!s) {
      s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      s.id = "tr-defs"; s.setAttribute("width", "0"); s.setAttribute("height", "0");
      s.style.cssText = "position:absolute;width:0;height:0";
      document.body.append(s);
    }
    return s;
  }
  function filter(inner) {
    const id = "trf" + ++uid, f = document.createElementNS("http://www.w3.org/2000/svg", "filter");
    f.id = id; f.setAttribute("x", "-20%"); f.setAttribute("y", "-20%");
    f.setAttribute("width", "140%"); f.setAttribute("height", "140%");
    f.setAttribute("color-interpolation-filters", "sRGB");
    f.innerHTML = inner; svgDefs().append(f);
    return [id, f];
  }
  const ctx = (A, B, t, d, o) => { const c = t + d * (o.cut ?? 0.5); return [$(A), $(B), c, c - t, t + d - c]; };
  const soft = (o) => o.soft !== false;
  function enter(B) { gsap.set(B, { autoAlpha: 0 }); }
  function swap(tl, A, B, at) { tl.set(B, { autoAlpha: 1 }, at); tl.set(A, { autoAlpha: 0 }, at); }

  /** Directional motion blur on els during [t, t+d], peak px at `c` (axis x|y). */
  function dirBlur(tl, els, t, c, end, peak, axis) {
    if (!peak) return;
    const [id, f] = filter(`<feGaussianBlur stdDeviation="0 0"/>`), fe = f.firstChild;
    tl.set(els, { filter: `url(#${id})` }, t).set(els, { filter: "none" }, end);
    tl.to(fe, { attr: { stdDeviation: axis === "y" ? `0 ${peak}` : `${peak} 0` }, duration: c - t, ease: "power2.in" }, t)
      .to(fe, { attr: { stdDeviation: "0 0" }, duration: end - c, ease: "power2.out" }, c);
  }

  // ───────────────────────────── SCENE transitions ─────────────────────────────
  /** TR-010 velocity zoom. A pushes in (1→peak) with blur, B lands from fromB→1. fromB>1 = edge-safe for footage. */
  function zoom(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), pk = o.peak ?? (soft(o) ? 1.25 : 2.2), bl = (o.blur ?? (soft(o) ? 8 : 18)) * k(a.parentNode);
    const xf = o.xfade ?? 2 * F; enter(b);
    tl.to(a, { scale: pk, rotation: o.rot ?? 0, filter: `blur(${bl}px)`, duration: h1, ease: o.in ?? (soft(o) ? "power2.in" : "expo.in") }, t);
    tl.fromTo(b, { scale: o.fromB ?? 1.2, rotation: -(o.rot ?? 0), filter: `blur(${bl}px)` },
      { scale: 1, rotation: 0, filter: "blur(0px)", duration: h2, ease: o.out ?? (soft(o) ? "power2.out" : "expo.out") }, c);
    tl.fromTo(b, { autoAlpha: 0 }, { autoAlpha: 1, duration: xf, ease: "none" }, c - xf / 2).set(a, { autoAlpha: 0 }, c + xf / 2);
    cue("zoom", c, null); return tl;
  }

  /** TR-001 whip pan. A leaves along dir (power3.in), B arrives (power3.out), directional blur peaks on the cut. */
  function whip(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), v = V[o.dir ?? "rtl"], [W, H] = size(a.parentNode);
    enter(b);
    tl.to(a, { x: v[0] * W, y: v[1] * H, duration: h1, ease: o.in ?? "power3.in" }, t);
    tl.fromTo(b, { x: -v[0] * W, y: -v[1] * H }, { x: 0, y: 0, duration: h2, ease: o.out ?? "power3.out" }, c);
    swap(tl, a, b, c);
    dirBlur(tl, [a, b], t, c, t + d, (o.blur ?? 40) * k(a.parentNode), v[0] ? "x" : "y");
    cue("whip", c, "transition_swipe"); return tl;
  }

  /** TR-002 push. A and B travel together (one in-out curve), optional motion blur. */
  function push(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), v = V[o.dir ?? "rtl"], [W, H] = size(a.parentNode), e = o.ease ?? "power3.inOut";
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.to(a, { x: v[0] * W, y: v[1] * H, duration: d, ease: e }, t);
    tl.fromTo(b, { x: -v[0] * W, y: -v[1] * H }, { x: 0, y: 0, duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    dirBlur(tl, [a, b], t, c, t + d, (o.blur ?? 18) * k(a.parentNode), v[0] ? "x" : "y");
    cue("push", c, "whoosh_soft"); return tl;
  }

  /** TR-003 slide-over. B slides over A; A drifts 30 % and dims (parallax). */
  function slideOver(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), v = V[o.dir ?? "rtl"], [W, H] = size(a.parentNode), e = o.ease ?? "power3.inOut";
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.to(a, { x: v[0] * W * 0.3, y: v[1] * H * 0.3, filter: "brightness(0.55)", duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    tl.fromTo(b, { x: -v[0] * W, y: -v[1] * H }, { x: 0, y: 0, duration: d, ease: e }, t);
    cue("slideOver", c, "whoosh_soft"); return tl;
  }

  /** TR-012 spin. Rotation + the exact over-scale that keeps corners covered (+4 %), blur peak on the cut. */
  function spin(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), [W, H] = size(a.parentNode), deg = (o.deg ?? 25) * (o.dir === "ltr" ? -1 : 1);
    const r = Math.abs(deg) * Math.PI / 180, cov = (Math.cos(r) + (Math.max(W, H) / Math.min(W, H)) * Math.sin(r)) * 1.04;
    const bl = (o.blur ?? 10) * k(a.parentNode); enter(b);
    tl.to(a, { rotation: deg, scale: cov, filter: `blur(${bl}px)`, duration: h1, ease: o.in ?? "power3.in" }, t);
    tl.fromTo(b, { rotation: -deg, scale: cov, filter: `blur(${bl}px)` }, { rotation: 0, scale: 1, filter: "blur(0px)", duration: h2, ease: o.out ?? "power3.out" }, c);
    swap(tl, a, b, c); cue("spin", c, "whoosh_fast"); return tl;
  }

  /** TR-020 blur cut / blur dissolve. */
  function blurCut(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), bl = (o.blur ?? 24) * k(a.parentNode), xf = o.xfade ?? 6 * F;
    enter(b);
    tl.to(a, { filter: `blur(${bl}px)`, scale: o.scaleA ?? 1.04, duration: h1, ease: "power2.in" }, t);
    tl.fromTo(b, { filter: `blur(${bl}px)`, scale: 1.06 }, { filter: "blur(0px)", scale: 1, duration: h2, ease: "power2.out" }, c);
    tl.fromTo(b, { autoAlpha: 0 }, { autoAlpha: 1, duration: xf, ease: "sine.inOut" }, c - xf / 2).set(a, { autoAlpha: 0 }, c + xf / 2);
    cue("blurCut", c, null); return tl;
  }

  /** TR-021 scale-in-place: A settles back and fades, B arrives from 1.06. The quietest designed transition. */
  function scaleInPlace(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o); enter(b);
    tl.to(a, { scale: o.to ?? 0.92, filter: "brightness(0.6)", duration: d, ease: "power2.inOut" }, t).set(a, { autoAlpha: 0 }, t + d);
    tl.fromTo(b, { scale: o.from ?? 1.06, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: d * 0.6, ease: "power2.out" }, t + d * 0.4);
    cue("scaleInPlace", c, null); return tl;
  }

  /** TR-030 card flip (3D, perspective). o.axis "y"|"x". Turning face darkens. */
  function cardFlip(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), s = o.dir === "ltr" ? 1 : -1, p = o.axis === "x" ? "rotationX" : "rotationY";
    gsap.set([a, b], { transformPerspective: o.persp ?? 1600, backfaceVisibility: "hidden" }); enter(b);
    tl.to(a, { [p]: 90 * s, filter: "brightness(0.6)", duration: h1, ease: "power2.in" }, t);
    tl.fromTo(b, { [p]: -90 * s, filter: "brightness(0.6)" }, { [p]: 0, filter: "brightness(1)", duration: h2, ease: "power2.out" }, c);
    swap(tl, a, b, c); cue("cardFlip", c, "paper"); return tl;
  }

  /** TR-031 flat mirror flip (scaleX through 0, no perspective). */
  function mirrorFlip(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), p = o.axis === "x" ? "scaleY" : "scaleX"; enter(b);
    tl.to(a, { [p]: 0, duration: h1, ease: "power2.in" }, t);
    tl.fromTo(b, { [p]: 0 }, { [p]: 1, duration: h2, ease: "power2.out" }, c);
    swap(tl, a, b, c); cue("mirrorFlip", c, "paper"); return tl;
  }

  /** TR-032 cube. Both faces rotate about an axis W/2 behind the screen (true cube). */
  function cube(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), [W] = size(a.parentNode), s = (V[o.dir ?? "rtl"][0] || -1), e = o.ease ?? "power2.inOut";
    gsap.set([a, b], { transformOrigin: `50% 50% ${-W / 2}px`, transformPerspective: o.persp ?? 2600, backfaceVisibility: "hidden" });
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.to(a, { rotationY: 90 * s, filter: "brightness(0.55)", duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    tl.fromTo(b, { rotationY: -90 * s, filter: "brightness(0.55)" }, { rotationY: 0, filter: "brightness(1)", duration: d, ease: e }, t);
    cue("cube", c, "whoosh_soft"); return tl;
  }

  /** TR-033 page turn. Arabic book (dir rtl): hinge on the right edge; the page swings away (into the screen) uncovering B from the left. */
  function pageTurn(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), rtl = (o.dir ?? "rtl") === "rtl";
    gsap.set(a, { transformOrigin: rtl ? "100% 50%" : "0% 50%", transformPerspective: o.persp ?? 2200, backfaceVisibility: "hidden" });
    enter(b); tl.set(b, { autoAlpha: 1 }, t).set(a, { zIndex: 5 }, t).set(a, { zIndex: "" }, t + d); // the page lies on top of B
    tl.to(a, { rotationY: rtl ? -90 : 90, filter: "brightness(0.7)", duration: d, ease: o.ease ?? "power2.in" }, t).set(a, { autoAlpha: 0 }, t + d);
    tl.fromTo(b, { filter: "brightness(0.7)" }, { filter: "brightness(1)", duration: d, ease: "power2.out" }, t);
    cue("pageTurn", c, "paper"); return tl;
  }

  /** TR-040 edge wipe with a colour bar on the seam (Opus wipe): clip-path inset on B, quart.inOut, optional 3 f peek. */
  function wipe(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), dir = o.dir ?? "rtl", v = V[dir], [W, H] = size(b.parentNode), e = o.ease ?? "power4.inOut";
    const from = { rtl: "inset(0% 0% 0% 100%)", ltr: "inset(0% 100% 0% 0%)", up: "inset(100% 0% 0% 0%)", down: "inset(0% 0% 100% 0%)" }[dir];
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.fromTo(b, { clipPath: from }, { clipPath: "inset(0% 0% 0% 0%)", duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    const bw = (o.bar ?? 24) * k(b.parentNode);
    if (bw) {
      const L = v[0] ? W : H, ax = v[0] ? "x" : "y", neg = (v[0] || v[1]) < 0;
      const bar = div(b.parentNode, `left:0;top:0;${v[0] ? `width:${bw}px;height:100%` : `height:${bw}px;width:100%`};background:${o.barColor ?? "#CF6E56"};z-index:50`);
      const p0 = neg ? L : -bw, p1 = neg ? -bw : L, pk = neg ? -bw * 0.7 : bw * 0.7;
      gsap.set(bar, { [ax]: p0, autoAlpha: 0 });
      tl.set(bar, { autoAlpha: 1 }, t - (o.peek ? 3 * F : 0));
      if (o.peek) tl.to(bar, { [ax]: p0 + pk, duration: 3 * F, ease: "power1.out" }, t - 3 * F);
      tl.to(bar, { [ax]: p1, duration: d, ease: e }, t).set(bar, { autoAlpha: 0 }, t + d);
    }
    cue("wipe", c, "transition_swipe"); return tl;
  }

  /** TR-041 iris from a point / UI element (o.at = [x,y] px or an element). expo.in like the Opus reel; ring rides the edge. */
  function iris(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), [W, H] = size(b.parentNode);
    let [x, y] = Array.isArray(o.at) ? o.at : [W / 2, H / 2];
    if (o.at && !Array.isArray(o.at)) { const r = $(o.at).getBoundingClientRect(), p = b.parentNode.getBoundingClientRect(); x = r.left - p.left + r.width / 2; y = r.top - p.top + r.height / 2; }
    const R = Math.hypot(Math.max(x, W - x), Math.max(y, H - y)) + 4, e = o.ease ?? (soft(o) ? "power3.inOut" : "expo.in");
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.fromTo(b, { clipPath: `circle(0px at ${x}px ${y}px)` }, { clipPath: `circle(${R}px at ${x}px ${y}px)`, duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    if (o.ring !== false) {
      const rw = (o.ringWidth ?? 10) * k(b.parentNode);
      const ring = div(b.parentNode, `left:${x - R}px;top:${y - R}px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;box-sizing:border-box;border:${rw}px solid ${o.ringColor ?? "#CF6E56"};z-index:50`);
      gsap.set(ring, { scale: 0, autoAlpha: 0 });
      tl.set(ring, { autoAlpha: 1 }, t).to(ring, { scale: 1, duration: d, ease: e }, t).set(ring, { autoAlpha: 0 }, t + d);
    }
    cue("iris", c, "whoosh_soft"); return tl;
  }

  /** TR-050 morph between two MG objects (FLIP): `from` flies onto `to`'s box while they crossfade. Build while both are at rest. */
  function morph(tl, from, to, t, d, o = {}) {
    from = $(from); to = $(to);
    const r1 = from.getBoundingClientRect(), r2 = to.getBoundingClientRect(), e = o.ease ?? "power3.inOut";
    const fwd = { x: r2.left - r1.left, y: r2.top - r1.top, scaleX: r2.width / r1.width, scaleY: r2.height / r1.height };
    const back = { x: r1.left - r2.left, y: r1.top - r2.top, scaleX: r1.width / r2.width, scaleY: r1.height / r2.height };
    gsap.set([from, to], { transformOrigin: "0 0" }); enter(to);
    tl.to(from, { ...fwd, duration: d, ease: e }, t).to(from, { autoAlpha: 0, duration: d * 0.35, ease: "none" }, t + d * 0.4);
    tl.fromTo(to, { ...back }, { x: 0, y: 0, scaleX: 1, scaleY: 1, duration: d, ease: e }, t)
      .fromTo(to, { autoAlpha: 0 }, { autoAlpha: 1, duration: d * 0.35, ease: "none" }, t + d * 0.3);
    cue("morph", t + d * 0.5, o.sfx ?? null); return tl;
  }

  /** TR-051 camera dolly through an MG world. world = preserve-3d wrapper, its children carry data-z (px, + = nearer).
   *  The camera travels o.dz px; layers fade just before they pass the lens. */
  function dolly(tl, world, t, d, o = {}) {
    world = $(world); const P = o.persp ?? 1200, dz = o.dz ?? 1600, e = gsap.parseEase(o.ease ?? "power2.inOut");
    gsap.set(world.parentNode, { perspective: P }); gsap.set(world, { transformStyle: "preserve-3d" });
    tl.fromTo(world, { z: 0 }, { z: dz, duration: d, ease: o.ease ?? "power2.inOut" }, t);
    [...world.children].forEach((L) => {
      const z = +(L.dataset.z ?? 0); gsap.set(L, { z });
      const need = P * 0.8 - z; if (need <= 0 || need >= dz) return; // never reaches the lens
      let lo = 0, hi = 1; for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; (e(m) * dz < need ? (lo = m) : (hi = m)); }
      tl.to(L, { autoAlpha: 0, duration: Math.min(6 * F, d * lo), ease: "power1.in" }, t + d * lo - Math.min(6 * F, d * lo));
    });
    cue("dolly", t + d * 0.5, "whoosh_soft"); return tl;
  }

  /** TR-052 portal / zoom-through an object (screen, window, card): A zooms until rect fills the frame; B rides inside it. o.rect=[x,y,w,h] or element. */
  function portal(tl, A, B, t, d, o = {}) {
    const [a, b] = ctx(A, B, t, d, o), [W, H] = size(a.parentNode); let [x, y, w, h] = Array.isArray(o.rect) ? o.rect : [0, 0, W, H];
    if (o.rect && !Array.isArray(o.rect)) { const r = $(o.rect).getBoundingClientRect(), p = a.parentNode.getBoundingClientRect(); [x, y, w, h] = [r.left - p.left, r.top - p.top, r.width, r.height]; }
    const cx = x + w / 2, cy = y + h / 2, s = Math.min(w / W, h / H), e = o.ease ?? "power3.inOut", rad = o.radius ?? 0;
    enter(b); tl.set(b, { autoAlpha: 1 }, t);
    tl.fromTo(a, { transformOrigin: `${cx}px ${cy}px` }, { x: W / 2 - cx, y: H / 2 - cy, scale: 1 / s, duration: d, ease: e }, t).set(a, { autoAlpha: 0 }, t + d);
    tl.fromTo(b, { x: cx - W / 2, y: cy - H / 2, scale: s, clipPath: `inset(0px round ${rad / s}px)` },
      { x: 0, y: 0, scale: 1, clipPath: "inset(0px round 0px)", duration: d, ease: e }, t);
    cue("portal", t + d * 0.6, "whoosh_soft"); return tl;
  }

  /** TR-060 zoom into a letter: word (inside A, coloured like B's background) scales about o.at=[px,py] (a point INSIDE a stroke,
   *  relative to the word box) until it fills the frame; B appears at the end. */
  function typeZoom(tl, word, B, t, d, o = {}) {
    word = $(word); const b = $(B), [px, py] = o.at ?? [word.offsetWidth / 2, word.offsetHeight / 2];
    enter(b);
    tl.fromTo(word, { transformOrigin: `${px}px ${py}px` }, { scale: o.scale ?? 60, duration: d, ease: o.ease ?? (soft(o) ? "power3.in" : "expo.in") }, t);
    tl.set(b, { autoAlpha: 1 }, t + d).set(word, { autoAlpha: 0 }, t + d);
    cue("typeZoom", t + d, "whoosh_fast"); return tl;
  }

  /** TR-070 ripple / heat-wave: displacement peaks on the cut, short crossfade. Heavy on video, fine on MG. */
  function ripple(tl, A, B, t, d, o = {}) {
    const [a, b, c, h1, h2] = ctx(A, B, t, d, o), xf = o.xfade ?? 4 * F;
    const [id, f] = filter(`<feTurbulence type="fractalNoise" baseFrequency="${o.freq ?? "0.006 0.012"}" numOctaves="2" seed="${o.seed ?? 3}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="0" xChannelSelector="R" yChannelSelector="G"/>`);
    const dm = f.lastChild; enter(b);
    tl.set([a, b], { filter: `url(#${id})` }, t).set([a, b], { filter: "none" }, t + d);
    tl.to(dm, { attr: { scale: (o.amp ?? 60) * k(a.parentNode) }, duration: h1, ease: "sine.in" }, t).to(dm, { attr: { scale: 0 }, duration: h2, ease: "sine.out" }, c);
    tl.fromTo(b, { autoAlpha: 0 }, { autoAlpha: 1, duration: xf, ease: "none" }, c - xf / 2).set(a, { autoAlpha: 0 }, c + xf / 2);
    cue("ripple", c, "swell"); return tl;
  }

  /** TR-080 glitch cut (scene): stepped x/skew jitter + contrast/hue every 2 f (seeded), hard swap on the cut. Tech/error beats only. */
  function glitchCut(tl, A, B, t, d, o = {}) {
    const [a, b, c] = ctx(A, B, t, d, o), R = rng(o.seed), amp = (o.amp ?? 40) * k(a.parentNode); enter(b);
    for (let f = t; f < t + d - 1e-6; f += 2 * F) {
      const el = f < c ? a : b, hit = R() < 0.6;
      tl.set(el, { x: hit ? (R() * 2 - 1) * amp : 0, skewX: hit ? (R() * 2 - 1) * 6 : 0, scale: hit ? 1.1 : 1,
        filter: hit ? `saturate(1.8) hue-rotate(${Math.round(R() * 90 - 45)}deg)` : "none" }, f); // no contrast push: cream must not go white
    }
    tl.set(b, { x: 0, skewX: 0, scale: 1, filter: "none" }, t + d);
    swap(tl, a, b, c); cue("glitchCut", c, "glitch"); return tl;
  }

  // ───────────────────────────── OVERLAY plates (alpha, over a hard cut) ─────────────────────────────
  const COL = "#181813";
  /** TR-042 cover wipe: a stage-colour panel crosses in dir; the cut hides under it; bars on both seams. */
  function coverWipe(tl, root, t, d, o = {}) {
    const [W, H] = size(root), v = V[o.dir ?? "rtl"], c = t + d * (o.cut ?? 0.5), bw = (o.bar ?? 24) * k(root), ax = v[0] ? "x" : "y", L = v[0] ? W : H;
    const p = div(root, `left:0;top:0;width:100%;height:100%;background:${o.color ?? COL}`);
    if (bw) [0, 1].forEach((i) => div(p, `${v[0] ? (i ? "right" : "left") : (i ? "bottom" : "top")}:-${bw}px;${v[0] ? `top:0;width:${bw}px;height:100%` : `left:0;height:${bw}px;width:100%`};background:${o.barColor ?? "#CF6E56"}`));
    const s = (v[0] || v[1]), off = L + bw;
    gsap.set(p, { [ax]: -s * off });
    tl.to(p, { [ax]: 0, duration: c - t, ease: o.in ?? "power3.in" }, t).to(p, { [ax]: s * off, duration: t + d - c, ease: o.out ?? "power3.out" }, c);
    cue("coverWipe", c, "transition_swipe"); return tl;
  }

  /** TR-043 doors / split panels: two halves close on the centre, cut, open. o.axis "h" (top+bottom) | "v" (left+right). */
  function doors(tl, root, t, d, o = {}) {
    const c = t + d * (o.cut ?? 0.5), hz = (o.axis ?? "h") === "h", col = o.color ?? COL;
    const p1 = div(root, `left:0;top:0;${hz ? "width:100%;height:50.5%" : "width:50.5%;height:100%"};background:${col}`);
    const p2 = div(root, `right:0;bottom:0;${hz ? "width:100%;height:50.5%" : "width:50.5%;height:100%"};background:${o.color2 ?? col}`);
    const pr = hz ? "yPercent" : "xPercent"; gsap.set(p1, { [pr]: -101 }); gsap.set(p2, { [pr]: 101 });
    tl.to([p1, p2], { [pr]: 0, duration: c - t, ease: "power3.in" }, t).to(p1, { [pr]: -101, duration: t + d - c, ease: "power3.out" }, c).to(p2, { [pr]: 101, duration: t + d - c, ease: "power3.out" }, c);
    cue("doors", c, "impact_soft"); return tl;
  }

  /** TR-044 blinds / slats (Opus: 8 slats, ~0.86 f stagger). Close from the top, open towards the bottom. */
  function blinds(tl, root, t, d, o = {}) {
    const c = t + d * (o.cut ?? 0.5), n = o.n ?? 8, st = o.stagger ?? 0.86 * F, h1 = c - t, h2 = t + d - c;
    const sl = Array.from({ length: n }, (_, i) => div(root, `left:0;top:${(i * 100) / n}%;width:100%;height:${100 / n + 0.2}%;background:${o.color ?? COL}`));
    gsap.set(sl, { scaleY: 0, transformOrigin: "50% 0%" });
    tl.to(sl, { scaleY: 1, duration: Math.max(F, h1 - st * (n - 1)), ease: "power2.in", stagger: st }, t);
    tl.set(sl, { transformOrigin: "50% 100%" }, c);
    tl.to(sl, { scaleY: 0, duration: Math.max(F, h2 - st * (n - 1)), ease: "power2.out", stagger: st }, c);
    cue("blinds", c, "transition_swipe"); return tl;
  }

  /** TR-045 colour bars: 3 bands sweep across staggered 2 f (palette colours), cut, sweep out the same way. */
  function bars(tl, root, t, d, o = {}) {
    const [W, H] = size(root), v = V[o.dir ?? "rtl"], c = t + d * (o.cut ?? 0.5), cols = o.colors ?? ["#CF6E56", "#ECECDE", COL], n = o.n ?? 3, st = o.stagger ?? 2 * F;
    const ax = v[0] ? "x" : "y", L = v[0] ? W : H, s = v[0] || v[1];
    const b = Array.from({ length: n }, (_, i) => div(root, v[0] ? `left:0;top:${(i * 100) / n}%;width:100%;height:${100 / n + 0.2}%;background:${cols[i % cols.length]}`
      : `top:0;left:${(i * 100) / n}%;height:100%;width:${100 / n + 0.2}%;background:${cols[i % cols.length]}`));
    gsap.set(b, { [ax]: -s * L });
    tl.to(b, { [ax]: 0, duration: c - t - st * (n - 1), ease: "power3.in", stagger: st }, t);
    tl.to(b, { [ax]: s * L, duration: t + d - c - st * (n - 1), ease: "power3.out", stagger: st }, c);
    cue("bars", c, "transition_swipe"); return tl;
  }

  /** TR-046 iris cover from a point: a disc grows to cover (in), cut, a hole opens from the same point (out). SVG mask, transform only. */
  function irisCover(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.5), [x, y] = o.at ?? [W / 2, H / 2], R = Math.hypot(Math.max(x, W - x), Math.max(y, H - y)) + 4, id = "trm" + ++uid;
    const wrap = div(root, "left:0;top:0;width:100%;height:100%");
    wrap.innerHTML = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="position:absolute;inset:0"><defs><mask id="${id}"><rect width="${W}" height="${H}" fill="#fff"/><circle class="h" cx="${x}" cy="${y}" r="${R}" fill="#000"/></mask></defs>
      <circle class="disc" cx="${x}" cy="${y}" r="${R}" fill="${o.color ?? COL}"/><rect class="pane" width="${W}" height="${H}" fill="${o.color ?? COL}" mask="url(#${id})"/></svg>`;
    const disc = wrap.querySelector(".disc"), pane = wrap.querySelector(".pane"), hole = wrap.querySelector(".h");
    gsap.set(disc, { svgOrigin: `${x} ${y}`, scale: 0 }); gsap.set(hole, { svgOrigin: `${x} ${y}`, scale: 0 }); gsap.set(pane, { autoAlpha: 0 });
    tl.to(disc, { scale: 1, duration: c - t, ease: o.in ?? "power3.in" }, t).set(disc, { autoAlpha: 0 }, c).set(pane, { autoAlpha: 1 }, c);
    tl.to(hole, { scale: 1, duration: t + d - c, ease: o.out ?? "power3.out" }, c).set(pane, { autoAlpha: 0 }, t + d);
    cue("irisCover", c, "whoosh_soft"); return tl;
  }

  /** TR-047 ink / liquid cover: seeded blobs under a gooey filter grow from o.from (right|left|top|bottom|center), cut, recede. */
  function ink(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.5), R = rng(o.seed), cols = 5, rows = 9, cw = W / cols, ch = H / rows, rad = Math.hypot(cw, ch) * 0.75;
    const [gid] = filter(`<feGaussianBlur in="SourceGraphic" stdDeviation="${18 * k(root)}" result="b"/><feColorMatrix in="b" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 28 -11"/>`);
    const box = div(root, `left:0;top:0;width:100%;height:100%;filter:url(#${gid})`);
    const org = { right: [W * 1.1, H / 2], left: [-W * 0.1, H / 2], top: [W / 2, -H * 0.1], bottom: [W / 2, H * 1.1], center: [W / 2, H / 2] }[o.from ?? "right"];
    const blobs = [];
    for (let i = -1; i <= cols; i++) for (let j = -1; j <= rows; j++) {
      const x = (i + 0.5) * cw + (R() - 0.5) * cw * 0.6, y = (j + 0.5) * ch + (R() - 0.5) * ch * 0.6, r = rad * (0.85 + R() * 0.4);
      const e = div(box, `left:${x - r}px;top:${y - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;background:${o.color ?? COL}`);
      blobs.push([Math.hypot(x - org[0], y - org[1]) + R() * cw * 0.8, e]);
    }
    blobs.sort((p, q) => p[0] - q[0]); const els = blobs.map((b) => b[1]), n = els.length;
    gsap.set(els, { scale: 0 });
    const h1 = c - t, h2 = t + d - c;
    tl.to(els, { scale: 1, duration: h1 * 0.45, ease: "power2.out", stagger: (h1 * 0.55) / n }, t);
    tl.to(els, { scale: 0, duration: h2 * 0.45, ease: "power2.in", stagger: (h2 * 0.55) / n }, c);
    cue("ink", c, "swoosh_reverse"); return tl;
  }

  /** TR-048 mosaic tiles / shatter: square tiles pop in by distance from o.at (+seeded jitter, small spin), cut, pop out. */
  function tiles(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.5), R = rng(o.seed), n = o.cols ?? 6, s = W / n, rows = Math.ceil(H / s), [ax, ay] = o.at ?? [W / 2, H / 2];
    const list = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < rows; j++) {
      const e = div(root, `left:${i * s - 1}px;top:${j * s - 1}px;width:${s + 2}px;height:${s + 2}px;background:${o.color ?? COL}`);
      list.push([Math.hypot((i + 0.5) * s - ax, (j + 0.5) * s - ay) + R() * s, e, (R() - 0.5) * (o.spin ?? 30)]);
    }
    list.sort((p, q) => p[0] - q[0]); const h1 = c - t, h2 = t + d - c, st1 = (h1 * 0.5) / list.length, st2 = (h2 * 0.5) / list.length;
    list.forEach(([, e, r], i) => {
      gsap.set(e, { scale: 0, rotation: r });
      tl.to(e, { scale: 1, rotation: 0, duration: h1 * 0.5, ease: "power2.out" }, t + i * st1);
      tl.to(e, { scale: 0, rotation: -r, duration: h2 * 0.5, ease: "power2.in" }, c + i * st2);
    });
    cue("tiles", c, "click_ui"); return tl;
  }

  /** TR-090 soft light leak (warm, drifting). Peak on the cut. In an NLE set the plate's composite mode to Screen (compose.py layers it as an overlay). */
  function leak(tl, root, t, d, o = {}) {
    const c = t + d * (o.cut ?? 0.5), pk = o.peak ?? 0.75, R = rng(o.seed), w = div(root, "inset:-20%");
    const L = [
      "radial-gradient(ellipse 52% 110% at 10% 58%, rgb(255 241 197 / 85%), transparent 45%), radial-gradient(ellipse 72% 120% at 24% 54%, rgb(255 126 57 / 70%), transparent 66%)",
      "radial-gradient(ellipse 58% 105% at 78% 34%, rgb(255 79 61 / 60%), rgb(255 44 92 / 22%) 48%, transparent 76%)",
      "linear-gradient(104deg, transparent 24%, rgb(255 144 62 / 26%) 40%, rgb(255 236 200 / 60%) 51%, rgb(255 124 48 / 18%) 62%, transparent 78%)",
    ].map((bg, i) => div(w, `inset:0;background:${bg};filter:blur(${(30 + i * 10) * k(root)}px)`));
    gsap.set(w, { autoAlpha: 0 });
    tl.to(w, { autoAlpha: pk, duration: c - t, ease: "sine.out" }, t).to(w, { autoAlpha: 0, duration: t + d - c, ease: "sine.in" }, c);
    L.forEach((l, i) => tl.fromTo(l, { xPercent: (R() * 2 - 1) * 20, rotation: (R() - 0.5) * 8 }, { xPercent: (R() * 2 - 1) * 20, rotation: (R() - 0.5) * 8, duration: d, ease: "sine.inOut" }, t));
    cue("leak", c, null); return tl;
  }

  /** TR-091 soft film burn: warm radial from an edge expands (power2.in), peaks ≤ .85 on the cut (never pure white). Composite Screen. */
  function burn(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.5), [x, y] = o.at ?? [W * 0.95, H * 0.3], r = Math.max(W, H);
    const e = div(root, `left:${x - r}px;top:${y - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;background:radial-gradient(circle, rgb(255 233 196 / 90%) 0, rgb(255 168 84 / 80%) 22%, rgb(222 82 34 / 55%) 45%, transparent 68%);filter:blur(${20 * k(root)}px)`);
    gsap.set(e, { scale: 0.25, autoAlpha: 0 });
    tl.to(e, { scale: 1.6, autoAlpha: o.peak ?? 0.85, duration: c - t, ease: "power2.in" }, t).to(e, { scale: 2.2, autoAlpha: 0, duration: t + d - c, ease: "power2.out" }, c);
    cue("burn", c, "swell"); return tl;
  }

  /** TR-092 soft flash in a PALETTE colour (default: no white flashes): 2 f up to ≤ .4, 6 f down. */
  function flash(tl, root, t, d, o = {}) {
    const c = t + d * (o.cut ?? 0.25), e = div(root, `inset:0;background:${o.color ?? "#ECECDE"}`);
    gsap.set(e, { autoAlpha: 0 });
    tl.to(e, { autoAlpha: o.peak ?? 0.35, duration: c - t, ease: "power1.out" }, t).to(e, { autoAlpha: 0, duration: t + d - c, ease: "expo.out" }, c);
    cue("flash", c, "impact_soft"); return tl;
  }

  /** TR-093 colour flip: n solid frames of a palette colour exactly on the cut (Opus "flash frame"). */
  function colorFlip(tl, root, t, d, o = {}) {
    const e = div(root, `inset:0;background:${o.color ?? "#CF6E56"}`); gsap.set(e, { autoAlpha: 0 });
    tl.set(e, { autoAlpha: 1 }, t).set(e, { autoAlpha: 0 }, t + Math.max(F, d));
    cue("colorFlip", t, null); return tl;
  }

  /** TR-094 anime speed lines (shock / realisation). Stepped seeded rotation every 2 f. */
  function speedLines(tl, root, t, d, o = {}) {
    const R = rng(o.seed), col = o.color ?? "rgb(255 255 255 / 70%)";
    const e = div(root, `inset:-25%;background:repeating-conic-gradient(from 0deg at 50% 45%, ${col} 0 .5deg, transparent .5deg 5deg);-webkit-mask:radial-gradient(circle at 50% 45%, transparent 22%, #000 60%);mask:radial-gradient(circle at 50% 45%, transparent 22%, #000 60%)`);
    gsap.set(e, { autoAlpha: 0, scale: 1.1 });
    tl.to(e, { autoAlpha: o.peak ?? 0.8, duration: 3 * F, ease: "power1.out" }, t).to(e, { autoAlpha: 0, duration: 5 * F, ease: "power1.in" }, t + d - 5 * F);
    for (let f = t; f < t + d; f += 2 * F) tl.set(e, { rotation: R() * 5 }, f);
    cue("speedLines", t, "whoosh_fast"); return tl;
  }

  /** TR-095 object pass (phone/hand/card crosses the lens and hides the cut). o.src = PNG (alpha) or a phone silhouette is drawn. */
  function objectPass(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.5), v = V[o.dir ?? "up"], w = W * 1.25, h = H * 1.25;
    const e = div(root, `left:${(W - w) / 2}px;top:${(H - h) / 2}px;width:${w}px;height:${h}px`);
    if (o.src) e.innerHTML = `<img src="${o.src}" style="width:100%;height:100%;object-fit:cover">`;
    else e.innerHTML = `<div style="position:absolute;inset:0;border-radius:${150 * k(root)}px;background:${o.color ?? "#0E0E0C"};box-shadow:0 0 0 ${10 * k(root)}px #3a3a36 inset"></div><div style="position:absolute;left:30%;right:30%;top:${40 * k(root)}px;height:${50 * k(root)}px;border-radius:${30 * k(root)}px;background:#000"></div>`;
    const ax = v[0] ? "x" : "y", L = (v[0] ? W + w : H + h) / 2 + 20, s = v[0] || v[1];
    gsap.set(e, { [ax]: -s * L, rotation: -(o.rot ?? 10) * s });
    tl.to(e, { [ax]: 0, rotation: 0, duration: c - t, ease: "power2.in" }, t).to(e, { [ax]: s * L, rotation: (o.rot ?? 10) * s, duration: t + d - c, ease: "power2.out" }, c);
    cue("objectPass", c, "whoosh_soft"); return tl;
  }

  /** TR-061 kashida wipe (Arabic typography wipe): word pops, its kashida bar stretches R→L across the frame, thickens to
   *  cover (cut), then collapses to reveal. Whole-word text only, never split. */
  function kashidaWipe(tl, root, t, d, o = {}) {
    const [W, H] = size(root), c = t + d * (o.cut ?? 0.55), h1 = c - t, col = o.color ?? "#ECECDE", bh = 18 * k(root), y = o.y ?? H * 0.5;
    const fs = o.size ?? 130 * k(root); // baseline of the word sits on the bar (Alexandria baseline ≈ 0.78 em in a 1.0 line box)
    const word = div(root, `left:0;right:0;top:${y - fs * 0.78}px;text-align:center;direction:rtl;font:800 ${fs}px/1 ${o.font ?? "Alexandria, sans-serif"};color:${col}`);
    word.textContent = o.word ?? "بعدين";
    const bar = div(root, `left:0;top:${y - bh / 2}px;width:100%;height:${bh}px;background:${o.barColor ?? col}`);
    gsap.set(word, { autoAlpha: 0, scale: 0.8 }); gsap.set(bar, { scaleX: 0, transformOrigin: "100% 50%" });
    tl.to(word, { autoAlpha: 1, scale: 1, duration: h1 * 0.3, ease: "back.out(1.6)" }, t);
    tl.to(bar, { scaleX: 1, duration: h1 * 0.35, ease: "power3.out" }, t + h1 * 0.25);
    tl.to(bar, { scaleY: (H / bh) * 2.1, duration: h1 * 0.4, ease: "power3.in" }, t + h1 * 0.6).set(word, { autoAlpha: 0 }, c);
    tl.to(bar, { scaleY: 0, duration: t + d - c, ease: "power3.out" }, c);
    cue("kashidaWipe", c, "transition_swipe"); return tl;
  }

  /** TR-081 glitch slices overlay: seeded palette bars jump every 2 f around the cut. Pair with a hard cut or glitchCut. */
  function glitchSlices(tl, root, t, d, o = {}) {
    const [, H] = size(root), R = rng(o.seed), cols = o.colors ?? ["#CF6E56", "#ECECDE", COL], n = o.n ?? 7;
    const sl = Array.from({ length: n }, (_, i) => div(root, `left:-10%;width:120%;top:0;height:10px;background:${cols[i % cols.length]}`));
    gsap.set(sl, { autoAlpha: 0 });
    for (let f = t; f < t + d - 1e-6; f += 2 * F)
      sl.forEach((s) => tl.set(s, { autoAlpha: R() < 0.55 ? 1 : 0, y: R() * H, scaleY: 1 + R() * 14, x: (R() - 0.5) * 120 }, f));
    tl.set(sl, { autoAlpha: 0 }, t + d);
    cue("glitchSlices", t + d / 2, "glitch"); return tl;
  }

  /** TR-096 shock ring accent (pairs with morphs / word slams / iris). */
  function rings(tl, root, t, d, o = {}) {
    const [W, H] = size(root), [x, y] = o.at ?? [W / 2, H / 2], r = (o.r ?? 260) * k(root);
    const e = div(root, `left:${x - r}px;top:${y - r}px;width:${2 * r}px;height:${2 * r}px;border-radius:50%;box-sizing:border-box;border:${(o.w ?? 8) * k(root)}px solid ${o.color ?? "#ECECDE"}`);
    gsap.set(e, { scale: 0.2, autoAlpha: 0 });
    tl.set(e, { autoAlpha: 1 }, t).to(e, { scale: o.to ?? 2, duration: d, ease: "power2.out" }, t).to(e, { autoAlpha: 0, duration: d * 0.6, ease: "power1.in" }, t + d * 0.4);
    cue("rings", t, "pop"); return tl;
  }

  const SCENE = { zoom, whip, push, slideOver, spin, blurCut, scaleInPlace, cardFlip, mirrorFlip, cube, pageTurn, wipe, iris, portal, ripple, glitchCut };
  const SPECIAL = { morph, dolly, typeZoom }; // (tl, from|world|word, to|B, t, d, o)
  const OVERLAY = { coverWipe, doors, blinds, bars, irisCover, ink, tiles, leak, burn, flash, colorFlip, speedLines, objectPass, kashidaWipe, glitchSlices, rings };
  G.TR = { F, rng, cues, dirBlur, SCENE, OVERLAY, SPECIAL, ...SCENE, ...SPECIAL, ...OVERLAY,
    kind: (n) => (n in SCENE ? "scene" : n in OVERLAY ? "overlay" : n in SPECIAL ? "special" : null) };
})(typeof window !== "undefined" ? window : globalThis);
