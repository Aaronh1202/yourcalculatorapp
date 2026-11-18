// Free invoice generator: live preview + print / save as PDF
(() => {
  const form = $("#inv"), rows = $("#items"), prev = $("#preview");
  const esc = s => String(s || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const today = todayISO(), due = new Date(); due.setDate(due.getDate() + 30);
  const dueISO = new Date(due.getTime() - due.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  let saved = {}; try { saved = JSON.parse(localStorage.getItem("invoiceDraft") || "{}"); } catch (e) { }

  function addRow(d = {}) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><span class="inp"><input name="desc" placeholder="Description" value="${esc(d.desc)}"></span></td>
      <td><span class="inp"><input name="qty" type="number" inputmode="decimal" step="any" value="${d.qty ?? 1}"></span></td>
      <td><span class="inp"><input name="rate" type="number" inputmode="decimal" step="any" placeholder="0.00" value="${d.rate ?? ""}"></span></td>
      <td><button type="button" class="x" aria-label="Remove line">✕</button></td>`;
    tr.querySelector(".x").onclick = () => { tr.remove(); render(); };
    rows.appendChild(tr);
  }
  function data() {
    const v = {}; $$("[data-f]", form).forEach(el => v[el.dataset.f] = el.value);
    v.items = $$("tr", rows).map(tr => ({ desc: tr.querySelector("[name=desc]").value, qty: parseFloat(tr.querySelector("[name=qty]").value) || 0, rate: parseFloat(tr.querySelector("[name=rate]").value) || 0 }));
    return v;
  }
  function render() {
    const v = data(), cur = v.cur || "USD";
    const m = n => n.toLocaleString("en-US", { style: "currency", currency: cur });
    const sub = v.items.reduce((s, i) => s + i.qty * i.rate, 0);
    const disc = sub * (parseFloat(v.disc) || 0) / 100, tax = (sub - disc) * (parseFloat(v.tax) || 0) / 100, total = sub - disc + tax;
    const fmtD = s => s ? new Date(s + "T00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "";
    prev.innerHTML = `<div class="iv-top"><div><div class="iv-title">INVOICE</div><div class="iv-num"># ${esc(v.num)}</div></div>
      <div class="iv-from"><b>${esc(v.from) || "Your business name"}</b><div>${esc(v.fromd).replace(/\n/g, "<br>")}</div></div></div>
      <div class="iv-meta"><div><span>Bill to</span><b>${esc(v.to) || "Client name"}</b><div>${esc(v.tod).replace(/\n/g, "<br>")}</div></div>
      <div><span>Invoice date</span><b>${fmtD(v.date)}</b><span style="margin-top:8px">Due date</span><b>${fmtD(v.due)}</b></div>
      <div class="iv-due"><span>Amount due</span><b>${m(total)}</b></div></div>
      <table class="iv-t"><thead><tr><th>Description</th><th>Qty</th><th>Rate</th><th>Amount</th></tr></thead><tbody>
      ${v.items.filter(i => i.desc || i.rate).map(i => `<tr><td>${esc(i.desc)}</td><td>${i.qty}</td><td>${m(i.rate)}</td><td>${m(i.qty * i.rate)}</td></tr>`).join("") || `<tr><td colspan="4" style="color:#999">Add a line item</td></tr>`}
      </tbody></table>
      <div class="iv-sum"><div><span>Subtotal</span><b>${m(sub)}</b></div>${disc ? `<div><span>Discount (${v.disc}%)</span><b>−${m(disc)}</b></div>` : ""}${tax ? `<div><span>Tax (${v.tax}%)</span><b>${m(tax)}</b></div>` : ""}<div class="iv-total"><span>Total</span><b>${m(total)}</b></div></div>
      ${v.notes ? `<div class="iv-notes"><span>Notes / payment terms</span><div>${esc(v.notes).replace(/\n/g, "<br>")}</div></div>` : ""}`;
    try { localStorage.setItem("invoiceDraft", JSON.stringify(v)); } catch (e) { }
  }
  // load draft or defaults
  $$("[data-f]", form).forEach(el => { const k = el.dataset.f; if (saved[k] !== undefined && k !== "date" && k !== "due") el.value = saved[k]; });
  if (!$("[data-f=date]").value) $("[data-f=date]").value = today;
  if (!$("[data-f=due]").value) $("[data-f=due]").value = dueISO;
  (saved.items && saved.items.length ? saved.items : [{ desc: "Website design", qty: 1, rate: 1200 }, { desc: "Hosting (12 months)", qty: 1, rate: 180 }]).forEach(addRow);
  form.addEventListener("input", render);
  $("#add").onclick = () => { addRow(); render(); rows.lastChild.querySelector("input").focus(); };
  $("#print").onclick = () => { render(); window.print(); };
  $("#clear").onclick = () => { try { localStorage.removeItem("invoiceDraft"); } catch (e) { } location.reload(); };
  render();
})();
