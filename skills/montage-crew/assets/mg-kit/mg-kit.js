/* mg-kit.js — idea-driven motion-graphics helpers for HyperFrames (GSAP 3.14, seek-safe).
 * Load after gsap.min.js (rtl-kit.js optional). Exposes window.MG. Styles: mg-kit.css.
 * Doc: references/mg-brain.md (what to show + layout modes) and references/mg-techniques.md (MG-NNN recipes).
 *
 * Conventions (same as rtl-kit.js):
 *  - every animating helper ADDS tweens to a paused timeline `tl` at absolute time `t` (seconds) and returns
 *    a handle (geometry / elements / end time). Canvas = 1080x1920 CSS px (render 4K with --resolution portrait-4k).
 *  - calls on the SAME element must be made in chronological order (state chains: frameTo, morph, takeover).
 *  - seek-safe: no Math.random (MG.rng(seed)), no repeat:-1, no wall clock; no CSS transform on elements GSAP
 *    transforms (mg-kit.css has none); never tween a timed `.clip` element — tween an untimed child/wrapper.
 *  - SVG used with draw/travel/particles shares the stage coordinate space: <svg class="mg-svg" viewBox="0 0 1080 1920">.
 */
(function () {
  const F = 1 / 30, W = 1080, H = 1920;
  const $ = (x) => (typeof x === "string" ? document.querySelector(x) : x);
  const $$ = (x) => (typeof x === "string" ? [...document.querySelectorAll(x)] : x.length != null ? [...x] : [x]);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const n2 = (v) => +v.toFixed(2);

  /** Append HTML to parent and return the new element. */
  function el(parent, html) {
    const t = document.createElement("template");
    t.innerHTML = html.trim();
    const n = t.content.firstElementChild;
    $(parent).appendChild(n);
    return n;
  }
  /** Seeded PRNG (mulberry32) -> () => [0,1). Use instead of Math.random. */
  function rng(seed = 1) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const place = (e, r) => gsap.set(e, { left: r[0], top: r[1], width: r[2], height: r[3] });

  /* ------------------------------------------------------------------ 1. LAYOUT MODES (speaker frame)
   * The speaker element is an UNTIMED wrapper (class mg-spk) holding the speaker's <video data-start data-media-start>
   * (or the A-roll composite). frameTo() moves/scales/clips it between named layouts; all shapes are
   * inset() rounded rects, so circle <-> card <-> split <-> full interpolate cleanly.
   * face = head centre + head half-height in the SOURCE frame (from zones.json: MG.faceFromBox(head_bbox)). */
  const FACE = { x: 540, y: 640, r: 170 };
  const LAYOUTS = {
    full:            { rect: [0, 0, W, H], radius: 0, zoom: 1 },
    "split-top":     { rect: [0, 0, W, 960], zoom: 1, faceAt: 0.5 },     // speaker top half, MG stage bottom half
    "split-bottom":  { rect: [0, 960, W, 960], zoom: 1, faceAt: 0.42 },  // MG stage top, speaker bottom (keep chin < 1480)
    "side-right":    { rect: [540, 0, 540, H], zoom: 1, faceAt: 0.34 },  // RTL: speaker first (right), content left
    "stage-card":    { rect: [150, 300, 780, 1000], radius: 56, faceAt: 0.4 }, // speaker as a big card on the MG world
    "card-top":      { rect: [190, 300, 700, 560], radius: 48, faceAt: 0.5 },  // speaker small-top, content below
    "card-bl":       { rect: [70, 990, 340, 470], radius: 44, faceAt: 0.45 },
    "card-br":       { rect: [600, 990, 340, 470], radius: 44, faceAt: 0.45 },  // x <= 940: clear of the IG right rail
    "circle-bl":     { rect: [70, 1110, 360, 360], radius: 180, faceAt: 0.5 },
    "circle-br":     { rect: [600, 1120, 340, 340], radius: 170, faceAt: 0.5 },
    "circle-tl":     { rect: [130, 300, 320, 320], radius: 160, faceAt: 0.5 },
    "circle-tr":     { rect: [630, 300, 320, 320], radius: 160, faceAt: 0.5 },
    "circle-center": { rect: [340, 1060, 400, 400], radius: 200, faceAt: 0.5 },
    "device-phone":  { rect: [312, 470, 456, 990], radius: 58, faceAt: 0.36 }, // inside MG.ui.phone({rect:[300,458,480,1014]})
    dot:             { rect: [520, 1240, 40, 40], radius: 20, faceAt: 0.5 },   // shrink-to-dot exit of a takeover
  };
  /** zones.json head_bbox [x1,y1,x2,y2] (danger box incl. hair + margin) -> face {x,y,r}. */
  const faceFromBox = (b) => ({ x: (b[0] + b[2]) / 2, y: (b[1] + b[3]) / 2, r: (b[3] - b[1]) / 2 / 1.25 });

  /** Geometry of a layout: {rect, radius, s, x, y, clip}. o: {face, rect, radius, zoom, faceAt}. */
  function layout(name, o = {}) {
    const p = typeof name === "string" ? LAYOUTS[name] : name;
    if (!p) throw new Error("MG.layout: unknown layout " + name);
    const face = { ...FACE, ...(o.face || {}) };
    const [x, y, w, h] = o.rect || p.rect;
    const radius = o.radius ?? p.radius ?? 0;
    const round = radius >= Math.min(w, h) / 2 - 0.5;
    const s = o.zoom ?? p.zoom ?? clamp(h / (face.r * 2 * (round ? 1.5 : 2.6)), 0.15, 1.6);
    const faceAt = o.faceAt ?? p.faceAt;
    let tx = 0, ty = 0;
    if (faceAt != null) {
      tx = x + w / 2 - s * face.x;
      ty = y + h * faceAt - s * face.y;
      // keep the source covering the rect (no empty edge) when it is big enough to do so
      if (s * W >= w) tx = clamp(tx, x + w - s * W, x);
      if (s * H >= h) ty = clamp(ty, y + h - s * H, y);
    }
    const lx = (x - tx) / s, ly = (y - ty) / s, lw = w / s, lh = h / s;
    const clip = `inset(${n2(ly)}px ${n2(W - lx - lw)}px ${n2(H - ly - lh)}px ${n2(lx)}px round ${n2(radius / s)}px)`;
    return { name, rect: [x, y, w, h], radius, s: n2(s), x: n2(tx), y: n2(ty), clip };
  }

  /** Move the speaker wrapper into a layout. to = name | geometry. o: {dur=.8, ease, face, rect, zoom, faceAt, radius}.
   *  Default motion = smooth (default: never snapped). dur 0 = hard reframe on a cut. */
  function frameTo(tl, target, t, to, o = {}) {
    const e = $(target);
    const g = typeof to === "object" && to.clip ? to : layout(to, o);
    if (!e._mgGeom) {
      e._mgGeom = layout("full");
      gsap.set(e, { transformOrigin: "0 0" });
      tl.set(e, { x: 0, y: 0, scale: 1, clipPath: e._mgGeom.clip }, 0);
    }
    const a = e._mgGeom;
    tl.fromTo(e, { x: a.x, y: a.y, scale: a.s, clipPath: a.clip },
      { x: g.x, y: g.y, scale: g.s, clipPath: g.clip, duration: o.dur ?? 0.8, ease: o.ease ?? "power3.inOut",
        immediateRender: false }, t);
    e._mgGeom = g;
    return g;
  }

  /** Thin accent ring/hairline around a layout rect (div.mg-ring). Returns the ring; exit with MG.out(). */
  function ring(tl, parent, t, g, o = {}) {
    const pad = o.pad ?? 8, [x, y, w, h] = g.rect;
    const r = el(parent, `<div class="mg-ring"></div>`);
    gsap.set(r, { left: x - pad, top: y - pad, width: w + 2 * pad, height: h + 2 * pad, borderRadius: g.radius + pad });
    tl.fromTo(r, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: o.dur ?? 10 * F, ease: "power3.out" }, t);
    return r;
  }

  /* ------------------------------------------------------------------ 2. TAKEOVER (full-frame MG stage over him)
   * stage = an UNTIMED full-frame div above the speaker wrapper. styles:
   *  wipe (edge bar, from right|left|top|bottom, quart.inOut 8 f) · iris (from a point, expo.in 10 f) ·
   *  push (stage slides up, speaker drops back) · blur-whip (sideways blur swap) · fade (matched-position crossfade).
   *  giveBack() = the same style reversed, continuing the direction. Returns the end time. */
  const WIPE = { right: "inset(0% 0% 0% 100%)", left: "inset(0% 100% 0% 0%)", bottom: "inset(100% 0% 0% 0%)", top: "inset(0% 0% 100% 0%)" };
  const OPP = { right: "left", left: "right", top: "bottom", bottom: "top" };
  const FULLCLIP = "inset(0% 0% 0% 0%)";
  function edgeBar(tl, stage, t, d, dir, ease, color) {
    const vert = dir === "top" || dir === "bottom";
    const b = el(stage.parentNode, `<div class="mg-edge-bar"></div>`);
    gsap.set(b, vert ? { left: 0, width: W, top: 0, height: 24 } : { top: 0, height: H, left: 0, width: 24 });
    if (color) b.style.background = color;
    const p = { right: [W, -24], left: [-24, W], bottom: [H, -24], top: [-24, H] }[dir];
    tl.fromTo(b, vert ? { y: p[0] } : { x: p[0] }, { ...(vert ? { y: p[1] } : { x: p[1] }), duration: d, ease, immediateRender: false }, t);
    gsap.set(b, { opacity: 0 });
    tl.set(b, { opacity: 0 }, 0).set(b, { opacity: 1 }, t).set(b, { opacity: 0 }, t + d);
  }
  function takeover(tl, stage, t, o = {}) {
    const s = $(stage), style = o.style ?? "wipe", under = o.under ? $(o.under) : null;
    if (!s._mgOn) { s._mgOn = true; gsap.set(s, { clipPath: WIPE.right }); tl.set(s, { clipPath: WIPE.right, opacity: 1 }, 0); } // hidden from frame 0
    let d;
    if (style === "wipe") {
      const dir = o.from ?? "right"; d = o.dur ?? 8 * F;
      tl.fromTo(s, { clipPath: WIPE[dir] }, { clipPath: FULLCLIP, duration: d, ease: "power4.inOut", immediateRender: false }, t);
      if (o.bar !== false) edgeBar(tl, s, t, d, dir, "power4.inOut", o.barColor);
    } else if (style === "iris") {
      const [x, y] = o.at ?? [540, 960]; d = o.dur ?? 10 * F;
      tl.fromTo(s, { clipPath: `circle(0px at ${x}px ${y}px)` }, { clipPath: `circle(2300px at ${x}px ${y}px)`,
        duration: d, ease: "expo.in", immediateRender: false }, t);
    } else if (style === "push") {
      d = o.dur ?? 12 * F;
      tl.set(s, { clipPath: FULLCLIP }, t);
      tl.fromTo(s, { yPercent: 100 }, { yPercent: 0, duration: d, ease: "power3.inOut", immediateRender: false }, t);
      if (under) tl.fromTo(under, { yPercent: 0, filter: "brightness(1)" }, { yPercent: -22, filter: "brightness(.45)", duration: d, ease: "power3.inOut", immediateRender: false }, t);
    } else if (style === "blur-whip") {
      d = o.dur ?? 10 * F; const dx = o.dir === "ltr" ? -1 : 1; // RTL default: new content comes from the right
      tl.set(s, { clipPath: FULLCLIP }, t);
      tl.fromTo(s, { x: 260 * dx, opacity: 0, filter: "blur(30px)" }, { x: 0, opacity: 1, filter: "blur(0px)", duration: d, ease: "power3.out", immediateRender: false }, t);
      if (under) tl.fromTo(under, { filter: "blur(0px)", opacity: 1 }, { filter: "blur(30px)", opacity: 0, duration: d * 0.7, ease: "power2.in", immediateRender: false }, t);
    } else { // fade
      d = o.dur ?? 8 * F;
      tl.set(s, { clipPath: FULLCLIP }, t);
      tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: d, ease: "power2.inOut", immediateRender: false }, t);
    }
    s._mgStyle = { style, o };
    return t + d;
  }
  function giveBack(tl, stage, t, o = {}) {
    const s = $(stage), prev = s._mgStyle || { style: "wipe", o: {} };
    const style = o.style ?? prev.style, under = (o.under ?? prev.o.under) ? $(o.under ?? prev.o.under) : null;
    let d;
    if (style === "wipe") {
      const dir = o.from ?? prev.o.from ?? "right"; d = o.dur ?? 8 * F;
      // the stage leaves the way the wipe was travelling: clip collapses toward the far side
      const to = WIPE[OPP[dir]];
      tl.fromTo(s, { clipPath: FULLCLIP }, { clipPath: to, duration: d, ease: "power4.inOut", immediateRender: false }, t);
      if (o.bar !== false && prev.o.bar !== false) edgeBar(tl, s, t, d, dir, "power4.inOut", o.barColor ?? prev.o.barColor);
    } else if (style === "iris") {
      const [x, y] = o.at ?? prev.o.at ?? [540, 960]; d = o.dur ?? 10 * F;
      tl.fromTo(s, { clipPath: `circle(2300px at ${x}px ${y}px)` }, { clipPath: `circle(0px at ${x}px ${y}px)`, duration: d, ease: "expo.out", immediateRender: false }, t);
    } else if (style === "push") {
      d = o.dur ?? 12 * F;
      tl.fromTo(s, { yPercent: 0 }, { yPercent: -100, duration: d, ease: "power3.inOut", immediateRender: false }, t);
      if (under) tl.fromTo(under, { yPercent: 22, filter: "brightness(.45)" }, { yPercent: 0, filter: "brightness(1)", duration: d, ease: "power3.inOut", immediateRender: false }, t);
    } else if (style === "blur-whip") {
      d = o.dur ?? 10 * F;
      tl.fromTo(s, { x: 0, opacity: 1, filter: "blur(0px)" }, { x: -260, opacity: 0, filter: "blur(30px)", duration: d, ease: "power3.in", immediateRender: false }, t);
      if (under) tl.fromTo(under, { filter: "blur(30px)", opacity: 0 }, { filter: "blur(0px)", opacity: 1, duration: d, ease: "power3.out", immediateRender: false }, t + d * 0.3);
    } else {
      d = o.dur ?? 8 * F;
      tl.fromTo(s, { opacity: 1 }, { opacity: 0, duration: d, ease: "power2.inOut", immediateRender: false }, t);
    }
    tl.set(s, { clipPath: WIPE.right, x: 0, yPercent: 0, opacity: 1, filter: "none" }, t + d);
    return t + d;
  }

  /** Background colour flip of a stage (3-colour world: never the same colour twice in a row). */
  const flipColor = (tl, stage, t, color, o = {}) =>
    tl.to($(stage), { backgroundColor: color, duration: o.dur ?? 6 * F, ease: o.ease ?? "power2.inOut" }, t);
  /** Finite grid drift (stage with .mg-grid): px/s along x and y. */
  function gridDrift(tl, stage, t, dur, o = {}) {
    const v = o.speed ?? 40;
    return tl.fromTo($(stage), { backgroundPosition: "0px 0px" }, { backgroundPosition: `${v * dur}px ${v * dur}px`, duration: dur, ease: "none" }, t);
  }

  /* ------------------------------------------------------------------ 3. PATHS: draw, travel, morph */
  /** Stroke draw-on (SVG path/line/circle/polyline). o: {dur=18f, ease, stagger, reverse}. Hidden before t. */
  function draw(tl, targets, t, o = {}) {
    $$(targets).forEach((p, i) => {
      const L = p.getTotalLength();
      p.style.strokeDasharray = `${L} ${L + 2}`;
      tl.fromTo(p, { strokeDashoffset: (o.reverse ? -1 : 1) * (L + 1) }, { strokeDashoffset: 0, duration: o.dur ?? 18 * F,
        ease: o.ease ?? "power2.inOut" }, t + i * (o.stagger ?? 0));
    });
    return tl;
  }
  /** Stroke erase (the line runs away in its drawing direction). */
  function erase(tl, targets, t, o = {}) {
    $$(targets).forEach((p, i) => {
      const L = p.getTotalLength();
      tl.fromTo(p, { strokeDashoffset: 0 }, { strokeDashoffset: -(L + 1), duration: o.dur ?? 12 * F, ease: o.ease ?? "power2.in",
        immediateRender: false }, t + i * (o.stagger ?? 0));
    });
    return tl;
  }
  /** Move an element along an SVG path (stage coords). o: {dur, ease, from=0, to=1, rotate, cx, cy (element centre offset)}. */
  function travel(tl, target, path, t, o = {}) {
    const e = $(target), p = $(path), L = p.getTotalLength(), pr = { v: o.from ?? 0 };
    const put = (v) => {
      const q = p.getPointAtLength(L * v);
      let rot = 0;
      if (o.rotate) { const q2 = p.getPointAtLength(Math.min(L, L * v + 1)), q0 = p.getPointAtLength(Math.max(0, L * v - 1)); rot = (Math.atan2(q2.y - q0.y, q2.x - q0.x) * 180) / Math.PI; }
      gsap.set(e, { x: q.x - (o.cx ?? 0), y: q.y - (o.cy ?? 0), rotation: rot });
    };
    put(pr.v);
    return tl.fromTo(pr, { v: o.from ?? 0 }, { v: o.to ?? 1, duration: o.dur ?? 1, ease: o.ease ?? "power2.inOut",
      immediateRender: false, onUpdate: () => put(pr.v) }, t);
  }
  // --- morph: resample both shapes to N points, align start point + direction, interpolate.
  let probe;
  function samplePts(d, n) {
    if (!probe) {
      probe = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      probe.setAttribute("style", "position:absolute;width:0;height:0;overflow:hidden");
      document.body.appendChild(probe);
    }
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", d); probe.appendChild(p);
    const L = p.getTotalLength(), out = [];
    for (let i = 0; i < n; i++) { const q = p.getPointAtLength((L * i) / n); out.push([q.x, q.y]); }
    p.remove();
    return out;
  }
  function alignPts(a, b) {
    const n = a.length; let best = Infinity, res = b;
    for (const c of [b, [...b].reverse()]) for (let k = 0; k < n; k++) {
      let s = 0;
      for (let i = 0; i < n; i += 2) { const q = c[(i + k) % n]; s += (q[0] - a[i][0]) ** 2 + (q[1] - a[i][1]) ** 2; }
      if (s < best) { best = s; res = c.map((_, i) => c[(i + k) % n]); }
    }
    return res;
  }
  /** Morph an SVG <path> into another shape (any two paths: icon -> icon, blob -> card, logo -> logo).
   *  o: {dur=14f, ease, points=96, closed=true}. Exact source/target d at progress 0/1. Chain calls in time order. */
  function morph(tl, path, t, toD, o = {}) {
    const e = $(path), n = o.points ?? 96, fromD = e._mgD ?? e.getAttribute("d");
    const A = samplePts(fromD, n), B = (o.closed ?? true) ? alignPts(A, samplePts(toD, n)) : samplePts(toD, n);
    const pr = { v: 0 }, z = (o.closed ?? true) ? "Z" : "";
    const dash = e.style.strokeDasharray; // a draw() dash pattern would cut the new (longer) outline
    const paint = (v) => {
      e.style.strokeDasharray = v <= 0 ? dash : "none";
      if (v <= 0) return e.setAttribute("d", fromD);
      if (v >= 1) return e.setAttribute("d", toD);
      let s = "";
      for (let i = 0; i < n; i++) s += (i ? "L" : "M") + n2(A[i][0] + (B[i][0] - A[i][0]) * v) + " " + n2(A[i][1] + (B[i][1] - A[i][1]) * v);
      e.setAttribute("d", s + z);
    };
    e._mgD = toD;
    return tl.fromTo(pr, { v: 0 }, { v: 1, duration: o.dur ?? 14 * F, ease: o.ease ?? "power3.inOut", immediateRender: false,
      onUpdate: () => paint(pr.v) }, t);
  }
  /** Fake morph (different silhouettes / DOM objects): A grows + fades while B settles from smaller. */
  function swap(tl, a, b, t, o = {}) {
    const d = o.dur ?? 7 * F;
    tl.fromTo($(a), { opacity: 1, scale: 1 }, { opacity: 0, scale: o.grow ?? 1.08, filter: "blur(6px)", duration: d, ease: "power2.in", immediateRender: false }, t);
    tl.fromTo($(b), { opacity: 0, scale: o.from ?? 0.92, filter: "blur(6px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: d * 1.4, ease: "power3.out" }, t + d * 0.4);
    return tl;
  }

  /* ------------------------------------------------------------------ 4. TYPE (Arabic-safe: whole words or text substrings, never letter spans) */
  /** Opus-style spring pop per word at its final position (scale .6 -> 1.13 -> 1, 12 f). times[] = word onsets. */
  function springWords(tl, target, times, o = {}) {
    const e = $(target);
    if (!e.dataset.mgSplit) {
      const words = e.textContent.trim().split(/\s+/);
      e.textContent = "";
      words.forEach((w, i) => { if (i) e.append(" "); el(e, `<span class="mg-w"></span>`).textContent = w; });
      e.dataset.mgSplit = "1";
    }
    [...e.querySelectorAll(".mg-w")].forEach((s, i) => {
      const at = times[i] ?? times[times.length - 1] + (i - times.length + 1) * 8 * F;
      tl.fromTo(s, { opacity: 0, scale: o.from ?? 0.6, y: 14 }, { opacity: 1, scale: 1, y: 0, duration: o.dur ?? 12 * F, ease: o.ease ?? "back.out(2.5)" }, at);
    });
    return tl;
  }
  /** Typewriter into an element (prompt bar, chat, terminal). o: {cps=22, dur, by:'char'|'word', caret: el}. Returns end time. */
  function type(tl, target, t, text, o = {}) {
    const e = $(target), units = o.by === "word" ? text.split(/(\s+)/) : [...text];
    const d = o.dur ?? units.length / (o.cps ?? 22), pr = { v: 0 };
    e.textContent = "";
    tl.fromTo(pr, { v: 0 }, { v: units.length, duration: d, ease: "none", immediateRender: false,
      onUpdate: () => { e.textContent = units.slice(0, Math.floor(pr.v + 1e-6)).join(""); } }, t);
    if (o.caret) caret(tl, o.caret, t - 0.3, d + 0.9);
    return t + d;
  }
  /** Blinking caret for a finite time (period .53 s), ends visible. */
  function caret(tl, target, t, dur) {
    const k = Math.max(1, Math.floor(dur / 0.53));
    return tl.fromTo($(target), { opacity: 1 }, { opacity: 0, duration: 0.265, ease: "steps(1)", repeat: 2 * k - 1, yoyo: true }, t);
  }
  /** Reveal pre-coloured code/terminal lines as typing (clip + steps), keeps syntax colours. o: {cps=30, gap=4f, rtl}. Returns end time. */
  function typeLines(tl, lines, t, o = {}) {
    let at = t;
    $$(lines).forEach((l) => {
      const n = Math.max(1, l.textContent.length), d = o.instant?.includes?.(l) ? F : n / (o.cps ?? 30);
      tl.fromTo(l, { clipPath: o.rtl ? "inset(0% 0% 0% 100%)" : "inset(0% 100% 0% 0%)" },
        { clipPath: "inset(0% 0% 0% 0%)", duration: d, ease: `steps(${n})` }, at);
      at += d + (o.gap ?? 4 * F);
    });
    return at;
  }
  /** Strike a word (negation): accent bar sweeps right->left across it (RTL). */
  function strike(tl, target, t, o = {}) {
    const e = $(target);
    const s = el(e, `<span class="mg-strike"></span>`);
    tl.fromTo(s, { scaleX: 0, transformOrigin: o.ltr ? "0% 50%" : "100% 50%" }, { scaleX: 1, duration: o.dur ?? 8 * F, ease: "power3.out" }, t);
    if (o.dim !== false) tl.to(e, { opacity: 0.55, duration: 6 * F, ease: "power2.out" }, t + 6 * F);
    return s;
  }
  /** Slot-machine roll through words (tool names, options). Builds a masked column. Returns the box. */
  function roll(tl, parent, t, words, o = {}) {
    const box = el(parent, `<div class="mg-roll"><div class="mg-roll-col"></div></div>`);
    const col = box.firstElementChild, lh = o.lineHeight ?? 130;
    gsap.set(box, { height: lh, lineHeight: lh + "px" });
    words.forEach((w) => { el(col, `<div class="mg-roll-item"></div>`).textContent = w; });
    const step = o.step ?? 7 * F;
    words.forEach((_, i) => { if (i) tl.to(col, { y: -lh * i, duration: i === words.length - 1 ? 14 * F : step, ease: i === words.length - 1 ? "back.out(1.6)" : "power2.inOut" }, t + (i - 1) * step); });
    return box;
  }

  /* ------------------------------------------------------------------ 5. DATA */
  /** Count a number in an element (Western digits). o: {from=0, dur=1, ease='expo.out', prefix, suffix, decimals, sep}. */
  function count(tl, target, t, to, o = {}) {
    const e = $(target), pr = { v: o.from ?? 0 }, dec = o.decimals ?? 0;
    const fmt = (v) => { let s = v.toFixed(dec); if (o.sep) s = s.replace(/\B(?=(\d{3})+(?!\d))/g, o.sep); return (o.prefix ?? "") + s + (o.suffix ?? ""); };
    e.textContent = fmt(pr.v);
    return tl.fromTo(pr, { v: o.from ?? 0 }, { v: to, duration: o.dur ?? 1, ease: o.ease ?? "expo.out", immediateRender: false,
      onUpdate: () => { e.textContent = fmt(pr.v); } }, t);
  }
  /** Bar chart. data [{label, value, accent}] ; o: {rect:[x,y,w,h], horizontal, max, stagger=4f, suffix}.
   *  Vertical bars grow from the bottom; horizontal bars grow right->left (RTL). Returns the bar elements. */
  function bars(tl, parent, t, data, o = {}) {
    const box = el(parent, `<div class="mg-bars ${o.horizontal ? "is-h" : ""}"></div>`);
    place(box, o.rect ?? [140, 760, 800, 560]);
    const max = o.max ?? Math.max(...data.map((d) => d.value));
    return data.map((d, i) => {
      const b = el(box, `<div class="mg-bar ${d.accent ? "is-accent" : ""}"><div class="mg-bar-track"><div class="mg-bar-fill"></div></div><div class="mg-bar-val"></div><div class="mg-bar-lab"></div></div>`);
      const fill = b.querySelector(".mg-bar-fill"), val = b.querySelector(".mg-bar-val"), at = t + i * (o.stagger ?? 4 * F);
      b.querySelector(".mg-bar-lab").textContent = d.label ?? "";
      fill.style[o.horizontal ? "width" : "height"] = (100 * d.value) / max + "%";
      tl.fromTo(fill, o.horizontal ? { scaleX: 0, transformOrigin: "100% 50%" } : { scaleY: 0, transformOrigin: "50% 100%" },
        { scaleX: 1, scaleY: 1, duration: o.dur ?? 16 * F, ease: "power3.out" }, at);
      count(tl, val, at, d.value, { dur: o.dur ?? 16 * F, ease: "power3.out", suffix: o.suffix ?? "" });
      tl.fromTo(b.querySelector(".mg-bar-lab"), { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 8 * F, ease: "power3.out" }, at + 4 * F);
      return b;
    });
  }
  /** Line chart (+ area + end dot) in a stage svg. values = numbers left->right (time axis). o: {rect, max, min, dur=1.1}. */
  function lineChart(tl, svg, t, values, o = {}) {
    const [x, y, w, h] = o.rect ?? [140, 820, 800, 480], s = $(svg), NS = "http://www.w3.org/2000/svg";
    const max = o.max ?? Math.max(...values), min = o.min ?? Math.min(0, ...values);
    const P = values.map((v, i) => [x + (w * i) / (values.length - 1), y + h - ((v - min) / (max - min || 1)) * h]);
    const d = P.map((p, i) => (i ? "L" : "M") + n2(p[0]) + " " + n2(p[1])).join("");
    const area = document.createElementNS(NS, "path"), line = document.createElementNS(NS, "path"), dot = document.createElementNS(NS, "circle");
    area.setAttribute("d", d + `L${x + w} ${y + h}L${x} ${y + h}Z`); area.setAttribute("class", "mg-area");
    line.setAttribute("d", d); line.setAttribute("class", "mg-line");
    const last = P[P.length - 1]; dot.setAttribute("cx", last[0]); dot.setAttribute("cy", last[1]); dot.setAttribute("r", 14); dot.setAttribute("class", "mg-line-dot");
    s.append(area, line, dot);
    const dur = o.dur ?? 1.1;
    draw(tl, line, t, { dur, ease: "power2.inOut" });
    tl.fromTo(area, { clipPath: `inset(0px ${W - x}px 0px 0px)` }, { clipPath: `inset(0px 0px 0px 0px)`, duration: dur, ease: "power2.inOut" }, t);
    tl.fromTo(dot, { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 8 * F, ease: "back.out(2.5)" }, t + dur - 2 * F);
    return { line, area, dot, points: P };
  }
  /** Donut / ring fill to pct with a centred counter. o: {x, y (centre), size=420, stroke=46, label el or null}. */
  function donut(tl, parent, t, pct, o = {}) {
    const size = o.size ?? 420, sw = o.stroke ?? 46, r = (size - sw) / 2, C = 2 * Math.PI * r;
    const box = el(parent, `<div class="mg-donut"><svg viewBox="0 0 ${size} ${size}"><circle class="mg-donut-bg" cx="${size / 2}" cy="${size / 2}" r="${r}" stroke-width="${sw}"/><circle class="mg-donut-fg" cx="${size / 2}" cy="${size / 2}" r="${r}" stroke-width="${sw}"/></svg><div class="mg-donut-val"></div></div>`);
    place(box, [(o.x ?? 540) - size / 2, (o.y ?? 1000) - size / 2, size, size]);
    const fg = box.querySelector(".mg-donut-fg");
    fg.style.strokeDasharray = `${C} ${C}`;
    // RTL reading: fill counter-clockwise from 12 o'clock unless o.cw
    gsap.set(fg, { rotation: -90, scaleY: o.cw ? 1 : -1, transformOrigin: "50% 50%" });
    tl.fromTo(fg, { strokeDashoffset: C }, { strokeDashoffset: C * (1 - pct / 100), duration: o.dur ?? 1.2, ease: o.ease ?? "power3.inOut" }, t);
    count(tl, box.querySelector(".mg-donut-val"), t, pct, { dur: o.dur ?? 1.2, ease: o.ease ?? "power3.inOut", suffix: "%" });
    return box;
  }
  /** Semicircle gauge + needle to pct (0..100). o: {x, y (pivot), size=640}. */
  function gauge(tl, parent, t, pct, o = {}) {
    const S = o.size ?? 640, r = S / 2 - 30;
    const box = el(parent, `<div class="mg-gauge"><svg viewBox="0 0 ${S} ${S / 2 + 20}"><path class="mg-gauge-bg" d="M30 ${S / 2} A${r} ${r} 0 0 1 ${S - 30} ${S / 2}"/><path class="mg-gauge-fg" d="M30 ${S / 2} A${r} ${r} 0 0 1 ${S - 30} ${S / 2}"/></svg><div class="mg-needle"></div><div class="mg-gauge-val"></div></div>`);
    place(box, [(o.x ?? 540) - S / 2, (o.y ?? 1100) - S / 2, S, S / 2 + 20]);
    const fg = box.querySelector(".mg-gauge-fg"), L = fg.getTotalLength(), needle = box.querySelector(".mg-needle");
    fg.style.strokeDasharray = `${L} ${L}`;
    gsap.set(needle, { left: S / 2 - 6, top: 30, height: S / 2 - 30, transformOrigin: "50% 100%" });
    const d = o.dur ?? 1.3;
    tl.fromTo(fg, { strokeDashoffset: L }, { strokeDashoffset: L * (1 - pct / 100), duration: d, ease: "power3.inOut" }, t);
    tl.fromTo(needle, { rotation: -90 }, { rotation: -90 + 1.8 * pct, duration: d, ease: "back.out(1.2)" }, t);
    count(tl, box.querySelector(".mg-gauge-val"), t, pct, { dur: d, ease: "power3.inOut", suffix: o.suffix ?? "%" });
    return box;
  }
  /** Waffle grid (part of whole): n cells, `on` light up (RTL order: from the top-right). o: {rect, cols=10, stagger=1f}. */
  function waffle(tl, parent, t, o = {}) {
    const n = o.n ?? 100, cols = o.cols ?? 10, on = o.on ?? 0;
    const box = el(parent, `<div class="mg-waffle"></div>`);
    place(box, o.rect ?? [190, 700, 700, 700]);
    box.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    const cells = Array.from({ length: n }, () => el(box, `<div class="mg-cell"></div>`));
    tl.fromTo(cells, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 8 * F, ease: "back.out(1.8)", stagger: { each: o.stagger ?? F, grid: [Math.ceil(n / cols), cols], from: o.from ?? "end" } }, t);
    const lit = cells.slice(0, on);
    const tOn = o.at ?? t + n * (o.stagger ?? F) * 0.6 + 6 * F; // light the cells on the spoken number
    lit.forEach((c, i) => tl.to(c, { keyframes: [{ scale: 1.15, backgroundColor: o.color ?? "#CF6E56", duration: 5 * F, ease: "power2.out" }, { scale: 1, duration: 6 * F, ease: "power2.inOut" }] }, tOn + i * 2 * F));
    return { box, cells, lit };
  }

  /* ------------------------------------------------------------------ 6. PARTICLES, ORBIT, PARALLAX, FX */
  /** Seeded dots inside rect. Returns [{el, x, y}] positioned at home. o: {seed, rect, size:[min,max], cls}. */
  function particles(parent, n, o = {}) {
    const r = rng(o.seed ?? 7), [x, y, w, h] = o.rect ?? [0, 0, W, H], [a, b] = o.size ?? [6, 16];
    return Array.from({ length: n }, () => {
      const p = { x: x + r() * w, y: y + r() * h, s: a + r() * (b - a), r: r() };
      p.el = el(parent, `<div class="mg-dot ${o.cls ?? ""}"></div>`);
      gsap.set(p.el, { left: p.x - p.s / 2, top: p.y - p.s / 2, width: p.s, height: p.s });
      return p;
    });
  }
  /** All particles fly into one point (idea -> one dot). */
  function converge(tl, pts, t, o = {}) {
    const [cx, cy] = o.at ?? [540, 960];
    pts.forEach((p) => tl.fromTo(p.el, { x: 0, y: 0, opacity: 1 }, { x: cx - p.x, y: cy - p.y, opacity: o.keep ? 1 : 0.9, duration: (o.dur ?? 0.9) * (0.7 + 0.3 * p.r), ease: "power3.in", immediateRender: false }, t + p.r * (o.spread ?? 0.25)));
    return tl;
  }
  /** Particles burst out of a point to their home positions (explosion / spread). */
  function burst(tl, pts, t, o = {}) {
    const [cx, cy] = o.at ?? [540, 960];
    pts.forEach((p) => tl.fromTo(p.el, { x: cx - p.x, y: cy - p.y, opacity: 0, scale: 0.4 }, { x: 0, y: 0, opacity: 1, scale: 1, duration: (o.dur ?? 0.8) * (0.7 + 0.3 * p.r), ease: "expo.out" }, t + p.r * (o.spread ?? 0.08)));
    return tl;
  }
  /** Finite orbit of items around a centre (logos/tools). Depth via scale + zIndex. o: {cx, cy, rx=360, ry=120, turns=0.5, dur=3, start=0}. */
  function orbit(tl, items, t, o = {}) {
    const list = $$(items), n = list.length, pr = { a: o.start ?? 0 };
    const put = (a) => list.forEach((e, i) => {
      const ang = a + (i * 2 * Math.PI) / n, z = Math.sin(ang);
      gsap.set(e, { x: (o.cx ?? 540) + Math.cos(ang) * (o.rx ?? 360), y: (o.cy ?? 960) + z * (o.ry ?? 120), scale: 0.72 + 0.28 * (z + 1) / 2, zIndex: Math.round(100 + z * 50), xPercent: -50, yPercent: -50 });
    });
    put(pr.a);
    return tl.fromTo(pr, { a: o.start ?? 0 }, { a: (o.start ?? 0) - (o.turns ?? 0.5) * 2 * Math.PI, duration: o.dur ?? 3, ease: o.ease ?? "power1.inOut", immediateRender: false, onUpdate: () => put(pr.a) }, t);
  }
  /** 2.5D parallax drift: layers [{el, depth}] move dx/dy * depth over dur (camera truck). */
  function parallax(tl, layers, t, dur, o = {}) {
    layers.forEach((L) => tl.fromTo($(L.el), { x: 0, y: 0, scale: 1 }, { x: (o.dx ?? -60) * L.depth, y: (o.dy ?? 0) * L.depth, scale: 1 + (o.zoom ?? 0.04) * L.depth, duration: dur, ease: o.ease ?? "sine.inOut" }, t));
    return tl;
  }
  /** 3D card rise (parent needs class mg-3d for perspective): rotateX 60 -> tilt rest + float. */
  function tiltIn(tl, target, t, o = {}) {
    const e = $(target);
    tl.fromTo(e, { opacity: 0, y: o.y ?? 220, rotationX: 60, rotationY: o.ry ?? -18, rotationZ: o.rz ?? 0 },
      { opacity: 1, y: 0, rotationX: o.rx ?? 12, rotationY: (o.ry ?? -18) * 0.6, duration: o.dur ?? 18 * F, ease: "expo.out" }, t);
    if (o.float) tl.to(e, { y: -12, rotationY: (o.ry ?? -18) * 0.4, duration: o.float, ease: "sine.inOut" }, t + (o.dur ?? 18 * F));
    return tl;
  }
  /** Stacked shadow string for fake extrusion (3D type / 3D tiles): use as textShadow or boxShadow. */
  function extrude(depth = 14, color = "#7a3a2c", dx = 1, dy = 1) {
    return Array.from({ length: depth }, (_, i) => `${dx * (i + 1)}px ${dy * (i + 1)}px 0 ${color}`).join(",") + `, ${dx * depth + 6}px ${dy * depth + 14}px 28px rgba(0,0,0,.35)`;
  }
  /** Seeded impact shake (n frames). */
  function shake(tl, target, t, o = {}) {
    const e = $(target), r = rng(o.seed ?? 3), n = o.frames ?? 6, amp = o.amp ?? 10;
    for (let i = 0; i < n; i++) { const k = 1 - i / n; tl.set(e, { x: (r() * 2 - 1) * amp * k, y: (r() * 2 - 1) * amp * k, rotation: (r() * 2 - 1) * 1.2 * k }, t + i * F); }
    return tl.set(e, { x: 0, y: 0, rotation: 0 }, t + n * F);
  }
  /** Seeded slice glitch (horizontal band clip + offset + RGB hue) for n frames, then clean. */
  function glitch(tl, target, t, o = {}) {
    const e = $(target), r = rng(o.seed ?? 11), n = o.frames ?? 6;
    for (let i = 0; i < n; i++) {
      const a = Math.floor(r() * 70), b = Math.floor(r() * (95 - a));
      tl.set(e, { x: (r() * 2 - 1) * (o.amp ?? 40), clipPath: r() < 0.5 ? `inset(${a}% 0% ${100 - a - b - 5}% 0%)` : "inset(0% 0% 0% 0%)", filter: `hue-rotate(${Math.floor(r() * 90)}deg) saturate(1.6)` }, t + i * F);
    }
    return tl.set(e, { x: 0, clipPath: "inset(0% 0% 0% 0%)", filter: "none" }, t + n * F);
  }
  /** Shockwave ring at a point (impact, click, reveal). */
  function shockwave(tl, parent, t, o = {}) {
    const [x, y] = o.at ?? [540, 960], s = o.size ?? 600;
    const r = el(parent, `<div class="mg-shock"></div>`);
    gsap.set(r, { left: x - s / 2, top: y - s / 2, width: s, height: s });
    tl.fromTo(r, { scale: 0.05, opacity: 1 }, { scale: 1, opacity: 0, duration: o.dur ?? 16 * F, ease: "expo.out" }, t);
    return r;
  }

  /* ------------------------------------------------------------------ 7. CURSOR */
  function cursor(parent) {
    return el(parent, `<div class="mg-cursor"><svg viewBox="0 0 40 48"><path d="M4 2 L4 40 L14 31 L21 46 L28 43 L21 28 L34 28 Z"/></svg></div>`);
  }
  /** Curved move (x and y on different eases) then click squash + ripple. Returns end time. */
  function click(tl, cur, t, from, to, o = {}) {
    const c = $(cur), d = o.dur ?? 0.6;
    tl.set(c, { opacity: 1 }, t);
    tl.fromTo(c, { x: from[0], y: from[1] }, { x: to[0], duration: d, ease: "power2.inOut", immediateRender: false }, t);
    tl.fromTo(c, { y: from[1] }, { y: to[1], duration: d, ease: "power3.inOut", immediateRender: false }, t);
    const tc = t + d + 2 * F;
    tl.to(c, { scale: 0.82, duration: 3 * F, ease: "power2.in" }, tc).to(c, { scale: 1, duration: 6 * F, ease: "back.out(2)" }, tc + 3 * F);
    if (o.ripple !== false) shockwave(tl, c.parentNode, tc + 2 * F, { at: to, size: o.rippleSize ?? 120, dur: 12 * F });
    if (o.press) tl.to($(o.press), { scale: 0.92, duration: 3 * F, ease: "power2.in" }, tc).to($(o.press), { scale: 1, duration: 6 * F, ease: "back.out(2)" }, tc + 3 * F);
    return tc + 9 * F;
  }

  /* ------------------------------------------------------------------ 8. UI MOCKS (rebuilt, never screenshots)
   * Builders return element handles; animate them with uiIn / type / typeLines / chatPlay / scroll. */
  function win(parent, kind, o) {
    const w = el(parent, `<div class="mg-win mg-${kind}"><div class="mg-win-bar"><i></i><i></i><i></i><span class="mg-win-title"></span></div><div class="mg-win-body"></div></div>`);
    place(w, o.rect ?? [90, 620, 900, 700]);
    w.querySelector(".mg-win-title").textContent = o.title ?? o.url ?? "";
    if (kind === "browser") w.querySelector(".mg-win-title").classList.add("mg-url");
    return { box: w, body: w.querySelector(".mg-win-body") };
  }
  const ui = {
    browser: (parent, o = {}) => win(parent, "browser", o),
    terminal: (parent, o = {}) => win(parent, "term", { title: "terminal", ...o }),
    /** Code editor. o.lines = HTML strings with token spans (.tk-k keyword .tk-s string .tk-f function .tk-c comment .tk-n number). */
    editor(parent, o = {}) {
      const w = win(parent, "editor", { title: o.file ?? "index.html", ...o });
      const lines = (o.lines ?? []).map((h, i) => { const l = el(w.body, `<div class="mg-code-line"><b>${i + 1}</b><span></span></div>`); l.lastElementChild.innerHTML = h; return l.lastElementChild; });
      return { ...w, lines };
    },
    /** Terminal lines: [{text, cls}] -> spans for typeLines. */
    lines(body, rows) { return rows.map((r) => { const l = el(body, `<div class="mg-term-line ${r.cls ?? ""}"></div>`); l.textContent = r.text; return l; }); },
    /** Phone frame; put content (or the speaker via frameTo 'device-phone') into .screen. */
    phone(parent, o = {}) {
      const p = el(parent, `<div class="mg-phone"><div class="mg-screen"><div class="mg-screen-in"></div></div><div class="mg-notch"></div></div>`);
      place(p, o.rect ?? [300, 458, 480, 1014]);
      return { box: p, screen: p.querySelector(".mg-screen"), inner: p.querySelector(".mg-screen-in") };
    },
    /** Prompt bar (AI input): field + caret + send button. RTL by default. */
    prompt(parent, o = {}) {
      const b = el(parent, `<div class="mg-prompt" dir="${o.dir ?? "rtl"}"><span class="mg-prompt-field"></span><span class="mg-caret"></span><span class="mg-send"><svg viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7"/></svg></span></div>`);
      place(b, o.rect ?? [90, 1180, 900, 140]);
      b.querySelector(".mg-prompt-field").textContent = "";
      if (o.placeholder) b.querySelector(".mg-prompt-field").dataset.ph = o.placeholder;
      return { box: b, field: b.querySelector(".mg-prompt-field"), caret: b.querySelector(".mg-caret"), send: b.querySelector(".mg-send") };
    },
    /** Chat thread. msgs [{who:'me'|'ai', text|html}]. RTL UI: my bubbles sit LEFT, AI replies RIGHT (mirrored app). */
    chat(parent, o = {}) {
      const box = el(parent, `<div class="mg-chat" dir="${o.dir ?? "rtl"}"><div class="mg-chat-in"></div></div>`);
      place(box, o.rect ?? [90, 520, 900, 900]);
      const inner = box.firstElementChild;
      const items = (o.msgs ?? []).map((m) => {
        const b = el(inner, `<div class="mg-msg ${m.who === "me" ? "is-me" : "is-ai"}"></div>`);
        if (m.html) b.innerHTML = m.html; else b.textContent = m.text ?? "";
        return b;
      });
      return { box, inner, items };
    },
    notif(parent, o = {}) {
      const n = el(parent, `<div class="mg-notif" dir="${o.dir ?? "rtl"}"><div class="mg-notif-ic"></div><div><b></b><span></span></div></div>`);
      place(n, o.rect ?? [110, 330, 860, 150]);
      n.querySelector("b").textContent = o.title ?? ""; n.querySelector("span").textContent = o.body ?? "";
      if (o.icon) n.querySelector(".mg-notif-ic").innerHTML = o.icon;
      return n;
    },
  };
  /** Entrance for any UI block. kind: 'rise' | 'scale' | 'tilt' | 'drop'. */
  function uiIn(tl, target, t, kind = "rise", o = {}) {
    const e = $(target), d = o.dur ?? 14 * F;
    const from = { rise: { y: 140, opacity: 0 }, scale: { scale: 0.86, opacity: 0, filter: "blur(10px)" }, drop: { y: -160, opacity: 0 },
      tilt: { y: 200, opacity: 0, rotationX: 50, transformPerspective: 1400 } }[kind];
    const to = { y: 0, scale: 1, opacity: 1, rotationX: 0, filter: "blur(0px)", duration: d, ease: o.ease ?? "expo.out" };
    if (kind !== "scale") delete to.filter;
    return tl.fromTo(e, from, to, t);
  }
  /** Chat play: each bubble pops at times[i]; AI bubbles get a typing indicator `typing` s before; thread scrolls when full. */
  function chatPlay(tl, chat, times, o = {}) {
    const boxH = chat.box.clientHeight, gap = 18;
    let used = 0;
    chat.items.forEach((b, i) => {
      const t = times[i], ai = b.classList.contains("is-ai");
      if (ai && o.typing !== false) {
        const dots = el(chat.inner, `<div class="mg-msg is-ai mg-typing"><i></i><i></i><i></i></div>`);
        chat.inner.insertBefore(dots, b);
        gsap.set(dots, { position: "absolute", right: 0, top: used });
        const tt = t - (o.typing ?? 0.6);
        tl.fromTo(dots, { opacity: 0, scale: 0.7 }, { opacity: 1, scale: 1, duration: 6 * F, ease: "back.out(2)" }, tt)
          .fromTo(dots.children, { y: 0 }, { y: -8, duration: 0.15, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor((t - tt) / 0.3) * 2 - 1), stagger: 0.08 }, tt)
          .set(dots, { opacity: 0 }, t);
      }
      used += b.offsetHeight + gap;
      tl.fromTo(b, { opacity: 0, scale: 0.7, y: 24, transformOrigin: b.classList.contains("is-me") ? "0% 100%" : "100% 100%" },
        { opacity: 1, scale: 1, y: 0, duration: 9 * F, ease: "back.out(1.6)" }, t);
      if (used > boxH) tl.to(chat.inner, { y: boxH - used, duration: 10 * F, ease: "power3.inOut" }, t);
    });
    return tl;
  }
  /** Scroll content inside a phone/browser (y offset px). */
  const scroll = (tl, inner, t, dy, o = {}) => tl.to($(inner), { y: -dy, duration: o.dur ?? 1, ease: o.ease ?? "power3.inOut" }, t);

  /* ------------------------------------------------------------------ 9. GENERIC IN/OUT */
  /** Clean exit (blur-fade-up), ~70 % of the entrance length. */
  const out = (tl, targets, t, o = {}) =>
    tl.to($$(targets), { opacity: 0, y: o.y ?? -20, filter: "blur(8px)", duration: o.dur ?? 7 * F, ease: "power2.in", stagger: o.stagger ?? 0 }, t);
  /** Stage builder: full-frame MG world (dark/light/accent bg, optional 90 px grid + warm glow behind the hero). */
  function stage(parent, o = {}) {
    const s = el(parent, `<div class="mg-stage ${o.grid === false ? "" : "mg-grid"} ${o.glow ? "mg-glow" : ""}"></div>`);
    if (o.bg) s.style.backgroundColor = o.bg;
    if (o.id) s.id = o.id;
    return s;
  }

  window.MG = {
    F, W, H, el, rng, place,
    LAYOUTS, FACE, faceFromBox, layout, frameTo, ring,
    takeover, giveBack, flipColor, gridDrift, stage,
    draw, erase, travel, morph, swap,
    springWords, type, caret, typeLines, strike, roll,
    count, bars, lineChart, donut, gauge, waffle,
    particles, converge, burst, orbit, parallax, tiltIn, extrude, shake, glitch, shockwave,
    cursor, click, ui, uiIn, chatPlay, scroll, out,
  };
})();
