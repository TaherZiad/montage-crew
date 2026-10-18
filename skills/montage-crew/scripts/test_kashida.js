// node scripts/test_kashida.js — checks kashida placement rules in assets/rtl-kit.js
global.window = {}; global.document = {};
require("../assets/rtl-kit.js");
const k = window.RK.kashida;
const cases = { "المشكلة": "المشـكلة", "تسويق": "تسـويق", "بيتك": "بيتـك", "مرات": "مـرات", "دار": "دار",
  "بلا": "بـلا", "لا": "لا", "سلام": "سـلام",   // لا / لام-ألف ligature never splits
  "تحرّك": "تـحرّك" };                           // never between a letter and its shadda
// with an explicit `at`, the tatweel lands AFTER the letter's marks
if (k("كلّش", 1, 1) !== "كلّـش") { console.error("FAIL mark", k("كلّش", 1, 1)); process.exit(1); }
for (const [w, exp] of Object.entries(cases)) if (k(w, 1) !== exp) { console.error("FAIL", w, k(w, 1), "!=", exp); process.exit(1); }
console.log("kashida ok");
