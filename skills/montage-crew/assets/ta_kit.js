/* ta_kit.js — SOFT Arabic text styles for HyperFrames (GSAP 3, paused timeline, seek-safe).
 * Word / line level only (never letters), reveals run right→left. Every helper ADDS tweens to `tl` at absolute
 * time `t` (seconds) and returns tl. Complements RK (assets/rtl-kit.js) — use
 * RK.wordsIn (blur-rise), RK.wipeRTL (mask wipe), RK.blurOut (exit) directly; this file adds the missing ones.
 * Visual check: verify/ta_kit_check.html (#<seconds> seeks) → verify/ta_kit_filmstrip.png
 */
(function () {
  const F = 1 / 30;
  const $ = (x) => (typeof x === "string" ? document.querySelector(x) : x);

  /** Split on spaces into inline-block word spans (DOM order = reading order = right→left on screen). */
  function words(el) {
    el = $(el);
    if (!el.dataset.taSplit) {
      const ws = el.textContent.trim().split(/\s+/);
      el.textContent = "";
      ws.forEach((w, i) => {
        if (i) el.append(" ");
        const s = document.createElement("span");
        s.className = "ta-w";
        s.style.display = "inline-block";
        s.textContent = w;
        el.append(s);
      });
      el.dataset.taSplit = "1";
    }
    return [...el.querySelectorAll(".ta-w")];
  }

  /** Karaoke without pills: upcoming words dim, active word tinted + 1.06, spoken words white. times[i] = word onsets. */
  function karaoke(tl, el, times, o = {}) {
    const ws = words(el);
    tl.set(ws, { color: o.dim ?? "rgba(255,255,255,.5)" }, 0);
    ws.forEach((w, i) => {
      tl.to(w, { color: o.hot ?? "#FFD27A", scale: o.scale ?? 1.06, duration: 2 * F, ease: "power1.out" }, times[i]);
      tl.to(w, { color: o.done ?? "#FFFFFF", scale: 1, duration: 6 * F, ease: "power1.inOut" },
        times[i + 1] ?? times[i] + (o.hold ?? 0.5));
    });
    return tl;
  }

  /** Rolling stack (minimal "stylish captions"): each new line blur-rises at the bottom slot, older lines
   *  step up one line, dim and soften; lines older than `keep` blur out. lines = [{text, t}]. */
  function rollingStack(tl, box, lines, o = {}) {
    box = $(box);
    const keep = o.keep ?? 3, d = o.dur ?? 12 * F;
    const step = parseFloat(getComputedStyle(box).fontSize) * (o.lh ?? 1.25);
    const els = lines.map((l) => {
      const e = document.createElement("div");
      e.className = "ta-line";
      e.textContent = l.text;
      e.style.cssText = "position:absolute;left:0;right:0;bottom:0;text-align:center;opacity:0";
      box.append(e);
      return e;
    });
    lines.forEach((l, i) => {
      tl.fromTo(els[i], { opacity: 0, y: step * 0.45, filter: "blur(12px)" },
        { opacity: 1, y: 0, filter: "blur(0px)", duration: d, ease: "power2.out" }, l.t);
      for (let j = 0; j < i; j++) {
        const age = i - j, gone = age >= keep;
        tl.to(els[j], { y: -age * step, opacity: gone ? 0 : 1 - age * 0.3, filter: `blur(${gone ? 10 : age * 1.5}px)`,
          duration: d, ease: "power2.out" }, l.t);
      }
    });
    return tl;
  }

  /** Words rise from behind their own line mask (no box), staggered in reading order (right→left). */
  function maskRise(tl, el, t, o = {}) {
    const ws = words(el);
    ws.forEach((w) => {
      if (w.parentNode.classList.contains("ta-m")) return;
      const m = document.createElement("span");
      m.className = "ta-m"; // padding keeps Arabic ascenders/descenders/dots inside the mask
      m.style.cssText = "display:inline-block;overflow:hidden;padding:.3em .06em .45em;margin:-.3em -.06em -.45em;vertical-align:bottom";
      w.replaceWith(m);
      m.append(w);
    });
    return tl.fromTo(ws, { yPercent: 120 }, { yPercent: 0, duration: o.dur ?? 12 * F, ease: o.ease ?? "power4.out",
      stagger: o.stagger ?? 3 * F }, t);
  }

  /** Sentence build (Apple/SaaS style): words appear one by one and the growing phrase stays centred.
   *  Measures layout → build inside document.fonts.ready and register the timeline at the end of that callback. */
  function centerBuild(tl, el, times, o = {}) {
    el = $(el);
    const ws = words(el), box = el.getBoundingClientRect(), mid = (box.left + box.right) / 2;
    const r = ws.map((w) => w.getBoundingClientRect());
    const shiftFor = (i) => {
      const seen = r.slice(0, i + 1);
      return mid - (Math.min(...seen.map((b) => b.left)) + Math.max(...seen.map((b) => b.right))) / 2;
    };
    tl.set(el, { x: shiftFor(0) }, 0);
    ws.forEach((w, i) => {
      if (i) tl.to(el, { x: shiftFor(i), duration: o.move ?? 10 * F, ease: "power3.out" }, times[i]);
      tl.fromTo(w, { opacity: 0, y: 14, filter: "blur(10px)" },
        { opacity: 1, y: 0, filter: "blur(0px)", duration: o.dur ?? 10 * F, ease: "power3.out" }, times[i]);
    });
    return tl;
  }

  /** Colour fill sweeping through a word right→left (karaoke fill / emphasis). Joins stay intact. */
  function fillSweep(tl, el, t, o = {}) {
    el = $(el);
    const hot = o.hot ?? "#FFD27A", dim = o.dim ?? "rgba(255,255,255,.55)";
    Object.assign(el.style, {
      backgroundImage: `linear-gradient(to left, ${hot} 47%, ${dim} 53%)`, backgroundSize: "200% 100%",
      webkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
    });
    return tl.fromTo(el, { backgroundPosition: "0% 0" }, { backgroundPosition: "100% 0", duration: o.dur ?? 8 * F,
      ease: o.ease ?? "none" }, t);
  }

  /** Specular shine crossing the word right→left once, then back to plain colour. */
  function shimmer(tl, el, t, o = {}) {
    el = $(el);
    const base = o.base ?? "#FFFFFF", hi = o.hi ?? "#FFE3A3";
    Object.assign(el.style, {
      backgroundImage: `linear-gradient(100deg, ${base} 0 42%, ${hi} 50%, ${base} 58% 100%)`, backgroundSize: "250% 100%",
      webkitBackgroundClip: "text", backgroundClip: "text", color: "transparent",
    });
    return tl.fromTo(el, { backgroundPosition: "0% 0" }, { backgroundPosition: "100% 0", duration: o.dur ?? 20 * F,
      ease: o.ease ?? "sine.inOut" }, t);
  }

  /** Soft glow pop: bloom flares for 3 f then settles to a gentle halo (no box). rgb = "r,g,b". */
  function glowPop(tl, el, t, o = {}) {
    el = $(el);
    const c = o.rgb ?? "255,190,90";
    tl.set(el, { textShadow: `0 0 0px rgba(${c},0), 0 0 0px rgba(${c},0)` }, 0);
    tl.to(el, { textShadow: `0 0 14px rgba(${c},0.9), 0 0 44px rgba(${c},0.6)`, duration: 3 * F, ease: "power2.out" }, t);
    return tl.to(el, { textShadow: `0 0 10px rgba(${c},0.45), 0 0 30px rgba(${c},0.25)`, duration: 14 * F,
      ease: "sine.out" }, t + 3 * F);
  }

  /** Hand-drawn underline that draws from the word's RIGHT edge. Animates the SVG attribute (a unitless
   *  CSS stroke-dashoffset is ignored by Chrome; pathLength + vector-effect breaks the dash). */
  function underline(tl, el, t, o = {}) {
    el = $(el);
    el.style.position = "relative";
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg"), p = document.createElementNS(ns, "path");
    svg.setAttribute("viewBox", "0 0 100 20");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.style.cssText = `position:absolute;left:0;width:100%;bottom:${o.bottom ?? "-0.08em"};height:.3em;overflow:visible`;
    p.setAttribute("d", o.d ?? "M100 10 C70 14 30 6 0 10"); // path starts at the right edge
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", o.color ?? "#FFC35A");
    p.setAttribute("stroke-width", o.w ?? 5);
    p.setAttribute("stroke-linecap", "round");
    svg.append(p);
    el.append(svg);
    const L = p.getTotalLength();
    p.setAttribute("stroke-dasharray", L);
    p.setAttribute("stroke-dashoffset", L);
    return tl.to(p, { attr: { "stroke-dashoffset": 0 }, duration: o.dur ?? 12 * F, ease: o.ease ?? "power2.inOut" }, t);
  }

  /** Airy exit: words drift up and blur away (reverse reading order optional via o.from = "end"). */
  function blurOutUp(tl, el, t, o = {}) {
    return tl.to(words(el), { opacity: 0, y: -12, filter: "blur(10px)", duration: o.dur ?? 6 * F, ease: "power2.in",
      stagger: { each: o.stagger ?? 1 * F, from: o.from ?? "start" } }, t);
  }

  window.TA = { F, words, karaoke, rollingStack, maskRise, centerBuild, fillSweep, shimmer, glowPop, underline, blurOutUp };
})();
