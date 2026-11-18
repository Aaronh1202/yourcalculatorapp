// Scientific calculator for the home page
(() => {
  const disp = document.getElementById("sci-display"), hist = document.getElementById("sci-expr"), log = document.getElementById("sci-history");
  const degBtn = document.getElementById("sci-deg");
  let expr = "", deg = true, justEval = false, history = [];
  try { history = JSON.parse(localStorage.getItem("calcHistory") || "[]"); } catch (e) { }

  const pretty = s => s.replace(/\*/g, "×").replace(/\//g, "÷").replace(/-/g, "−").replace(/sqrt\(/g, "√(").replace(/pi/g, "π");
  function show(v) { disp.textContent = v === "" ? "0" : pretty(v); disp.classList.toggle("small", (v || "").length > 14); }

  function fact(n) { if (n < 0 || n !== Math.floor(n) || n > 170) return NaN; let r = 1; for (let i = 2; i <= n; i++) r *= i; return r; }
  function evaluate(s) {
    let e = s.replace(/×/g, "*").replace(/÷/g, "/").replace(/−/g, "-").replace(/\^/g, "**").replace(/π|pi/g, "(PI)").replace(/ℯ/g, "(E)").replace(/(\d)e([+-]?\d)/g, "$1*10**$2");
    e = e.replace(/(\d+(?:\.\d+)?|\))!/g, "fact($1)").replace(/(\d+(?:\.\d+)?)%/g, "($1/100)");
    e = e.replace(/(\d|\))\s*\(/g, "$1*(").replace(/\)(\d)/g, ")*$1").replace(/(\d|\))([a-zA-Z])/g, "$1*$2");
    if (!/^[\d+\-*/().,\sA-Za-z]*$/.test(e)) throw 0;
    const words = e.match(/[A-Za-z]+/g) || [];
    const allowed = ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "sqrt", "PI", "E", "fact", "abs"];
    if (words.some(w => !allowed.includes(w))) throw 0;
    const k = deg ? Math.PI / 180 : 1;
    const f = new Function("sin", "cos", "tan", "asin", "acos", "atan", "ln", "log", "sqrt", "PI", "E", "fact", "abs", "return (" + (e || "0") + ")");
    const fix = x => Math.abs(x) < 1e-12 ? 0 : x;
    return f(x => fix(Math.sin(x * k)), x => fix(Math.cos(x * k)), x => fix(Math.tan(x * k)), x => Math.asin(x) / k, x => Math.acos(x) / k, x => Math.atan(x) / k,
      Math.log, Math.log10, Math.sqrt, Math.PI, Math.E, fact, Math.abs);
  }
  function fmt(x) {
    if (typeof x !== "number" || !isFinite(x)) return "Error";
    if (Math.abs(x) >= 1e15 || (Math.abs(x) < 1e-9 && x !== 0)) return x.toExponential(8).replace(/\.?0+e/, "e");
    return String(parseFloat(x.toPrecision(12)));
  }
  function preview() { try { const v = evaluate(expr); hist.textContent = expr && /[+\-*/^(!%a-z]/.test(expr.slice(1)) ? "= " + fmt(v) : ""; } catch (e) { hist.textContent = ""; } }
  function renderHistory() {
    log.innerHTML = history.map(h => `<li><span>${pretty(h[0])}</span><b>${h[1]}</b></li>`).join("") || "<li class='none'>Your calculations will show up here</li>";
  }
  function press(k) {
    if (k === "AC") { expr = ""; hist.textContent = ""; show(""); return; }
    if (k === "DEL") { expr = expr.replace(/(sin|cos|tan|asin|acos|atan|ln|log|sqrt)\($|.$/, ""); show(expr); preview(); return; }
    if (k === "=") {
      if (!expr) return;
      let r; try { r = fmt(evaluate(expr)); } catch (e) { r = "Error"; }
      hist.textContent = pretty(expr) + " =";
      if (r !== "Error") { history.unshift([expr, r]); history = history.slice(0, 20); try { localStorage.setItem("calcHistory", JSON.stringify(history)); } catch (e) { } renderHistory(); }
      show(r === "Error" ? "Error" : r); disp.classList.remove("pop"); void disp.offsetWidth; disp.classList.add("pop");
      expr = r === "Error" ? "" : r; justEval = true; return;
    }
    if (k === "±") { expr = expr ? "-(" + expr + ")" : "-"; show(expr); preview(); return; }
    if (justEval && /^[\d.(]|^[a-z]|^π|^ℯ/.test(k)) expr = "";
    justEval = false;
    expr += k; show(expr); preview();
  }
  document.querySelectorAll("#sci [data-k]").forEach(b => b.addEventListener("click", () => press(b.dataset.k)));
  degBtn.addEventListener("click", () => { deg = !deg; degBtn.textContent = deg ? "DEG" : "RAD"; preview(); });
  document.getElementById("sci-clearhist").addEventListener("click", () => { history = []; try { localStorage.removeItem("calcHistory"); } catch (e) { } renderHistory(); });
  document.addEventListener("keydown", e => {
    if (e.target.matches("input,textarea,select")) return;
    const map = { Enter: "=", "=": "=", Backspace: "DEL", Escape: "AC", Delete: "AC", "*": "*", "/": "/", "+": "+", "-": "-", "^": "^", "(": "(", ")": ")", ".": ".", "%": "%", "!": "!" };
    let k = map[e.key] || (/^\d$/.test(e.key) ? e.key : null);
    if (!k) return;
    e.preventDefault(); press(k);
    const btn = document.querySelector(`#sci [data-k="${CSS.escape(k)}"]`);
    if (btn) { btn.classList.add("hit"); setTimeout(() => btn.classList.remove("hit"), 120); }
  });
  renderHistory();
})();
