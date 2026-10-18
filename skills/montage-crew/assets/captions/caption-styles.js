/* caption-styles.js — 28 caption styles + 14 colour schemes for Arabic short videos (HyperFrames + GSAP 3).
 * Catalogue / how to pick: references/captions-library.md. Visual gallery: assets/captions/gallery/gallery.jpg
 *
 *   CS.apply(tl, captions, words, "CAP-08", "SC-04", { root: "#captions", top: 1170 })
 *   (alias: window.applyCaptionStyle(tl, captions, words, styleId, scheme, opts))
 *
 *   words    = words_cut.json "words": [{ w|word|text, s, e }]   (seconds, final timeline)
 *   captions = [{ i: [wordIdx, ...], key?: wordIdx, emoji?: "💻", tok?: ["display", ...], t0?, t1? }]
 *              t0 defaults to first onset − 1 f; t1 to the next caption's t0 (or last end + 0.35 s after a > 0.6 s pause).
 *   scheme   = "SC-xx" | scheme object {ink, acc, acc2, stk, on} | null (style default)
 *
 * Rules kept: Arabic is split by WORD only (never letters → joining intact); reveals run right→left; seek-safe
 * (paused timeline, no Math.random, no repeat:-1, hidden start states come from CSS, not from the timeline);
 * animates opacity / transform / filter / colour / text-shadow / clip-path only.
 * Needs caption-styles.css (+ fonts/). CAP-26 (kashida) needs rtl-kit.js (window.RK) loaded first.
 */
(function () {
  const F = 1 / 30;

  // ---------- colour schemes ----------
  const SCHEMES = {
    "SC-01": { name: "Ivory Rose",      ink: "#F2F0E8", acc: "#FF4D8D", acc2: "#B45CFF", stk: "#120A10", on: "#FFFFFF" },
    "SC-02": { name: "Hormozi Gold",    ink: "#FFFFFF", acc: "#FFD400", acc2: "#FF8A00", stk: "#000000", on: "#111111" },
    "SC-03": { name: "Beast Lime",      ink: "#FFFFFF", acc: "#44FF4F", acc2: "#FF3B3B", stk: "#000000", on: "#0A0A0A" },
    "SC-04": { name: "Neon Blue",       ink: "#F4F8FF", acc: "#3A86FF", acc2: "#7FD1FF", stk: "#050B18", on: "#FFFFFF" },
    "SC-05": { name: "Cyber Magenta",   ink: "#FFFFFF", acc: "#FF2FA8", acc2: "#7B5CFF", stk: "#12001A", on: "#FFFFFF" },
    "SC-06": { name: "Teal Eco",        ink: "#F2FAFF", acc: "#3FD7FF", acc2: "#FF7A59", stk: "#031A24", on: "#04202B" },
    "SC-07": { name: "Espresso Copper", ink: "#F9E2CA", acc: "#E09A5C", acc2: "#C8794A", stk: "#1D1011", on: "#1D1011" },
    "SC-08": { name: "Navy Cream",      ink: "#F2F2F2", acc: "#D9BFA8", acc2: "#9DB8D6", stk: "#00213C", on: "#00213C" },
    "SC-09": { name: "Mint Calm",       ink: "#FFFFFF", acc: "#6BCB77", acc2: "#93C5FD", stk: "#0B1F12", on: "#0B1F12" },
    "SC-10": { name: "Sunset",          ink: "#FFF6EC", acc: "#FF6B3D", acc2: "#FFC14D", stk: "#2A0E05", on: "#FFFFFF" },
    "SC-11": { name: "Royal Purple",    ink: "#F5F0FF", acc: "#B388FF", acc2: "#FFD166", stk: "#160A2E", on: "#160A2E" },
    "SC-12": { name: "Mono Editorial",  ink: "#FFFFFF", acc: "#FFE8A3", acc2: "#BFC5CC", stk: "#000000", on: "#111111" },
    "SC-13": { name: "Baghdad Gold",    ink: "#FFFDF5", acc: "#E6C36A", acc2: "#2FBF71", stk: "#0E1A12", on: "#1A1405" },
    "SC-14": { name: "Crimson",         ink: "#FFFFFF", acc: "#FF3B47", acc2: "#FFB4B9", stk: "#1A0003", on: "#FFFFFF" },
  };

  // ---------- styles (data) ----------
  // enter: cut|soft|fade|pop|slam|drop|wipe|tilt   words: all|cut|blur|pop|drop|type|single   hl: none|active|progress|karaoke
  // deco: pill|underline|marker|glow|glitch|focus|scale|outline|grad|kashida|caret|line   exit: cut|soft
  const S = (id, name, o) => ({ id, name, enter: "cut", words: "all", hl: "active", deco: null, exit: "cut", ...o });
  const STYLES = [
    S("CAP-01", "Soft Phrase",        { schemes: ["SC-01", "SC-04", "SC-06"] }),
    S("CAP-02", "Soft Blur-In",       { enter: "soft", exit: "soft", schemes: ["SC-01", "SC-07", "SC-08"] }),
    S("CAP-03", "Karaoke Fill",       { hl: "karaoke", schemes: ["SC-02", "SC-01", "SC-04"] }),
    S("CAP-04", "Hormozi Punch",      { words: "pop", popFrom: 1.3, popEase: "power2.out", schemes: ["SC-02", "SC-03", "SC-14"] }),
    S("CAP-05", "Beast Bounce",       { enter: "tilt", words: "pop", popFrom: 0.3, popEase: "back.out(2.4)", hlColor: "acc2", schemes: ["SC-03", "SC-02", "SC-05"] }),
    S("CAP-06", "Clean Educator",     { enter: "pop", popFrom: 0.96, exit: "soft", schemes: ["SC-09", "SC-11", "SC-12"] }),
    S("CAP-07", "Highlight Pill",     { deco: "pill", schemes: ["SC-05", "SC-02", "SC-09"], box: true }),
    S("CAP-08", "Underline Sweep",    { deco: "underline", schemes: ["SC-04", "SC-10", "SC-01"] }),
    S("CAP-09", "Neon Glow",          { enter: "fade", deco: "glow", hlColor: "acc2", schemes: ["SC-04", "SC-05", "SC-06"] }),
    S("CAP-10", "Outline to Fill",    { hl: "progress", deco: "outline", schemes: ["SC-12", "SC-02", "SC-06"] }),
    S("CAP-11", "Gradient Sweep",     { hl: "none", deco: "grad", schemes: ["SC-05", "SC-10", "SC-11"] }),
    S("CAP-12", "3D Extrude",         { enter: "pop", popFrom: 0.7, popY: 40, popEase: "back.out(1.8)", hl: "none", deco: "scale", schemes: ["SC-10", "SC-02", "SC-04"] }),
    S("CAP-13", "Typewriter",         { words: "type", deco: "caret", hl: "none", schemes: ["SC-06", "SC-12", "SC-04"] }),
    S("CAP-14", "Word Blur-Rise",     { words: "blur", schemes: ["SC-01", "SC-07", "SC-08"] }),
    S("CAP-15", "Stacked Emphasis",   { layout: "stack", words: "blur", hl: "none", schemes: ["SC-07", "SC-01", "SC-11"] }),
    S("CAP-16", "Two-Tone Lead",      { enter: "soft", exit: "soft", hl: "none", schemes: ["SC-08", "SC-13", "SC-09"] }),
    S("CAP-17", "Emoji Inline",       { schemes: ["SC-02", "SC-09", "SC-10"] }),
    S("CAP-18", "Cinematic Lower",    { enter: "fade", deco: "line", hl: "none", exit: "soft", schemes: ["SC-07", "SC-12", "SC-08"] }),
    S("CAP-19", "Ruqaa Script",       { enter: "wipe", hl: "none", exit: "soft", schemes: ["SC-07", "SC-13", "SC-01"] }),
    S("CAP-20", "Editorial Serif",    { enter: "fade", hl: "none", exit: "soft", schemes: ["SC-12", "SC-07", "SC-08"] }),
    S("CAP-21", "Kufi Statement",     { enter: "slam", schemes: ["SC-14", "SC-02", "SC-04"] }),
    S("CAP-22", "Bubble Pop",         { words: "pop", popFrom: 0.4, popEase: "back.out(2.6)", wobble: 4, schemes: ["SC-11", "SC-05", "SC-09"] }),
    S("CAP-23", "Glitch RGB",         { deco: "glitch", schemes: ["SC-04", "SC-05", "SC-06"] }),
    S("CAP-24", "Spotlight Focus",    { deco: "focus", schemes: ["SC-01", "SC-04", "SC-10"] }),
    S("CAP-25", "One Word",           { words: "single", hl: "none", schemes: ["SC-12", "SC-02", "SC-05"] }),
    S("CAP-26", "Kashida Stretch",    { deco: "kashida", schemes: ["SC-07", "SC-08", "SC-01"] }),
    S("CAP-27", "Marker Highlight",   { deco: "marker", hl: "none", schemes: ["SC-02", "SC-09", "SC-10"] }),
    S("CAP-28", "Retro Offset",       { words: "drop", schemes: ["SC-10", "SC-11", "SC-03"] }),
  ];
  const BY_ID = Object.fromEntries(STYLES.map((s) => [s.id, s]));

  // ---------- helpers ----------
  const $ = (x) => (typeof x === "string" ? document.querySelector(x) : x);
  const rgba = (hex, a) => {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  };
  const wordText = (w) => w.w ?? w.word ?? w.text ?? "";
  const isLatin = (t) => /^[\x00-\x7F]+$/.test(t);
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  };

  function resolveScheme(style, scheme) {
    const sc = typeof scheme === "object" && scheme ? scheme : SCHEMES[scheme || style.schemes[0]];
    if (!sc) throw new Error("caption-styles: unknown scheme " + scheme);
    return { ...sc, dim: sc.dim ?? rgba(sc.ink, 0.42) };
  }

  /** Caption windows: t0 = onset − 1 f, t1 = next t0, or last end + 0.35 s when a > 0.6 s pause follows. */
  function timing(captions, words) {
    const t0s = captions.map((c) => c.t0 ?? Math.max(0, words[c.i[0]].s - F));
    return captions.map((c, n) => {
      const last = words[c.i[c.i.length - 1]];
      let t1 = c.t1 ?? (n + 1 < captions.length ? t0s[n + 1] : last.e + 0.35);
      if (c.t1 == null && t1 - last.e > 0.6) t1 = last.e + 0.35;
      const times = c.i.map((wi) => Math.max(t0s[n], words[wi].s - F));
      return { t0: t0s[n], t1, times };
    });
  }

  // ---------- build ----------
  function apply(tl, captions, words, styleId, scheme, opts = {}) {
    const st = BY_ID[styleId];
    if (!st) throw new Error("caption-styles: unknown style " + styleId);
    const sc = resolveScheme(st, scheme);
    const root = $(opts.root || "#captions");
    const layer = el("div", `cs-layer cs-${st.id.toLowerCase()}`);
    layer.style.cssText = `--ink:${sc.ink};--acc:${sc.acc};--acc2:${sc.acc2};--stk:${sc.stk};--on:${sc.on};--dim:${sc.dim};` +
      `--acc-a:${rgba(sc.acc, 0.45)};--acc-m:${rgba(sc.acc, 0.78)};--acc2-a:${rgba(sc.acc2, 0.6)};` + (opts.top != null ? `--cs-top:${opts.top}px;` : "");
    root.appendChild(layer);
    const tm = timing(captions, words);
    const hlCol = sc[st.hlColor || "acc"];

    captions.forEach((c, n) => {
      const { t0, t1, times } = tm[n];
      const cap = el("div", "cs-cap");
      const ws = c.i.map((wi, j) => {
        const txt = c.tok?.[j] ?? wordText(words[wi]);
        const w = el("span", "cs-w" + (wi === c.key ? " cs-key" : "") + (isLatin(txt) ? " lat" : ""), txt);
        if (["pill", "underline"].includes(st.deco) || (st.deco === "marker" && wi === c.key)) w.appendChild(el("i", "cs-" + st.deco));
        return w;
      });
      // layout
      if (st.layout === "stack" && c.key != null) {
        const l1 = el("div", "cs-l1"), l2 = el("div", "cs-l2");
        ws.forEach((w) => { const L = w.classList.contains("cs-key") ? l2 : l1; if (L.childNodes.length) L.append(" "); L.append(w); });
        cap.append(l1, l2);
      } else {
        ws.forEach((w, j) => { if (j) cap.append(" "); cap.append(w); });
      }
      if (c.emoji) {
        const em = el("span", "cs-emo", c.emoji);
        const k = ws[c.i.indexOf(c.key)] || ws[ws.length - 1];
        k.after(" ", em);
        const tk = times[c.i.indexOf(c.key)] ?? times[times.length - 1];
        tl.fromTo(em, { scale: 0, rotation: -18 }, { scale: 1, rotation: 0, duration: 6 * F, ease: "back.out(2.2)" }, tk + 2 * F);
      }
      if (st.deco === "line") cap.prepend(el("i", "cs-line"));
      if (st.deco === "caret") cap.append(el("i", "cs-caret"));
      layer.appendChild(cap);

      // ---- caption enter ----
      const E = st.enter;
      if (E === "cut") tl.set(cap, { opacity: 1 }, t0);
      else if (E === "soft") tl.fromTo(cap, { opacity: 0, y: 8, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 6 * F, ease: "power3.out" }, t0);
      else if (E === "fade") tl.fromTo(cap, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 9 * F, ease: "power2.out" }, t0);
      else if (E === "pop") tl.fromTo(cap, { opacity: 0, scale: st.popFrom ?? 0.85, y: st.popY ?? 0 }, { opacity: 1, scale: 1, y: 0, duration: 6 * F, ease: st.popEase ?? "power3.out" }, t0);
      else if (E === "slam") tl.fromTo(cap, { opacity: 0, scale: 1.22 }, { opacity: 1, scale: 1, duration: 5 * F, ease: "expo.out" }, t0);
      else if (E === "tilt") tl.fromTo(cap, { opacity: 0, rotation: -3 }, { opacity: 1, rotation: -3, duration: F, ease: "none" }, t0);
      else if (E === "wipe") {
        tl.fromTo(cap, { opacity: 0 }, { opacity: 1, duration: 2 * F }, t0);
        tl.fromTo(cap, { clipPath: "inset(-30% -30% -30% 100%)" }, { clipPath: "inset(-30% -30% -30% -30%)", duration: 12 * F, ease: "power2.out" }, t0);
      }
      if (st.deco === "line") {
        tl.fromTo(cap.querySelector(".cs-line"), { scaleX: 0 }, { scaleX: 1, duration: 12 * F, ease: "power3.out" }, t0);
      }
      if (st.deco === "caret") {
        const car = cap.querySelector(".cs-caret");
        for (let t = t0 + 8 * F, on = false; t < t1 - F; t += 8 * F, on = !on) tl.set(car, { opacity: on ? 1 : 0 }, t);
      }

      // ---- words ----
      ws.forEach((w, j) => {
        const t = times[j], tn = j + 1 < ws.length ? times[j + 1] : t1;
        const isKey = c.i[j] === c.key;
        switch (st.words) {
          case "cut": tl.set(w, { opacity: 1 }, t); break;
          case "type": tl.set(w, { display: "inline-block" }, t); break;
          case "blur": tl.fromTo(w, { opacity: 0, y: 14, filter: "blur(12px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: (isKey && st.layout === "stack" ? 7 : 5) * F, ease: "power3.out" }, t); break;
          case "pop": tl.fromTo(w, { opacity: 0, scale: st.popFrom, rotation: st.wobble ? (j % 2 ? st.wobble : -st.wobble) : 0 },
            { opacity: 1, scale: 1, rotation: 0, duration: 5 * F, ease: st.popEase }, t); break;
          case "drop": tl.fromTo(w, { opacity: 0, y: -46 }, { opacity: 1, y: 0, duration: 7 * F, ease: "back.out(1.6)" }, t); break;
          case "single":
            tl.fromTo(w, { opacity: 0, scale: 1.25, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 4 * F, ease: "power3.out" }, t);
            if (j + 1 < ws.length) tl.set(w, { opacity: 0 }, tn);
            break;
        }
        // colour highlight (key words keep their CSS colour unless the style animates them)
        if (st.hl === "active" && !(isKey && st.deco !== "pill")) {
          tl.to(w, { color: hlCol, duration: 2 * F, ease: "power1.out" }, t);
          if (j + 1 < ws.length) tl.to(w, { color: sc.ink, duration: 3 * F, ease: "power1.inOut" }, tn);
        } else if (st.hl === "karaoke") {
          tl.to(w, { color: sc.acc, duration: 2 * F, ease: "power1.out" }, t);
          if (j + 1 < ws.length && !isKey) tl.to(w, { color: sc.ink, duration: 4 * F, ease: "power1.inOut" }, tn);
        } else if (st.hl === "progress") {
          tl.to(w, { color: isKey ? sc.acc : sc.ink, duration: 3 * F, ease: "power1.out" }, t);
        }
        // decorations
        const nxt = j + 1 < ws.length;
        switch (st.deco) {
          case "pill": {
            const p = w.querySelector(".cs-pill");
            tl.fromTo(p, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 3 * F, ease: "back.out(1.8)" }, t);
            tl.to(w, { color: sc.on, duration: F }, t);
            if (nxt) { tl.to(p, { opacity: 0, duration: 2 * F }, tn); tl.to(w, { color: sc.ink, duration: 2 * F }, tn); }
            break;
          }
          case "underline": {
            const u = w.querySelector(".cs-underline");
            tl.fromTo(u, { scaleX: 0 }, { scaleX: 1, duration: 6 * F, ease: "power3.out" }, t);
            if (nxt && !isKey) tl.to(u, { opacity: 0, duration: 3 * F }, tn);
            break;
          }
          case "marker":
            if (isKey) tl.fromTo(w.querySelector(".cs-marker"), { scaleX: 0 }, { scaleX: 1, duration: 8 * F, ease: "power2.out" }, t);
            break;
          case "glow": {
            const off = `0 0 0px ${rgba(sc.acc, 0)}, 0 0 0px ${rgba(sc.acc, 0)}`;
            const on = `0 0 14px ${rgba(sc.acc, 1)}, 0 0 42px ${rgba(sc.acc, 0.85)}`;
            tl.fromTo(w, { textShadow: off }, { textShadow: on, duration: 3 * F, ease: "power2.out" }, t);
            tl.set(w, { opacity: 0.45 }, t + F); tl.set(w, { opacity: 1 }, t + 2 * F); tl.set(w, { opacity: 0.7 }, t + 4 * F); tl.set(w, { opacity: 1 }, t + 5 * F);
            if (nxt && !isKey) tl.to(w, { textShadow: off, duration: 4 * F }, tn);
            break;
          }
          case "glitch": {
            const a = (d) => `${d}px 0 0 ${rgba("#FF2A6D", 0.9)}, ${-d}px 0 0 ${rgba("#2DE2E6", 0.9)}`;
            tl.fromTo(w, { textShadow: a(9) }, { textShadow: a(0), duration: 5 * F, ease: "steps(5)" }, t);
            [7, -5, 3, -1, 0].forEach((x, k) => tl.set(w, { x }, t + k * F));
            break;
          }
          case "focus":
            tl.to(w, { opacity: 1, filter: "blur(0px)", scale: 1.08, duration: 3 * F, ease: "power2.out" }, t);
            if (nxt) tl.to(w, { opacity: 0.4, filter: "blur(3px)", scale: 1, duration: 4 * F, ease: "power2.inOut" }, tn);
            break;
          case "scale":
            tl.fromTo(w, { scale: 1 }, { scale: 1.14, duration: 3 * F, ease: "back.out(2)" }, t);
            tl.to(w, { scale: 1, duration: 4 * F, ease: "power2.out" }, t + 4 * F);
            break;
          case "outline": break; // colour fill handled by hl:"progress"
          case "grad":
            tl.fromTo(w, { backgroundPosition: "0% 0%" }, { backgroundPosition: "100% 0%", duration: 8 * F, ease: "power2.inOut" }, t);
            break;
          case "kashida":
            if (isKey && window.RK) {
              const base = w.textContent, p = { n: 0 };
              // seeking back before t renders progress 0 → n 0 → plain word again (seek-safe)
              tl.fromTo(p, { n: 0 }, { n: 5, duration: 12 * F, ease: "power3.out", onUpdate: () => { w.textContent = RK.kashida(base, Math.round(p.n)); } }, t);
            }
            break;
        }
      });

      // ---- caption exit ----
      if (st.exit === "soft") {
        const tx = Math.max(times[times.length - 1] + 3 * F, t1 - 4 * F);
        tl.to(cap, { opacity: 0, filter: "blur(6px)", duration: Math.max(F, t1 - tx), ease: "power2.in" }, tx);
      } else tl.set(cap, { opacity: 0 }, t1);
    });
    return tl;
  }

  window.CS = { apply, STYLES, SCHEMES, timing, F };
  window.applyCaptionStyle = apply;
})();
