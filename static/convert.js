(() => {
  const box = document.getElementById("conv"); if (!box || !window.UNITS) return;
  let cat = box.dataset.cat;
  const A = document.getElementById("cv-a"), B = document.getElementById("cv-b"), UA = document.getElementById("cv-ua"), UB = document.getElementById("cv-ub"), RES = document.getElementById("cv-res"), ALL = document.getElementById("cv-all");
  const U = () => UNITS[cat].units;
  function conv(a, b, v) {
    if (cat === "temperature") {
      const c = a === "c" ? v : a === "f" ? (v - 32) * 5 / 9 : v - 273.15;
      return b === "c" ? c : b === "f" ? c * 9 / 5 + 32 : c + 273.15;
    }
    return v * U()[a][3] / U()[b][3];
  }
  function fmt(x) {
    if (!isFinite(x)) return "";
    if (x === 0) return "0";
    if (Math.abs(x) >= 1e15 || Math.abs(x) < 1e-6) return x.toExponential(4);
    const d = Math.max(0, Math.min(10, 6 - Math.floor(Math.log10(Math.abs(x)))));
    return (+x.toFixed(d)).toLocaleString("en-US", { maximumFractionDigits: d });
  }
  const raw = x => { if (!isFinite(x)) return ""; const d = Math.max(0, Math.min(10, 6 - Math.floor(Math.log10(Math.abs(x) || 1)))); return String(+x.toFixed(d)); };
  function ftin(ft) { let f = Math.floor(ft + 1e-9), i = (ft - f) * 12; if (+i.toFixed(1) >= 12) { f++; i = 0; } return `${f} ft ${+i.toFixed(1)} in`; }
  function fill(sel, val) {
    sel.innerHTML = Object.entries(U()).map(([k, u]) => `<option value="${k}"${k === val ? " selected" : ""}>${u[1].replace(/^\w/, c => c.toUpperCase())} (${u[2]})</option>`).join("");
  }
  function show(from) {
    const a = UA.value, b = UB.value;
    if (from === "b") { const v = parseFloat(B.value); A.value = isNaN(v) ? "" : raw(conv(b, a, v)); }
    else { const v = parseFloat(A.value); B.value = isNaN(v) ? "" : raw(conv(a, b, v)); }
    const v = parseFloat(A.value), r = conv(a, b, v), ua = U()[a], ub = U()[b];
    if (isNaN(v)) { RES.innerHTML = ""; if (ALL) ALL.innerHTML = ""; return; }
    let extra = "";
    if (cat === "length" && b === "ft" && r > 0) extra = `<small>= ${ftin(r)}</small>`;
    else if (cat === "length" && b === "in" && r >= 12) extra = `<small>= ${ftin(r / 12)}</small>`;
    else if (cat === "time" && b === "h" && r > 0 && r % 1) extra = `<small>= ${Math.floor(r)} h ${Math.round((r % 1) * 60)} min</small>`;
    RES.innerHTML = `<b>${fmt(v)} ${ua[2]}</b> = <b class="big">${fmt(r)} ${ub[2]}</b>${extra}`;
    if (ALL) ALL.innerHTML = Object.entries(U()).filter(([k]) => k !== a).map(([k, u]) => `<button type="button" data-u="${k}"><span>${u[1].replace(/^\w/, c => c.toUpperCase())}</span><b>${fmt(conv(a, k, v))} ${u[2]}</b></button>`).join("");
  }
  function setCat(c, a, b) { cat = c; const ks = Object.keys(U()); fill(UA, a || ks[1]); fill(UB, b || ks[Math.min(ks.length - 1, 4)]); show("a"); }
  if (box.dataset.pick) {
    const sel = document.createElement("select"); sel.id = "cv-cat"; sel.setAttribute("aria-label", "Category");
    sel.innerHTML = Object.entries(UNITS).map(([k, c]) => `<option value="${k}"${k === cat ? " selected" : ""}>${c.name}</option>`).join("");
    sel.onchange = () => setCat(sel.value, sel.value === "temperature" ? "c" : null, sel.value === "temperature" ? "f" : null);
    box.prepend(sel);
  }
  fill(UA, box.dataset.from); fill(UB, box.dataset.to);
  A.addEventListener("input", () => show("a")); B.addEventListener("input", () => show("b"));
  UA.addEventListener("change", () => show("a")); UB.addEventListener("change", () => show("a"));
  document.getElementById("cv-swap").onclick = () => { const t = UA.value; UA.value = UB.value; UB.value = t; A.value = B.value || A.value; show("a"); };
  if (ALL) ALL.addEventListener("click", e => { const t = e.target.closest("button"); if (t) { UB.value = t.dataset.u; show("a"); } });
  show("a");
})();
