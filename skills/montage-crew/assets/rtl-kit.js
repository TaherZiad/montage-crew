/* rtl-kit.js — Arabic motion-graphics helpers for HyperFrames (GSAP, seek-safe).
 * Every helper ADDS tweens to a paused timeline `tl` at absolute time `t` (seconds).
 * Never split Arabic into letter spans (breaks joining): use wipeRTL / wordsIn / kashida*.
 * Letter-level helpers (baselinePop, trackCollapse) are for Latin only.
 */
(function () {
  const F = 1 / 30; // one frame @30fps
  // Arabic letters that do NOT connect to the following letter (right-joining / non-joining)
  const NO_LEFT_JOIN = new Set("اأإآٱدذرزوؤةءـ".split(""));
  const isArabicLetter = (c) => /[ؠ-يٱ-ۓ]/.test(c);
  const isMark = (c) => /[ً-ٰٟ]/.test(c); // tashkeel: the tatweel goes AFTER the marks, never between letter and mark

  /** Insert n tatweels (ـ) at a valid joining point. at = index of the letter to extend after (optional). */
  function kashida(word, n, at) {
    if (!n) return word;
    const chars = [...word];
    const valid = [];
    const after = {}; // letter index -> insert position (after its marks)
    for (let i = 0; i < chars.length - 1; i++) {
      if (!isArabicLetter(chars[i]) || NO_LEFT_JOIN.has(chars[i])) continue;
      let j = i + 1;
      while (j < chars.length && isMark(chars[j])) j++;
      if (j < chars.length && isArabicLetter(chars[j]) && !(chars[i] === "ل" && "اأإآ".includes(chars[j]))) { // لا never splits
        valid.push(i); after[i] = j;
      }
    }
    if (!valid.length) return word;
    // Khatt rules: never after the ل of a leading "ال"; prefer after medial س ص ش ض,
    // else before a final ة ه د ا ل ك (and friends), else the middle joining point.
    const pool = word.startsWith("ال") && valid.length > 1 ? valid.filter((i) => i > 1) : valid;
    const last = chars.length - 1;
    const pref = pool.find((i) => i > 0 && "سصشض".includes(chars[i]))
      ?? (pool.includes(last - 1) && "ةهدالكرنق".includes(chars[last]) ? last - 1 : undefined)
      ?? pool[Math.floor((pool.length - 1) / 2)];
    const idx = at != null && valid.includes(at) ? at : pref;
    chars.splice(after[idx], 0, "ـ".repeat(n));
    return chars.join("");
  }

  const el$ = (x) => (typeof x === "string" ? document.querySelector(x) : x);
  const span = (cls, text, style) => {
    const s = document.createElement("span");
    s.className = cls;
    s.style.cssText = style;
    s.textContent = text;
    return s;
  };

  /** Right-to-left reveal (clip wipe) + optional rise/blur/scale. Keeps Arabic shaping intact. */
  function wipeRTL(tl, target, t, o = {}) {
    const el = el$(target);
    const d = o.dur ?? 8 * F;
    tl.fromTo(el, { clipPath: "inset(-30% -30% -30% 100%)" },
      { clipPath: "inset(-30% -30% -30% -30%)", duration: d, ease: o.ease ?? "power3.out" }, t);
    tl.fromTo(el, { opacity: 0, y: o.y ?? 12, scale: o.scale ?? 1, filter: `blur(${o.blur ?? 8}px)` },
      { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: d, ease: o.ease ?? "power3.out" }, t);
    return tl;
  }

  /** Grow the kashida of el (text in data-base) from 0 to n tatweels. */
  function kashidaGrow(tl, target, t, o = {}) {
    const el = el$(target);
    const base = el.dataset.base || el.textContent;
    el.dataset.base = base;
    const p = { n: o.from ?? 0 };
    el.textContent = kashida(base, p.n, o.at);
    tl.to(p, {
      n: o.n ?? 6, duration: o.dur ?? 12 * F, ease: o.ease ?? "power3.out",
      onUpdate: () => { el.textContent = kashida(base, Math.round(p.n), o.at); },
    }, t);
    return tl;
  }

  /** T-KASHIDA: wipe in, then bar grows (the signature move). */
  function kashidaIn(tl, target, t, o = {}) {
    wipeRTL(tl, target, t, { dur: 6 * F, ...o });
    return kashidaGrow(tl, target, t + 4 * F, { n: o.n ?? 6, dur: 12 * F, at: o.at });
  }

  /** Split into word spans (RTL-safe) and reveal each word. times[] = absolute word times from words.json. */
  function wordsIn(tl, target, t, o = {}) {
    const el = el$(target);
    if (!el.dataset.split) {
      const words = el.textContent.trim().split(/\s+/);
      el.textContent = "";
      words.forEach((w, i) => {
        if (i) el.append(" ");
        el.append(span("rk-w", w, "display:inline-block"));
      });
      el.dataset.split = "1";
    }
    const spans = [...el.querySelectorAll(".rk-w")];
    spans.forEach((s, i) => {
      const at = o.times?.[i] ?? t + i * (o.stagger ?? 4 * F);
      tl.fromTo(s, { opacity: 0, y: o.y ?? 12, scale: o.scale ?? 1, filter: `blur(${o.blur ?? 12}px)` },
        { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: o.dur ?? 5 * F, ease: "power3.out" }, at);
    });
    return tl;
  }

  /** Pop (pills, icons, numerals). */
  function popIn(tl, target, t, o = {}) {
    return tl.fromTo(el$(target), { opacity: 0, scale: o.from ?? 0.6, rotation: o.rot ?? 0 },
      { opacity: 1, scale: 1, rotation: o.toRot ?? 0, duration: o.dur ?? 6 * F, ease: o.ease ?? "back.out(1.6)" }, t);
  }

  /** Blur-pop keyword: scale 1.4→1, blur 12→0. */
  function blurPop(tl, target, t, o = {}) {
    return tl.fromTo(el$(target), { opacity: 0, scale: o.from ?? 1.4, filter: "blur(12px)" },
      { opacity: 1, scale: 1, filter: "blur(0px)", duration: o.dur ?? 7 * F, ease: "power3.out" }, t);
  }

  /** Slam: scale 1.8→1, opacity 0→1 (T-SLAM). Not 0.3: a fromTo from-state shows before t on a paused timeline. */
  function slam(tl, target, t, o = {}) {
    return tl.fromTo(el$(target), { opacity: 0, scale: o.from ?? 1.8 },
      { opacity: 1, scale: 1, duration: o.dur ?? 15 * F, ease: "expo.out" }, t);
  }

  /** Slide/drop in from an offset (x/y in %). */
  function slideIn(tl, target, t, o = {}) {
    return tl.fromTo(el$(target),
      { opacity: 0, xPercent: o.x ?? 0, yPercent: o.y ?? 60, rotation: o.rot ?? 0, scale: o.scale ?? 1, filter: `blur(${o.blur ?? 0}px)` },
      { opacity: 1, xPercent: 0, yPercent: 0, rotation: o.toRot ?? 0, scale: 1, filter: "blur(0px)", duration: o.dur ?? 8 * F, ease: o.ease ?? "expo.out" }, t);
  }

  /** Blur-fade out (in-shot exits). */
  function blurOut(tl, target, t, o = {}) {
    return tl.to(el$(target), { opacity: 0, filter: `blur(${o.blur ?? 10}px)`, duration: o.dur ?? 4 * F, ease: "power2.in" }, t);
  }

  /** Push older text back when a new card enters (Teal Eco). */
  function pushBack(tl, targets, t) {
    return tl.to(targets, { opacity: 0.4, scale: 1.08, filter: "grayscale(.6)", duration: 10 * F, ease: "power2.out" }, t);
  }

  /** Liquid-tag word swap: old goes up/shrinks, new rises with overshoot. */
  function wordSwap(tl, oldEl, newEl, t) {
    tl.to(el$(oldEl), { yPercent: -60, scale: 0.6, opacity: 0, duration: 8 * F, ease: "power2.in" }, t);
    return tl.fromTo(el$(newEl), { yPercent: 60, scale: 1.3, opacity: 0 },
      { yPercent: 0, scale: 1, opacity: 1, duration: 10 * F, ease: "back.out(1.2)" }, t + 5 * F);
  }

  /** Latin: split letters and pop each from its baseline (L→R). */
  function splitLetters(el) {
    if (!el.dataset.split) {
      const chars = [...el.textContent];
      el.textContent = "";
      chars.forEach((c) => el.append(span("rk-l", c === " " ? " " : c, "display:inline-block;transform-origin:50% 100%")));
      el.dataset.split = "1";
    }
    return [...el.querySelectorAll(".rk-l")];
  }
  function baselinePop(tl, target, t, o = {}) {
    const ls = splitLetters(el$(target));
    return tl.fromTo(ls, { opacity: 0, scale: o.from ?? 0.2 },
      { opacity: 1, scale: 1, duration: o.dur ?? 6 * F, ease: "back.out(1.6)", stagger: o.stagger ?? 3 * F }, t);
  }
  function trackCollapse(tl, target, t, o = {}) {
    const el = el$(target);
    const ls = splitLetters(el);
    tl.fromTo(el, { letterSpacing: o.from ?? "0.6em" }, { letterSpacing: "0em", duration: o.dur ?? 15 * F, ease: "power3.out" }, t);
    return tl.fromTo(ls, { opacity: 0 }, { opacity: 1, duration: 4 * F, stagger: 1.5 * F }, t);
  }

  /** Rolling counter 0→to (integer). */
  function counter(tl, target, t, o = {}) {
    const el = el$(target);
    const p = { v: o.from ?? 0 };
    el.textContent = String(p.v);
    return tl.to(p, { v: o.to, duration: o.dur ?? 19 * F, ease: o.ease ?? "expo.out",
      onUpdate: () => { el.textContent = (o.prefix ?? "") + Math.round(p.v) + (o.suffix ?? ""); } }, t);
  }

  /** Camera punch/zoom on a NON-timed wrapper around the footage (and matte). */
  function punch(tl, cams, t, o = {}) {
    return tl.to(cams, { scale: o.to ?? 1.8, xPercent: o.x ?? 0, yPercent: o.y ?? 0,
      duration: o.dur ?? 0, ease: o.ease ?? (o.to > 1.2 ? "power2.inOut" : "expo.out") }, t);
  }
  /** Hard-cut reframe (instant). */
  function reframe(tl, cams, t, scale, o = {}) {
    return tl.set(cams, { scale, xPercent: o.x ?? 0, yPercent: o.y ?? 0 }, t);
  }
  /** Slow push inside a shot. */
  function drift(tl, cams, t, dur, o = {}) {
    return tl.fromTo(cams, { scale: o.from ?? 1 }, { scale: o.to ?? 1.06, duration: dur, ease: "none" }, t);
  }

  /** Blur-cut across a cut at time t (20/40/20 px). */
  function blurCut(tl, target, t) {
    const el = el$(target);
    tl.set(el, { filter: "blur(20px)" }, t - F);
    tl.set(el, { filter: "blur(40px)" }, t);
    tl.set(el, { filter: "blur(20px)" }, t + F);
    return tl.set(el, { filter: "blur(0px)" }, t + 2 * F);
  }

  /** White silhouette flash of the matte layer for n frames before t. */
  function silhouetteFlash(tl, matte, t, n = 3) {
    tl.set(el$(matte), { filter: "brightness(0) invert(1)" }, t - n * F);
    return tl.set(el$(matte), { filter: "none" }, t);
  }

  /** Full-frame white/colour flash overlay element (opacity 0 by default in CSS). */
  function flash(tl, overlay, t, o = {}) {
    tl.fromTo(el$(overlay), { opacity: 0 }, { opacity: 1, duration: o.up ?? 2 * F, ease: "power1.in" }, t);
    return tl.to(el$(overlay), { opacity: 0, duration: o.down ?? 3 * F, ease: "power1.out" }, t + (o.up ?? 2 * F) + (o.hold ?? 0));
  }

  /** Blurred foreground blob: fly in then drift (deterministic). */
  function blobDrift(tl, target, t, dur, o = {}) {
    const el = el$(target);
    tl.fromTo(el, { opacity: 0, xPercent: o.fromX ?? 30, yPercent: o.fromY ?? 0, rotation: o.rot ?? 0 },
      { opacity: o.opacity ?? 0.85, xPercent: 0, yPercent: 0, duration: 12 * F, ease: "expo.out" }, t);
    return tl.to(el, { xPercent: o.dx ?? -12, rotation: (o.rot ?? 0) + (o.drot ?? 6), duration: dur, ease: "none" }, t + 12 * F);
  }


  /** SOFT reveal (craft/09): fade + blur 8→0 + rise 8 px, no pop. For captions/keywords/labels. */
  function softIn(tl, target, t, o = {}) {
    return tl.fromTo(el$(target), { opacity: 0, y: o.y ?? 8, filter: `blur(${o.blur ?? 8}px)` },
      { opacity: 1, y: 0, filter: "blur(0px)", duration: o.dur ?? 8 * F, ease: o.ease ?? "power3.out" }, t);
  }
  /** SOFT exit: fade + slight blur, 5 f. */
  function softOut(tl, target, t, o = {}) {
    return tl.to(el$(target), { opacity: 0, filter: `blur(${o.blur ?? 6}px)`, duration: o.dur ?? 5 * F, ease: "power2.in" }, t);
  }
  /** Phrase captions: hard swap on each onset (no animation), back-to-back. caps = [{sel, t0, t1}] */
  function captionSwaps(tl, caps) {
    caps.forEach((c) => { tl.set(el$(c.sel), { opacity: 1 }, c.t0); tl.set(el$(c.sel), { opacity: 0 }, c.t1); });
    return tl;
  }
  window.RK = { softIn, softOut, captionSwaps, F, kashida, wipeRTL, kashidaGrow, kashidaIn, wordsIn, popIn, blurPop, slam, slideIn, blurOut,
    pushBack, wordSwap, baselinePop, trackCollapse, counter, punch, reframe, drift, blurCut, silhouetteFlash, flash, blobDrift };
})();
