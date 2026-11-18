// Shared calculator engine
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const ok = n => typeof n === "number" && isFinite(n);
const money = (n, d = 2) => ok(n) ? n.toLocaleString("en-US", { style: "currency", currency: "USD", minimumFractionDigits: d, maximumFractionDigits: d }) : "—";
const num = (n, d = 2) => ok(n) ? n.toLocaleString("en-US", { maximumFractionDigits: d }) : "—";
const pct = (n, d = 2) => ok(n) ? num(n, d) + "%" : "—";
const COLORS = ["#6366f1", "#ec4899", "#f59e0b", "#10b981", "#06b6d4", "#8b5cf6"];

function readForm(form) {
  const v = {};
  $$("[name]", form).forEach(el => {
    if (el.type === "radio" && !el.checked) return;
    if (el.type === "checkbox") v[el.name] = el.checked;
    else if (el.type === "number" || el.dataset.num !== undefined) v[el.name] = el.value === "" ? NaN : parseFloat(el.value);
    else v[el.name] = el.value;
  });
  return v;
}

function applyWhen(form, v) {
  $$("[data-when]", form).forEach(el => {
    const [k, val] = el.dataset.when.split("=");
    el.classList.toggle("hidden", String(v[k]) !== val);
  });
}

function donut(parts) {
  const total = parts.reduce((s, p) => s + Math.max(0, p[1]), 0);
  if (!(total > 0)) return "";
  let a = 0;
  const stops = parts.map((p, i) => {
    const c = p[2] || COLORS[i % COLORS.length];
    const from = a; a += Math.max(0, p[1]) / total * 360;
    return `${c} ${from}deg ${a}deg`;
  }).join(",");
  const legend = parts.map((p, i) => `<li><i style="background:${p[2] || COLORS[i % COLORS.length]}"></i>${p[0]}<b>${p[3] || money(p[1])}</b><span>${num(p[1] / total * 100, 1)}%</span></li>`).join("");
  return `<div class="chart"><div class="donut" style="background:conic-gradient(${stops})"></div><ul class="legend">${legend}</ul></div>`;
}

function bars(series, labels) {
  // series: [[name, values[], color]]  stacked
  const n = labels.length; if (!n) return "";
  const totals = labels.map((_, i) => series.reduce((s, x) => s + Math.max(0, x[1][i]), 0));
  const max = Math.max(...totals) || 1;
  const step = Math.ceil(n / 30);
  let cols = "";
  for (let i = 0; i < n; i += step) {
    const segs = series.map((x, k) => `<span style="height:${Math.max(0, x[1][i]) / max * 100}%;background:${x[2] || COLORS[k]}"></span>`).join("");
    cols += `<div class="col" title="${labels[i]}: ${money(totals[i], 0)}">${segs}</div>`;
  }
  const legend = series.map((x, k) => `<span><i style="background:${x[2] || COLORS[k]}"></i>${x[0]}</span>`).join("");
  return `<div class="bars">${cols}</div><div class="barlabels"><span>${labels[0]}</span><span>${labels[n - 1]}</span></div><div class="barlegend">${legend}</div>`;
}

function render(out, r) {
  if (!r || !r.big || r.big[1] === "—" || r.big[1] === undefined) {
    out.innerHTML = `<div class="empty">${(r && r.error) || "Enter your numbers to see the answer"}</div>`;
    return;
  }
  const rows = (r.rows || []).map(x => `<div class="row"><span>${x[0]}</span><b>${x[1]}</b></div>`).join("");
  out.innerHTML = `<div class="biglabel">${r.big[0]}</div><div class="bignum">${r.big[1]}</div>${r.sub ? `<div class="sub">${r.sub}</div>` : ""}
    <div class="rows">${rows}</div>${r.chart || ""}${r.note ? `<p class="note">${r.note}</p>` : ""}
    <button class="copy" type="button">📋 Copy result</button>`;
  $(".copy", out).onclick = e => {
    const t = r.big[0] + ": " + r.big[1].replace(/<[^>]+>/g, "") + "\n" + (r.rows || []).map(x => x[0] + ": " + String(x[1]).replace(/<[^>]+>/g, "")).join("\n");
    navigator.clipboard && navigator.clipboard.writeText(t).then(() => { e.target.textContent = "✅ Copied!"; setTimeout(() => e.target.textContent = "📋 Copy result", 1500); });
  };
  out.classList.remove("pop"); void out.offsetWidth; out.classList.add("pop");
}

function calc(fn, formSel = "#calc", outSel = "#out") {
  const form = $(formSel), out = $(outSel);
  if (!form || !out) return;
  $$("input[type=date][data-today]", form).forEach(el => { if (!el.value) el.value = todayISO(); });
  const run = () => {
    const v = readForm(form);
    applyWhen(form, v);
    let r; try { r = fn(v, form); } catch (e) { console.error(e); r = null; }
    render(out, r);
  };
  form.addEventListener("input", run);
  form.addEventListener("change", run);
  form.addEventListener("submit", e => { e.preventDefault(); run(); });
  // quick-pick chips: <button data-set="name=value">
  $$("[data-set]", form).forEach(b => b.addEventListener("click", () => {
    const [k, val] = b.dataset.set.split("=");
    const el = form.querySelector(`[name="${k}"]`);
    if (el) { el.value = val; run(); }
    $$(`[data-set^="${k}="]`, form).forEach(x => x.classList.toggle("on", x === b));
  }));
  $$(".reset", form).forEach(b => b.addEventListener("click", () => setTimeout(run)));
  run();
}

// helpers for payments
function payment(P, annualRate, n) {
  const r = annualRate / 1200;
  if (!(n > 0)) return NaN;
  return r === 0 ? P / n : P * r / (1 - Math.pow(1 + r, -n));
}
function yearlyBalances(P, annualRate, n, pmt) {
  const r = annualRate / 1200; let bal = P; const bal_ = [], paidP = [], paidI = []; let cp = 0, ci = 0;
  for (let m = 1; m <= n; m++) {
    const i = bal * r; const p = Math.min(bal, pmt - i); bal -= p; cp += p; ci += i;
    if (m % 12 === 0 || m === n) { bal_.push(Math.max(0, bal)); paidP.push(cp); paidI.push(ci); }
  }
  return { bal: bal_, paidP, paidI };
}
function parseDate(s) { if (!s) return null; const [y, m, d] = s.split("-").map(Number); return new Date(y, m - 1, d); }
function todayISO() { const t = new Date(); return new Date(t.getTime() - t.getTimezoneOffset() * 60000).toISOString().slice(0, 10); }

// ---- 2026 US federal tax (IRS Rev. Proc. 2025-32) ----
const TAX2026 = {
  std: { single: 16100, mfj: 32200, hoh: 24150 },
  brackets: {
    single: [[12400, .10], [50400, .12], [105700, .22], [201775, .24], [256225, .32], [640600, .35], [Infinity, .37]],
    mfj: [[24800, .10], [100800, .12], [211400, .22], [403550, .24], [512450, .32], [768700, .35], [Infinity, .37]],
    hoh: [[17700, .10], [67450, .12], [105700, .22], [201750, .24], [256200, .32], [640600, .35], [Infinity, .37]],
  },
  ssBase: 184500, addlMedicare: { single: 200000, mfj: 250000, hoh: 200000 }
};
function fedTax(taxable, status) {
  let tax = 0, prev = 0, top = 0;
  for (const [cap, r] of TAX2026.brackets[status] || TAX2026.brackets.single) {
    if (taxable > prev) { tax += (Math.min(taxable, cap) - prev) * r; top = r; }
    prev = cap;
  }
  return { tax: Math.max(0, tax), top };
}
