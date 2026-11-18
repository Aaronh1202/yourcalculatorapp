import re, json, os, pathlib, shutil, datetime
import converters as CV
OUT = pathlib.Path("public")
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
for f in ["style.css", "calc.js", "sci.js", "invoice.js", "convert.js"]: shutil.copy("static/" + f, OUT / f)
(OUT / "units.js").write_text(CV.unit_js())
SITE = "YourCalculatorApp"
DOMAIN = "https://yourcalculatorapp.com"
CONTACT = os.environ.get("CONTACT_EMAIL", "hello@example.com")

# ---------- form helpers ----------
def N(name, label, val="", pre="", suf="", full=False, chips=None, step="any", mn=None):
    m = f' min="{mn}"' if mn is not None else ""
    p = f"<i>{pre}</i>" if pre else ""
    s = f'<i class="suf">{suf}</i>' if suf else ""
    ch = ""
    if chips:
        ch = '<div class="chips">' + "".join(f'<button type="button" data-set="{name}={c[0]}"{" class=on" if str(c[0]) == str(val) else ""}>{c[1]}</button>' for c in chips) + "</div>"
    return f'<label class="field{" full" if full else ""}">{label}<span class="inp">{p}<input type="number" inputmode="decimal" name="{name}" value="{val}" step="{step}"{m}>{s}</span>{ch}</label>'

def S(name, label, opts, val=None, full=False):
    o = "".join(f'<option value="{v}"{" selected" if str(v) == str(val) else ""}>{t}</option>' for v, t in opts)
    dn = " data-num" if all(isinstance(v, (int, float)) for v, _ in opts) else ""
    return f'<label class="field{" full" if full else ""}">{label}<span class="inp"><select name="{name}"{dn}>{o}</select></span></label>'

def D(name, label, today=False, val="", full=False):
    t = " data-today" if today else ""
    return f'<label class="field{" full" if full else ""}">{label}<span class="inp"><input type="date" name="{name}" value="{val}"{t}></span></label>'

def T(name, label, val=""):
    return f'<label class="field">{label}<span class="inp"><input type="time" name="{name}" value="{val}"></span></label>'

def SEG(name, label, opts, val, full=True):
    o = "".join(f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == val else ""}><span>{t}</span></label>' for v, t in opts)
    return f'<div class="field{" full" if full else ""}">{label}<div class="seg">{o}</div></div>'

def when(cond, html):
    return f'<div class="field full" data-when="{cond}" style="display:contents">{html}</div>'

def calc_box(fields, js, title="Your numbers", fid="calc", oid="out"):
    return f'<div class="calc"><form class="panel" id="{fid}" autocomplete="off"><h2>{title}</h2><div class="fields">{fields}</div></form><div class="result" id="{oid}"></div></div><script>{js}</script>'

def mini(fid, title, fields, js):
    return f'<div class="mini"><form class="panel" id="{fid}" autocomplete="off"><h2>{title}</h2><div class="fields">{fields}</div></form><div class="result" id="{fid}o"></div></div><script>calc({js},"#{fid}","#{fid}o")</script>'

GRADES = [("4.0", "A / A+"), ("3.7", "A-"), ("3.3", "B+"), ("3.0", "B"), ("2.7", "B-"), ("2.3", "C+"), ("2.0", "C"), ("1.7", "C-"), ("1.3", "D+"), ("1.0", "D"), ("0.7", "D-"), ("0", "F")]

# ---------- calculators ----------
CALCS = []
def add(slug, cat, emoji, name, card, title, desc, tool, content, intro=None, hidden=False):
    CALCS.append(dict(slug=slug, cat=cat, emoji=emoji, name=name, card=card, title=title, desc=desc, tool=tool, content=content, intro=intro, hidden=hidden))

add("mortgage-calculator", "Financial", "🏠", "Mortgage Calculator", "Monthly house payment with taxes & insurance",
    "Mortgage Calculator – Monthly Payment with Taxes & Insurance",
    "Free mortgage calculator. Estimate your monthly house payment with property tax, home insurance and HOA, plus total interest and payoff date.",
    calc_box(
        N("price", "Home price", 350000, "$", full=True) +
        N("down", "Down payment", 20, suf="%", chips=[(3.5, "3.5%"), (5, "5%"), (10, "10%"), (20, "20%")]) +
        N("rate", "Interest rate", 6.5, suf="%") +
        S("years", "Loan term", [(30, "30 years"), (20, "20 years"), (15, "15 years"), (10, "10 years")], 30) +
        N("tax", "Property tax / year", 6000, "$") +
        N("ins", "Home insurance / year", 1800, "$") +
        N("hoa", "HOA / month", 0, "$"),
        """calc(v=>{const L=v.price*(1-(v.down||0)/100),n=v.years*12,pi=payment(L,v.rate||0,n);if(!(L>0)||!ok(pi))return null;
const tax=(v.tax||0)/12,ins=(v.ins||0)/12,hoa=v.hoa||0,m=pi+tax+ins+hoa,y=yearlyBalances(L,v.rate||0,n,pi),d=new Date();d.setFullYear(d.getFullYear()+v.years);
return{big:["Monthly payment",money(m)],sub:money(pi)+" principal &amp; interest",rows:[["Loan amount",money(L,0)],["Down payment",money(v.price-L,0)],["Total interest",money(pi*n-L,0)],["Total of all payments",money(pi*n,0)],["Payoff date",d.toLocaleDateString("en-US",{month:"short",year:"numeric"})]],
chart:donut([["Principal &amp; interest",pi],["Property tax",tax],["Insurance",ins],["HOA",hoa]].filter(p=>p[1]>0))+bars([["Principal paid",y.paidP],["Interest paid",y.paidI]],y.bal.map((_,i)=>"Year "+(i+1)))}})"""),
    """<h2>How this mortgage calculator works</h2><p>Enter the home price, your down payment and interest rate. The calculator works out the monthly principal and interest, then adds property tax, homeowners insurance and HOA dues so you see the full payment you'll actually make each month.</p>
<p class="formula">M = P × r(1+r)ⁿ ÷ ((1+r)ⁿ − 1)</p><p>P is the loan amount, r is the monthly interest rate (annual rate ÷ 12) and n is the number of monthly payments.</p>
<h2>How much down payment do I need?</h2><p>20% down avoids private mortgage insurance (PMI) on most conventional loans. FHA loans allow as little as 3.5% down, and some conventional loans allow 3–5%. A bigger down payment lowers your monthly payment and total interest.</p>
<h2>15-year vs 30-year mortgage</h2><p>A 15-year loan has a higher monthly payment but usually a lower rate and far less total interest. A 30-year loan keeps the monthly payment low. Switch the term above to compare them instantly.</p>""")

add("loan-calculator", "Financial", "💵", "Loan Calculator", "Payment and interest for any loan",
    "Loan Calculator – Monthly Payment & Total Interest",
    "Free loan calculator for personal loans, student loans and more. See your monthly payment, total interest and total cost instantly.",
    calc_box(
        N("amount", "Loan amount", 15000, "$", full=True) +
        N("rate", "Interest rate", 9, suf="%") +
        N("term", "Loan term", 5) +
        S("unit", "Term in", [("years", "Years"), ("months", "Months")], "years"),
        """calc(v=>{const n=v.unit==="years"?v.term*12:v.term,p=payment(v.amount,v.rate||0,n);if(!(v.amount>0)||!ok(p))return null;
return{big:["Monthly payment",money(p)],rows:[["Number of payments",num(n,0)],["Total interest",money(p*n-v.amount)],["Total cost",money(p*n)]],chart:donut([["Principal",v.amount],["Interest",p*n-v.amount]])}})"""),
    """<h2>How to use the loan calculator</h2><p>Type the amount you want to borrow, the yearly interest rate (APR) and how long you'll take to pay it back. You'll instantly see your monthly payment, how much interest you'll pay overall and the total cost of the loan.</p>
<p class="formula">Payment = P × r ÷ (1 − (1+r)⁻ⁿ)</p>
<h2>How to pay less interest</h2><p>A shorter term, a lower rate or a smaller loan all cut the interest you pay. Even paying a little extra each month goes straight to principal and shortens the loan.</p>""")

add("auto-loan-calculator", "Financial", "🚗", "Auto Loan Calculator", "Car payment with tax, trade-in and down",
    "Auto Loan Calculator – Estimate Your Car Payment",
    "Free car loan calculator. Estimate your monthly car payment with sales tax, down payment and trade-in value, plus total interest.",
    calc_box(
        N("price", "Car price", 32000, "$", full=True) +
        N("down", "Down payment", 3000, "$") +
        N("trade", "Trade-in value", 0, "$") +
        N("rate", "Interest rate (APR)", 7, suf="%") +
        N("tax", "Sales tax", 6.25, suf="%") +
        N("months", "Loan term", 60, suf="months", full=True, chips=[(36, "36 mo"), (48, "48 mo"), (60, "60 mo"), (72, "72 mo"), (84, "84 mo")]),
        """calc(v=>{const taxable=Math.max(0,v.price-(v.trade||0)),tx=taxable*(v.tax||0)/100,L=taxable+tx-(v.down||0),p=payment(L,v.rate||0,v.months);if(!(L>0)||!ok(p))return null;
return{big:["Monthly payment",money(p)],rows:[["Amount financed",money(L)],["Sales tax",money(tx)],["Total interest",money(p*v.months-L)],["Total cost of car",money(p*v.months+(v.down||0)+(v.trade||0))]],chart:donut([["Amount financed",L],["Interest",p*v.months-L]])}})"""),
    """<h2>How car payments are calculated</h2><p>Your trade-in is subtracted from the price, sales tax is added, and your down payment is taken off. What's left is the amount financed, which is spread over your loan term at your interest rate.</p>
<h2>What's a good car loan term?</h2><p>60 months is the most common. 72 and 84-month loans lower the payment but cost much more in interest, and you can end up owing more than the car is worth. Try the term buttons above to compare.</p>""")

add("compound-interest-calculator", "Financial", "📈", "Compound Interest Calculator", "Watch savings grow with monthly deposits",
    "Compound Interest Calculator – See How Your Money Grows",
    "Free compound interest calculator with monthly contributions. See your future balance, total deposits and interest earned year by year.",
    calc_box(
        N("p", "Starting amount", 5000, "$") +
        N("c", "Monthly contribution", 200, "$") +
        N("rate", "Annual interest rate", 7, suf="%") +
        N("years", "Years to grow", 20) +
        S("freq", "Compounding", [(12, "Monthly"), (365, "Daily"), (4, "Quarterly"), (1, "Yearly")], 12, full=True),
        """calc(v=>{if(!(v.years>0))return null;const r=Math.pow(1+(v.rate||0)/100/v.freq,v.freq/12)-1;let b=v.p||0,dep=v.p||0;const D=[],I=[],L=[];
for(let m=1;m<=Math.round(v.years*12);m++){b=b*(1+r)+(v.c||0);dep+=(v.c||0);if(m%12===0){D.push(dep);I.push(b-dep);L.push("Year "+m/12)}}
return{big:["Future balance",money(b,0)],sub:"after "+num(v.years)+" years",rows:[["Total deposits",money(dep,0)],["Interest earned",money(b-dep,0)],["Interest share",pct((b-dep)/b*100,1)]],chart:bars([["Deposits",D,"#6366f1"],["Interest",I,"#f59e0b"]],L)}})"""),
    """<h2>What is compound interest?</h2><p>Compound interest means you earn interest on your interest. Each period, the interest is added to your balance, so the next period's interest is a little bigger. Over many years, this snowball effect does most of the work.</p>
<p class="formula">A = P(1 + r/n)ⁿᵗ + monthly contributions</p>
<h2>The rule of 72</h2><p>Divide 72 by your interest rate to estimate how many years it takes to double your money. At 8%, money doubles in about 9 years.</p>""")

add("salary-calculator", "Financial", "💼", "Salary Calculator", "Hourly ↔ yearly pay converter",
    "Salary Calculator – Convert Hourly to Annual Salary",
    "Convert hourly wage to annual salary and back. See your pay per hour, day, week, paycheck, month and year instantly.",
    calc_box(
        N("amt", "Pay amount", 25, "$") +
        S("per", "Per", [("hour", "Hour"), ("day", "Day"), ("week", "Week"), ("biweek", "2 weeks"), ("month", "Month"), ("year", "Year")], "hour") +
        N("hours", "Hours per week", 40) +
        N("weeks", "Weeks worked per year", 52),
        """calc(v=>{const hw=v.hours||40,wk=v.weeks||52,f={hour:hw*wk,day:wk*5,week:wk,biweek:wk/2,month:12,year:1},yr=v.amt*f[v.per];if(!(yr>0))return null;
return{big:["Yearly salary",money(yr,0)],rows:[["Hourly",money(yr/(hw*wk))],["Daily",money(yr/(wk*5))],["Weekly",money(yr/wk)],["Every 2 weeks",money(yr/wk*2)],["Twice a month",money(yr/24)],["Monthly",money(yr/12)]],note:"Before taxes. Daily pay assumes a 5-day work week."}})"""),
    """<h2>How to convert hourly pay to salary</h2><p>Multiply your hourly rate by the hours you work each week, then by 52 weeks. A quick shortcut for full-time work: double your hourly wage and add three zeros. $25/hour is about $50,000 a year.</p>
<p class="formula">Annual salary = hourly rate × hours per week × weeks per year</p>
<h2>What about unpaid time off?</h2><p>If you don't get paid vacation, lower the weeks per year. For example, two unpaid weeks off means 50 weeks.</p>""")

add("tip-calculator", "Financial", "🍽️", "Tip Calculator", "Split the bill and tip fast",
    "Tip Calculator – Calculate Tip and Split the Bill",
    "Free tip calculator. Work out the tip, total and how much each person pays when splitting the bill. Quick 15%, 18%, 20% and 25% buttons.",
    calc_box(
        N("bill", "Bill amount", 60, "$", full=True) +
        N("tip", "Tip", 18, suf="%", full=True, chips=[(10, "10%"), (15, "15%"), (18, "18%"), (20, "20%"), (25, "25%")]) +
        N("people", "Split between", 1, suf="people", mn=1) +
        S("round", "Round per person", [("no", "Don't round"), ("up", "Round up")], "no"),
        """calc(v=>{if(!(v.bill>0))return null;const n=Math.max(1,Math.round(v.people||1)),t=v.bill*(v.tip||0)/100;let per=(v.bill+t)/n;if(v.round==="up")per=Math.ceil(per);
return{big:[n>1?"Each person pays":"Total with tip",money(n>1?per:v.bill+t)],rows:[["Tip amount",money(t)],["Total bill",money(per*n)],...(n>1?[["Tip per person",money(t/n)]]:[])]}})"""),
    """<h2>How much should I tip?</h2><p>In the US, 15–20% is standard at sit-down restaurants, with 20% now the most common for good service. 10–15% is typical for takeout or counter service, and 20–25% for great service.</p>
<h2>Quick mental math</h2><p>For 20%, move the decimal one place left and double it. On a $60 bill, 10% is $6, so 20% is $12.</p>""")

add("sales-tax-calculator", "Financial", "🧾", "Sales Tax Calculator", "Add or remove sales tax",
    "Sales Tax Calculator – Add or Remove Sales Tax",
    "Free sales tax calculator. Add sales tax to a price or find the price before tax from a total. Works with any state or local rate.",
    calc_box(
        SEG("mode", "What do you want to do?", [("add", "Add tax to a price"), ("remove", "Find price before tax")], "add") +
        N("amt", "Amount", 100, "$") +
        N("rate", "Sales tax rate", 8.25, suf="%"),
        """calc(v=>{if(!(v.amt>0))return null;const r=(v.rate||0)/100;if(v.mode==="add")return{big:["Total with tax",money(v.amt*(1+r))],rows:[["Price before tax",money(v.amt)],["Sales tax",money(v.amt*r)]]};
const pre=v.amt/(1+r);return{big:["Price before tax",money(pre)],rows:[["Total paid",money(v.amt)],["Sales tax included",money(v.amt-pre)]]}})"""),
    """<h2>How to calculate sales tax</h2><p>Multiply the price by the tax rate as a decimal. At 8.25%, a $100 item has $8.25 in tax, for a total of $108.25.</p>
<p class="formula">Tax = price × rate ÷ 100 &nbsp;·&nbsp; Price before tax = total ÷ (1 + rate ÷ 100)</p>
<h2>What's my sales tax rate?</h2><p>Rates combine state, county and city taxes, so they differ by location. Check your receipt or your state's revenue website for the exact rate where you shop.</p>""")

add("discount-calculator", "Financial", "🏷️", "Discount Calculator", "Sale price and how much you save",
    "Discount Calculator – Find the Sale Price & Savings",
    "Free discount calculator. Enter the price and percent off to see the sale price and how much you save, including extra discounts and tax.",
    calc_box(
        N("price", "Original price", 80, "$", full=True) +
        N("off", "Discount", 25, suf="% off", full=True, chips=[(10, "10%"), (20, "20%"), (25, "25%"), (30, "30%"), (40, "40%"), (50, "50%")]) +
        N("extra", "Extra discount (optional)", 0, suf="% off") +
        N("tax", "Sales tax (optional)", 0, suf="%"),
        """calc(v=>{if(!(v.price>0))return null;const a=v.price*(1-(v.off||0)/100),b=a*(1-(v.extra||0)/100),t=b*(v.tax||0)/100;
return{big:["Sale price",money(b+t)],sub:"You save "+money(v.price-b)+" ("+pct((1-b/v.price)*100,1)+" total)",rows:[["Original price",money(v.price)],["After first discount",money(a)],...(v.extra?[["After extra discount",money(b)]]:[]),...(v.tax?[["Sales tax",money(t)]]:[])]}})"""),
    """<h2>How to calculate a discount</h2><p>Multiply the price by the percent off, then subtract it. 25% off $80 is $20 off, so you pay $60.</p>
<h2>Do stacked discounts add up?</h2><p>No. "25% off plus an extra 10%" is not 35% off. The extra 10% comes off the already-reduced price, so it's 32.5% off in total. Add an extra discount above to see the real number.</p>""")

PCT_TOOL = (
    mini("p1", "What is X% of Y?", N("a", "Percent", 15, suf="%") + N("b", "of", 200),
         "v=>({big:[num(v.a)+'% of '+num(v.b),num(v.a/100*v.b,4)]})") +
    mini("p2", "X is what percent of Y?", N("a", "Value", 30) + N("b", "is what % of", 120),
         "v=>({big:[num(v.a)+' is',pct(v.a/v.b*100,4)],sub:'of '+num(v.b)})") +
    mini("p3", "Percent change (increase or decrease)", N("a", "From", 50) + N("b", "To", 65),
         "v=>{const c=(v.b-v.a)/Math.abs(v.a)*100;return{big:[c>=0?'Increase':'Decrease',pct(Math.abs(c),4)],rows:[['Difference',num(v.b-v.a,4)]]}}") +
    mini("p4", "X is Y% of what?", N("a", "Value", 45) + N("b", "is this percent", 30, suf="%"),
         "v=>({big:[num(v.a)+' is '+num(v.b)+'% of',num(v.a/(v.b/100),4)]})"))
add("percentage-calculator", "Math", "％", "Percentage Calculator", "Percent of, percent change and more",
    "Percentage Calculator – Percent Of, Change & Difference",
    "Free percentage calculator. Find X% of a number, what percent one number is of another, percent increase or decrease, and more.",
    '<div class="stack" style="margin-top:-14px;position:relative">' + PCT_TOOL + "</div>",
    """<h2>How to calculate a percentage</h2><p>To find a percent of a number, turn the percent into a decimal and multiply: 15% of 200 = 0.15 × 200 = 30.</p>
<p class="formula">Percent change = (new − old) ÷ |old| × 100</p>
<h2>Percent change vs percent difference</h2><p>Percent change compares a new value to an original one (like a price going from $50 to $65 is a 30% increase). Use the third calculator above for price changes, grades, stock moves and more.</p>""")

add("fraction-calculator", "Math", "➗", "Fraction Calculator", "Add, subtract, multiply, divide fractions",
    "Fraction Calculator – Add, Subtract, Multiply & Divide",
    "Free fraction calculator. Add, subtract, multiply and divide fractions and get the simplified answer, mixed number and decimal.",
    calc_box(
        N("a", "First numerator", 1) + N("b", "First denominator", 2) +
        S("op", "Operation", [("+", "+ Add"), ("-", "− Subtract"), ("*", "× Multiply"), ("/", "÷ Divide")], "+", full=True) +
        N("c", "Second numerator", 3) + N("d", "Second denominator", 4),
        """calc(v=>{const g=(x,y)=>{x=Math.abs(x);y=Math.abs(y);while(y){[x,y]=[y,x%y]}return x};let{a,b,c,d}=v;if(![a,b,c,d].every(Number.isInteger)||!b||!d)return{error:"Use whole numbers, and denominators can't be 0"};
let n,m;if(v.op==="+"){n=a*d+c*b;m=b*d}else if(v.op==="-"){n=a*d-c*b;m=b*d}else if(v.op==="*"){n=a*c;m=b*d}else{n=a*d;m=b*c}if(!m)return{error:"Can't divide by zero"};
if(m<0){n=-n;m=-m}const k=g(n,m)||1;n/=k;m/=k;const w=Math.trunc(n/m),r=Math.abs(n%m);
const sym={"+":"+","-":"−","*":"×","/":"÷"}[v.op];
return{big:["Answer",m===1?String(n):n+"/"+m],sub:a+"/"+b+" "+sym+" "+c+"/"+d,rows:[["Mixed number",w&&r?w+" "+r+"/"+m:(m===1?String(n):n+"/"+m)],["Decimal",num(n/m,6)],["Percent",pct(n/m*100,4)]]}})"""),
    """<h2>How to add fractions</h2><p>Give both fractions the same denominator, add the tops, then simplify. 1/2 + 3/4 = 2/4 + 3/4 = 5/4, which is 1 1/4 as a mixed number.</p>
<h2>How to divide fractions</h2><p>Flip the second fraction and multiply: 1/2 ÷ 3/4 = 1/2 × 4/3 = 4/6 = 2/3. The calculator always shows the answer in simplest form.</p>""")

add("average-calculator", "Math", "📊", "Average Calculator", "Mean, median, mode and range",
    "Average Calculator – Mean, Median, Mode & Range",
    "Free average calculator. Paste a list of numbers to get the mean, median, mode, range, sum and standard deviation instantly.",
    calc_box(
        '<label class="field full">Your numbers (separate with commas, spaces or new lines)<span class="inp"><textarea name="list">85, 92, 78, 92, 88, 95, 70</textarea></span></label>',
        """calc(v=>{const a=(v.list.match(/-?\\d*\\.?\\d+/g)||[]).map(Number).filter(ok);if(!a.length)return null;const s=[...a].sort((x,y)=>x-y),n=a.length,sum=a.reduce((x,y)=>x+y,0),mean=sum/n,
med=n%2?s[(n-1)/2]:(s[n/2-1]+s[n/2])/2,cnt={};a.forEach(x=>cnt[x]=(cnt[x]||0)+1);const mx=Math.max(...Object.values(cnt)),modes=mx>1?Object.keys(cnt).filter(k=>cnt[k]===mx).join(", "):"None",
sd=Math.sqrt(a.reduce((x,y)=>x+(y-mean)**2,0)/n);
return{big:["Average (mean)",num(mean,4)],rows:[["Median",num(med,4)],["Mode",modes],["Range",num(s[n-1]-s[0],4)],["Count",n],["Sum",num(sum,4)],["Smallest / largest",num(s[0],4)+" / "+num(s[n-1],4)],["Standard deviation",num(sd,4)]]}})"""),
    """<h2>Mean, median and mode explained</h2><p>The <b>mean</b> is the classic average: add everything and divide by how many numbers there are. The <b>median</b> is the middle number when they're in order. The <b>mode</b> is the number that shows up most often.</p>
<p class="formula">Mean = sum of values ÷ number of values</p>
<h2>Which average should I use?</h2><p>Use the median when a few very high or low numbers would skew the mean, like home prices or incomes. Use the mean for test scores and most everyday averages.</p>""")

UNITS = SEG("u", "Units", [("us", "US (ft, lb)"), ("m", "Metric (cm, kg)")], "us")
HW_US = N("ft", "Height (feet)", 5) + N("inch", "Height (inches)", 9) + N("lb", "Weight", 165, suf="lb", full=True)
HW_M = N("cm", "Height", 175, suf="cm") + N("kg", "Weight", 75, suf="kg")
HW_JS = "const hm=v.u==='us'?((v.ft||0)*12+(v.inch||0))*0.0254:(v.cm||0)/100,kg=v.u==='us'?(v.lb||0)*0.45359237:(v.kg||0);"
add("bmi-calculator", "Health", "⚖️", "BMI Calculator", "Body mass index for adults",
    "BMI Calculator – Check Your Body Mass Index",
    "Free BMI calculator for adults in pounds and feet or kilograms and centimeters. See your BMI, category and healthy weight range.",
    calc_box(UNITS + when("u=us", HW_US) + when("u=m", HW_M),
        "calc(v=>{" + HW_JS + """if(!(hm>0&&kg>0))return null;const b=kg/hm/hm,cat=b<18.5?"Underweight":b<25?"Healthy weight":b<30?"Overweight":"Obesity",lo=18.5*hm*hm,hi=24.9*hm*hm,f=v.u==='us'?x=>num(x/0.45359237,0)+" lb":x=>num(x,1)+" kg";
return{big:["Your BMI",num(b,1)],sub:cat,rows:[["Healthy weight for your height",f(lo)+" – "+f(hi)],["BMI categories","Under 18.5 · 18.5–24.9 · 25–29.9 · 30+"]],note:"BMI is a screening tool for adults and doesn't account for muscle, age or body type. Talk to a doctor about your health."}})"""),
    """<h2>How BMI is calculated</h2><p>BMI divides your weight by your height squared. It gives a quick estimate of whether your weight is in a typical range for your height.</p>
<p class="formula">BMI = weight (kg) ÷ height (m)² &nbsp;·&nbsp; BMI = 703 × weight (lb) ÷ height (in)²</p>
<h2>BMI categories for adults</h2><p>Under 18.5 is underweight, 18.5–24.9 is the healthy range, 25–29.9 is overweight and 30 or above is obesity. BMI can overestimate for very muscular people, so it's best used alongside other measures.</p>""")

add("calorie-calculator", "Health", "🔥", "Calorie Calculator", "Daily calories to maintain weight",
    "Calorie Calculator – How Many Calories Do I Need?",
    "Free calorie calculator. Estimate how many calories you burn per day (TDEE) based on age, height, weight and activity level.",
    calc_box(UNITS + SEG("sex", "Sex", [("m", "Male"), ("f", "Female")], "m") + N("age", "Age", 30, suf="years", full=True) + when("u=us", HW_US) + when("u=m", HW_M) +
        S("act", "Activity level", [("1.2", "Little or no exercise"), ("1.375", "Light: 1–3 days/week"), ("1.55", "Moderate: 3–5 days/week"), ("1.725", "Active: 6–7 days/week"), ("1.9", "Very active / physical job")], "1.375", full=True),
        "calc(v=>{" + HW_JS + """if(!(hm>0&&kg>0&&v.age>0))return null;const bmr=10*kg+625*hm-5*v.age+(v.sex==='m'?5:-161),t=bmr*parseFloat(v.act);
return{big:["Calories to maintain",num(t,0)+" /day"],rows:[["Resting calories (BMR)",num(bmr,0)],["Mild weight loss",num(t-250,0)],["Mild weight gain",num(t+250,0)]],note:"Estimate using the Mifflin-St Jeor equation. Everyone is different, so check with a doctor or dietitian before changing your diet."}})"""),
    """<h2>How many calories do I burn a day?</h2><p>Your body burns calories just to stay alive (your BMR), plus more for everything you do. Multiplying BMR by an activity factor gives your total daily energy expenditure, or TDEE.</p>
<p class="formula">BMR = 10 × kg + 6.25 × cm − 5 × age + 5 (men) or − 161 (women)</p>
<h2>How accurate is this?</h2><p>The Mifflin-St Jeor formula is one of the most accurate for most people, but it's still an estimate. Track how your weight changes over a few weeks and adjust from there.</p>""")

add("age-calculator", "Everyday", "🎂", "Age Calculator", "Exact age in years, months and days",
    "Age Calculator – How Old Am I Exactly?",
    "Free age calculator. Find your exact age in years, months and days, total days lived and a countdown to your next birthday.",
    calc_box(D("dob", "Date of birth", val="2000-01-01") + D("asof", "Age on this date", today=True),
        """calc(v=>{const b=parseDate(v.dob),t=parseDate(v.asof);if(!b||!t||t<b)return{error:"Pick a birth date before the second date"};
let y=t.getFullYear()-b.getFullYear(),m=t.getMonth()-b.getMonth(),d=t.getDate()-b.getDate();if(d<0){m--;d+=new Date(t.getFullYear(),t.getMonth(),0).getDate()}if(m<0){y--;m+=12}
const days=Math.round((t-b)/864e5);let nb=new Date(t.getFullYear(),b.getMonth(),b.getDate());if(nb<t)nb.setFullYear(nb.getFullYear()+1);const until=Math.round((nb-t)/864e5);
return{big:["Age",y+" years"],sub:m+" months, "+d+" days",rows:[["Total months",num(y*12+m,0)],["Total weeks",num(Math.floor(days/7),0)],["Total days",num(days,0)],["Next birthday",until===0?"🎉 Today!":"in "+until+" days"],["Born on a",b.toLocaleDateString("en-US",{weekday:"long"})]]}})"""),
    """<h2>How to calculate your age</h2><p>Enter your birthday and the calculator counts the full years, then the leftover months and days. It also shows your age in total weeks and days, and how long until your next birthday.</p>
<h2>Can I find age on a past or future date?</h2><p>Yes. Change the second date to see how old someone was on a certain day, or how old they'll be in the future. Handy for forms, school cutoffs and milestones.</p>""")

DATE2 = mini("dd", "Add or subtract days", D("start", "Start date", today=True) + S("op", "Operation", [("1", "Add"), ("-1", "Subtract")], "1") + N("n", "Days", 30),
    "v=>{const s=parseDate(v.start);if(!s||!ok(v.n))return null;const d=new Date(s);d.setDate(d.getDate()+parseInt(v.op)*v.n);return{big:['Result date',d.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'})],sub:d.toLocaleDateString('en-US',{weekday:'long'})}}")
add("date-calculator", "Everyday", "📅", "Days Between Dates", "Count days, weeks and workdays",
    "Days Between Dates Calculator – Count Days & Workdays",
    "Free date calculator. Count the days between two dates, including weekdays only, or add and subtract days from any date.",
    '<div class="stack" style="margin-top:-14px;position:relative">' +
    mini("dc", "Days between two dates", D("a", "Start date", today=True) + D("b", "End date", val=(datetime.date.today().replace(month=12, day=25) if datetime.date.today() <= datetime.date.today().replace(month=12, day=25) else datetime.date.today().replace(year=datetime.date.today().year + 1, month=12, day=25)).isoformat()) +
         '<label class="field full" style="flex-direction:row;align-items:center;gap:8px"><input type="checkbox" name="inc"> Include the end date</label>',
         """v=>{const a=parseDate(v.a),b=parseDate(v.b);if(!a||!b)return null;const[s,e]=a<b?[a,b]:[b,a];let days=Math.round((e-s)/864e5)+(v.inc?1:0),wd=0;const c=new Date(s);for(let i=0;i<days&&i<40000;i++){const w=c.getDay();if(w&&w<6)wd++;c.setDate(c.getDate()+1)}
return{big:['Days between',num(days,0)+' days'],rows:[['Weeks',Math.floor(days/7)+' weeks, '+days%7+' days'],['Weekdays (Mon–Fri)',num(wd,0)],['Months (approx.)',num(days/30.4375,1)],['Years (approx.)',num(days/365.25,2)]]}}""") +
    DATE2 + "</div>",
    """<h2>How to count days between dates</h2><p>Pick a start and end date and you'll see the number of days in between, plus weeks, weekdays and an approximate number of months. Tick "Include the end date" if you're counting both the first and last day, like for a trip or event.</p>
<h2>Counting business days</h2><p>The weekday count skips Saturdays and Sundays. It doesn't remove holidays, so subtract any holidays that fall in your range.</p>""")

HOURS_ROWS = "".join(f'<tr><td><b>{d}</b></td><td><span class="inp"><input type="time" name="s{i}" value="{"09:00" if i < 5 else ""}"></span></td><td><span class="inp"><input type="time" name="e{i}" value="{"17:00" if i < 5 else ""}"></span></td><td><span class="inp"><input type="number" inputmode="numeric" name="b{i}" value="{30 if i < 5 else ""}" placeholder="0"></span></td></tr>' for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]))
add("hours-calculator", "Everyday", "⏰", "Hours Calculator", "Weekly time card with pay",
    "Hours Calculator – Time Card Calculator with Breaks",
    "Free time card calculator. Add up hours worked each day with start and end times and breaks, then see total hours and pay for the week.",
    calc_box(f'<div class="field full"><table class="grid tc"><tr><th>Day</th><th>Start</th><th>End</th><th>Break (min)</th></tr>{HOURS_ROWS}</table></div>' +
        N("rate", "Hourly pay (optional)", 20, "$") + N("ot", "Overtime after", 40, suf="hours"),
        """calc(v=>{let tot=0;const per=[];for(let i=0;i<7;i++){const s=v["s"+i],e=v["e"+i];if(!s||!e){per.push(0);continue}const[a,b]=s.split(":").map(Number),[c,d]=e.split(":").map(Number);let m=(c*60+d)-(a*60+b);if(m<0)m+=1440;m-=(v["b"+i]||0);m=Math.max(0,m);per.push(m);tot+=m}
const h=tot/60,fmt=m=>Math.floor(m/60)+"h "+String(Math.round(m%60)).padStart(2,"0")+"m",ot=Math.max(0,h-(v.ot||40)),reg=h-ot,pay=v.rate?reg*v.rate+ot*v.rate*1.5:NaN,days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
return{big:["Total hours",num(h,2)],sub:fmt(tot),rows:[...per.map((m,i)=>m?[days[i],fmt(m)]:null).filter(Boolean),...(ot>0?[["Overtime hours",num(ot,2)]]:[]),...(ok(pay)?[["Gross pay",money(pay)]]:[])],note:ot>0?"Overtime paid at 1.5×.":""}})""",
        title="Your week"),
    """<h2>How to calculate hours worked</h2><p>For each day, subtract the start time from the end time and take off unpaid breaks. Shifts that go past midnight are handled automatically. The total is shown in both decimal hours (for payroll) and hours and minutes.</p>
<h2>Converting minutes to decimal hours</h2><p>Divide minutes by 60. 15 minutes is 0.25 hours, 30 minutes is 0.5 and 45 minutes is 0.75. So 7 hours 45 minutes is 7.75 hours.</p>""")

GPA_ROWS = "".join(f'<tr><td><span class="inp"><input name="n{i}" placeholder="Class {i + 1}"></span></td><td><span class="inp"><select name="g{i}"><option value="">—</option>' + "".join(f'<option value="{v}"{" selected" if (i < 4 and v == ["4.0", "3.3", "3.7", "3.0"][i]) else ""}>{t}</option>' for v, t in GRADES) + f'</select></span></td><td><span class="inp"><input type="number" inputmode="decimal" name="c{i}" value="{3 if i < 4 else ""}" placeholder="0"></span></td></tr>' for i in range(8))
add("gpa-calculator", "Everyday", "🎓", "GPA Calculator", "Semester and cumulative GPA",
    "GPA Calculator – Calculate Your Semester & Cumulative GPA",
    "Free GPA calculator on a 4.0 scale. Enter your letter grades and credit hours to get your semester GPA and updated cumulative GPA.",
    calc_box(f'<div class="field full"><table class="grid"><tr><th>Class (optional)</th><th>Grade</th><th>Credits</th></tr>{GPA_ROWS}</table></div>' +
        N("cg", "Current GPA (optional)", "") + N("cc", "Credits so far (optional)", ""),
        """calc(v=>{let q=0,c=0;for(let i=0;i<8;i++){const g=v["g"+i],cr=v["c"+i];if(g!==""&&cr>0){q+=parseFloat(g)*cr;c+=cr}}if(!c)return null;const g=q/c;const rows=[["Credits this term",num(c)],["Grade points",num(q,2)]];
if(v.cg>=0&&v.cc>0){rows.push(["New cumulative GPA",num((v.cg*v.cc+q)/(v.cc+c),2)]);rows.push(["Total credits",num(v.cc+c)])}return{big:["Semester GPA",g.toFixed(2)],rows}})""",
        title="Your classes"),
    """<h2>How GPA is calculated</h2><p>Each letter grade is worth grade points (A = 4.0, B = 3.0 and so on). Multiply each class's grade points by its credit hours, add them up, then divide by your total credits.</p>
<p class="formula">GPA = Σ(grade points × credits) ÷ Σ credits</p>
<h2>How to find your cumulative GPA</h2><p>Add your current GPA and the number of credits you've already completed. The calculator combines them with this term's classes to show your new overall GPA.</p>""")

add("grade-calculator", "Everyday", "📝", "Grade Calculator", "Test score % and final exam needed",
    "Grade Calculator – Test Percentage & Final Exam Grade Needed",
    "Free grade calculator. Turn points into a percentage and letter grade, and find out what you need on your final exam to get the grade you want.",
    '<div class="stack" style="margin-top:-14px;position:relative">' +
    mini("g1", "Test score to percentage", N("a", "Points earned", 42) + N("b", "Points possible", 50),
         "v=>{if(!(v.b>0))return null;const p=v.a/v.b*100,L=p>=97?'A+':p>=93?'A':p>=90?'A-':p>=87?'B+':p>=83?'B':p>=80?'B-':p>=77?'C+':p>=73?'C':p>=70?'C-':p>=67?'D+':p>=63?'D':p>=60?'D-':'F';return{big:['Score',pct(p,2)],sub:'Letter grade: '+L,rows:[['Points missed',num(v.b-v.a)]]}}") +
    mini("g2", "Final exam grade needed", N("cur", "Current grade", 85, suf="%") + N("want", "Grade you want", 90, suf="%") + N("w", "Final exam weight", 20, suf="%", full=True),
         "v=>{if(!(v.w>0))return null;const n=(v.want-v.cur*(1-v.w/100))/(v.w/100);return{big:['You need',pct(n,1)],sub:'on the final to get '+pct(v.want,0),note:n>100?'That\\'s above 100%, so it may not be possible without extra credit.':n<=0?'You\\'ve already locked it in! 🎉':''}}") + "</div>",
    """<h2>How to calculate a test grade</h2><p>Divide the points you earned by the points possible and multiply by 100. 42 out of 50 is 84%, which is a B on the standard scale.</p>
<p class="formula">Needed on final = (goal − current × (1 − weight)) ÷ weight</p>
<h2>What do I need on my final?</h2><p>Enter your current grade, the grade you want and how much the final is worth (check your syllabus). The calculator shows the exact score you need.</p>""")

# ---------- money & business calculators (added) ----------
NO_TAX_STATES = [("TX", "Texas"), ("FL", "Florida"), ("TN", "Tennessee"), ("WA", "Washington"), ("NV", "Nevada"), ("AK", "Alaska"), ("SD", "South Dakota"), ("WY", "Wyoming"), ("NH", "New Hampshire")]
PAY_JS = """calc(v=>{const per={52:"week",26:"2 weeks",24:"half-month",12:"month"},f=v.freq,gross=v.type==="hourly"?v.amt*(v.hours||40)*52:v.amt;if(!(gross>0)||!f)return null;
const k4=gross*(v.k401||0)/100,hl=(v.health||0)*f,fw=Math.max(0,gross-hl),ss=Math.min(fw,TAX2026.ssBase)*.062,med=fw*.0145+Math.max(0,fw-200000)*.009;
const ft=fedTax(Math.max(0,gross-k4-hl-TAX2026.std[v.status]),v.status),st=v.state==="other"?Math.max(0,gross-k4-hl)*(v.srate||0)/100:0;
const net=gross-k4-hl-ft.tax-ss-med-st,p=x=>money(x/f);
return{big:["Take-home pay per paycheck",p(net)],sub:money(net,0)+" a year · paid every "+per[f],rows:[["Gross pay",p(gross)],["Federal income tax",p(ft.tax)],["Social Security (6.2%)",p(ss)],["Medicare (1.45%)",p(med)],["State income tax",v.state==="other"?p(st):"$0.00 (no state income tax)"],...(k4?[["401(k)",p(k4)]]:[]),...(hl?[["Health insurance",p(hl)]]:[]),["Federal tax bracket",Math.round(ft.top*100)+"%"],["Total tax rate",pct((ft.tax+ss+med+st)/gross*100,1)]],
chart:donut([["Take-home",net,"#10b981"],["Federal tax",ft.tax,"#6366f1"],["Social Security & Medicare",ss+med,"#ec4899"],["State tax",st,"#f59e0b"],["401(k) & benefits",k4+hl,"#06b6d4"]].filter(x=>x[1]>0)),note:"2026 estimate using IRS tax brackets and the standard deduction. Your real withholding depends on your W-4 and benefits."}})"""

def paycheck_tool(state="TX"):
    opts = [(c, n + " (no state income tax)") for c, n in NO_TAX_STATES] + [("other", "Another state (enter its rate)")]
    return calc_box(
        SEG("type", "How are you paid?", [("salary", "Salary (per year)"), ("hourly", "Hourly")], "salary") +
        N("amt", "Pay amount", 60000, "$", full=True) +
        when("type=hourly", N("hours", "Hours per week", 40, full=True)) +
        S("freq", "Pay frequency", [(26, "Every 2 weeks"), (52, "Weekly"), (24, "Twice a month"), (12, "Monthly")], 26) +
        S("status", "Filing status", [("single", "Single"), ("mfj", "Married filing jointly"), ("hoh", "Head of household")], "single") +
        S("state", "State", opts, state, full=True) +
        when("state=other", N("srate", "Your state income tax rate", 4.5, suf="%", full=True)) +
        N("k401", "401(k) contribution", 0, suf="% of pay") + N("health", "Health insurance", 0, "$", suf="/ check"),
        PAY_JS)

STATE_LINKS = '<div class="statelinks">' + "".join(f'<a href="{n.lower().replace(" ", "-")}-paycheck-calculator">{n}</a>' for c, n in NO_TAX_STATES) + "</div>"
PAY_CONTENT = """<h2>How your paycheck is calculated</h2><p>Start with your gross pay, then subtract pre-tax benefits like a 401(k) and health insurance. Federal income tax is figured with the 2026 IRS brackets after the standard deduction ($16,100 single, $32,200 married). Then Social Security (6.2%, on the first $184,500) and Medicare (1.45%) come out, plus state income tax if your state has one.</p>
<p class="formula">Take-home = gross pay − pre-tax benefits − federal tax − Social Security − Medicare − state tax</p>
<h2>Why is my paycheck different?</h2><p>Your employer withholds based on your W-4 form, so extra withholding, dependents, or other income can change the real number. Local taxes, union dues, HSA contributions and wage garnishments aren't included here.</p>
<h2>Paycheck calculators by state</h2><p>These states have no state income tax on wages, so more of your paycheck stays with you:</p>""" + STATE_LINKS

add("paycheck-calculator", "Financial", "💸", "Paycheck Calculator", "Take-home pay after 2026 taxes",
    "Paycheck Calculator 2026 – Take-Home Pay After Taxes",
    "Free 2026 paycheck calculator. See your take-home pay after federal tax, Social Security, Medicare and state tax for salary or hourly pay, per paycheck and per year.",
    paycheck_tool("TX"), PAY_CONTENT)

for code, sname in NO_TAX_STATES:
    slug = sname.lower().replace(" ", "-") + "-paycheck-calculator"
    add(slug, "Financial", "💸", f"{sname} Paycheck Calculator", f"Take-home pay in {sname}",
        f"{sname} Paycheck Calculator 2026 – Take-Home Pay After Taxes",
        f"Free {sname} paycheck calculator for 2026. {sname} has no state income tax, so see your take-home pay after federal tax, Social Security and Medicare.",
        paycheck_tool(code),
        f"""<h2>{sname} paycheck taxes</h2><p>{sname} doesn't tax wages, so your paycheck only has federal income tax, Social Security (6.2%) and Medicare (1.45%) taken out, plus any benefits you choose. That means you keep more of each paycheck than workers in most other states.</p>
<h2>How the calculator works</h2><p>Enter your salary or hourly wage and how often you're paid. Federal tax uses the 2026 IRS brackets and the standard deduction. Pre-tax 401(k) and health insurance lower your taxable income.</p>
<h2>Other paycheck calculators</h2><p>See the <a href="paycheck-calculator">main paycheck calculator</a> or another no-income-tax state:</p>""" + STATE_LINKS, hidden=True)

add("house-affordability-calculator", "Financial", "🏡", "How Much House Can I Afford", "Max home price for your income",
    "How Much House Can I Afford? – Home Affordability Calculator",
    "Find out how much house you can afford based on your income, debts and down payment. Uses the 28/36 rule lenders use, with taxes and insurance included.",
    calc_box(
        N("income", "Yearly household income (before tax)", 90000, "$", full=True) +
        N("debts", "Monthly debt payments", 400, "$") + N("down", "Down payment saved", 30000, "$") +
        N("rate", "Mortgage rate", 6.5, suf="%") + S("years", "Loan term", [(30, "30 years"), (15, "15 years")], 30) +
        N("ptax", "Property tax rate", 1.6, suf="% / yr") + N("ins", "Home insurance", 2000, "$", suf="/ yr") + N("hoa", "HOA", 0, "$", suf="/ mo"),
        """calc(v=>{const inc=v.income/12;if(!(inc>0))return null;const M=Math.min(inc*.28,inc*.36-(v.debts||0));if(M<=0)return{error:"Your monthly debts are too high for a typical mortgage at this income"};
const n=v.years*12,r=(v.rate||0)/1200,k=r?r/(1-Math.pow(1+r,-n)):1/n,fix=(v.ins||0)/12+(v.hoa||0),dn=v.down||0,price=(M-fix+dn*k)/(k+(v.ptax||0)/1200);if(!(price>0))return null;
const loan=Math.max(0,price-dn),pi=loan*k,tx=price*(v.ptax||0)/1200,tot=pi+tx+fix;
return{big:["You can afford a home up to",money(price,0)],sub:"Monthly payment about "+money(tot,0),rows:[["Loan amount",money(loan,0)],["Down payment",money(dn,0)+" ("+pct(dn/price*100,1)+")"],["Principal & interest",money(pi)],["Property tax",money(tx)],["Insurance + HOA",money(fix)],["Housing cost ratio (limit 28%)",pct(tot/inc*100,1)],["Total debt ratio (limit 36%)",pct((tot+(v.debts||0))/inc*100,1)]],
chart:donut([["Principal & interest",pi],["Property tax",tx],["Insurance & HOA",fix]].filter(x=>x[1]>0)),note:"Uses the 28/36 rule many lenders start with. FHA and some other loans allow higher ratios. Under 20% down usually adds mortgage insurance (PMI)."}})"""),
    """<h2>How much house can I afford?</h2><p>Most lenders use the <b>28/36 rule</b>: your housing payment (mortgage, property tax, insurance and HOA) should be no more than 28% of your gross monthly income, and all your debts together no more than 36%. This calculator finds the highest home price that fits both limits.</p>
<h2>How to afford more house</h2><ul><li>Pay down car loans, student loans or credit cards to free up room in the 36% limit.</li><li>Save a bigger down payment.</li><li>Shop around for a lower mortgage rate, since even 0.5% makes a big difference.</li><li>Look at areas with lower property taxes.</li></ul>""")

add("budget-calculator", "Financial", "📒", "Budget Calculator", "50/30/20 monthly budget planner",
    "Budget Calculator – Free 50/30/20 Monthly Budget Planner",
    "Free monthly budget calculator. Enter your take-home pay and expenses to see what's left over and how you compare to the 50/30/20 budget rule.",
    calc_box(
        N("income", "Monthly take-home pay", 4500, "$", full=True) +
        N("rent", "Rent / mortgage", 1400, "$") + N("util", "Utilities & phone", 250, "$") + N("food", "Groceries", 500, "$") + N("car", "Car & gas", 450, "$") +
        N("ins", "Insurance", 200, "$") + N("debt", "Debt payments", 200, "$") + N("subs", "Subscriptions", 60, "$") + N("fun", "Eating out & fun", 400, "$") + N("save", "Savings & investing", 500, "$", full=True),
        """calc(v=>{const I=v.income;if(!(I>0))return null;const g=k=>v[k]||0,needs=g("rent")+g("util")+g("food")+g("car")+g("ins")+g("debt"),wants=g("subs")+g("fun"),sv=g("save"),left=I-needs-wants-sv;
return{big:[left>=0?"Left over each month":"Over budget by",money(Math.abs(left))],sub:left>=0?"Put it toward savings or paying off debt.":"Trim some spending to break even.",rows:[["Needs (target 50%)",money(needs,0)+" · "+pct(needs/I*100,0)],["Wants (target 30%)",money(wants,0)+" · "+pct(wants/I*100,0)],["Savings (target 20%)",money(sv,0)+" · "+pct(sv/I*100,0)],["50/30/20 targets",money(I*.5,0)+" / "+money(I*.3,0)+" / "+money(I*.2,0)]],
chart:donut([["Needs",needs,"#6366f1"],["Wants",wants,"#ec4899"],["Savings",sv,"#10b981"],["Left over",Math.max(0,left),"#f59e0b"]].filter(x=>x[1]>0))}})"""),
    """<h2>The 50/30/20 budget rule</h2><p>A simple way to split your take-home pay: <b>50% for needs</b> (housing, food, utilities, transportation, minimum debt payments), <b>30% for wants</b> (eating out, entertainment, shopping) and <b>20% for savings</b> and extra debt payoff.</p>
<h2>Tips to stick to your budget</h2><ul><li>Set up automatic transfers to savings on payday so you save first.</li><li>Review subscriptions every few months and cancel ones you don't use.</li><li>Build an emergency fund of 3–6 months of needs before investing heavily.</li></ul>""")

DEBT_ROWS = "".join(f'<tr><td><span class="inp"><input name="n{i}" placeholder="Debt {i + 1}" value="{n}"></span></td><td><span class="inp"><input type="number" inputmode="decimal" name="b{i}" placeholder="0" value="{b}"></span></td><td><span class="inp"><input type="number" inputmode="decimal" name="r{i}" placeholder="0" value="{r}"></span></td><td><span class="inp"><input type="number" inputmode="decimal" name="m{i}" placeholder="0" value="{m}"></span></td></tr>'
    for i, (n, b, r, m) in enumerate([("Credit card", 4200, 24.9, 120), ("Car loan", 9800, 7.5, 290), ("Store card", 900, 29.9, 35), ("", "", "", ""), ("", "", "", "")]))
add("debt-payoff-calculator", "Financial", "❄️", "Debt Payoff Calculator", "Snowball vs avalanche payoff plan",
    "Debt Payoff Calculator – Debt Snowball & Avalanche Planner",
    "Free debt payoff calculator. Compare the debt snowball and avalanche methods, see your debt-free date and how much interest extra payments save.",
    calc_box(f'<div class="field full"><table class="grid debts"><tr><th>Debt</th><th>Balance $</th><th>APR %</th><th>Min $</th></tr>{DEBT_ROWS}</table></div>' +
        N("extra", "Extra payment each month", 200, "$", full=True) +
        SEG("method", "Payoff method", [("snowball", "Snowball (smallest first)"), ("avalanche", "Avalanche (highest rate first)")], "snowball"),
        """calc(v=>{const ds=[];for(let i=0;i<5;i++){const b=v["b"+i];if(b>0)ds.push({n:v["n"+i]||"Debt "+(i+1),b,r:(v["r"+i]||0)/1200,m:v["m"+i]||0})}if(!ds.length)return null;
const sim=(extra,roll)=>{const d=ds.map(x=>({...x})),order=[],budget=ds.reduce((s,x)=>s+x.m,0)+extra;let mo=0,int=0;
while(d.some(x=>x.b>.005)&&mo<600){mo++;d.forEach(x=>{if(x.b>0){const i=x.b*x.r;x.b+=i;int+=i}});let pool=roll?budget:extra;
d.forEach(x=>{if(x.b>0){const p=Math.min(x.b,x.m);x.b-=p;if(roll)pool-=p}});
d.filter(x=>x.b>.005).sort(v.method==="avalanche"?(a,b)=>b.r-a.r||a.b-b.b:(a,b)=>a.b-b.b).forEach(x=>{if(pool>0){const p=Math.min(x.b,pool);x.b-=p;pool-=p}});
d.forEach(x=>{if(x.b<=.005&&!x.done){x.done=1;x.b=0;order.push([x.n,mo])}})}return{mo,int,order,ok:mo<600}};
const a=sim(v.extra||0,true),b=sim(0,false);if(!a.ok)return{error:"Your payments don't cover the interest. Raise your payments to see a payoff date."};
const yr=m=>Math.floor(m/12)+" yr "+(m%12)+" mo",d=new Date();d.setMonth(d.getMonth()+a.mo);
return{big:["Debt-free in",yr(a.mo)],sub:"by "+d.toLocaleDateString("en-US",{month:"long",year:"numeric"}),rows:[["Total interest",money(a.int,0)],...(b.ok?[["Interest saved vs. minimums",money(b.int-a.int,0)],["Time saved",yr(Math.max(0,b.mo-a.mo))]]:[["Minimum payments only","Never paid off"]]),...a.order.map((x,i)=>[(i+1)+". "+x[0]+" paid off","month "+x[1]])]}})""", title="Your debts"),
    """<h2>Debt snowball vs. debt avalanche</h2><p>Both methods pay the minimum on every debt and put every extra dollar toward one target debt. When it's paid off, its payment rolls into the next one, so your payments snowball.</p><ul><li><b>Snowball:</b> pay off the smallest balance first. Quick wins keep you motivated.</li><li><b>Avalanche:</b> pay off the highest interest rate first. This saves the most money.</li></ul>
<h2>How to get out of debt faster</h2><ul><li>Even $50–$100 extra a month can cut years off your payoff.</li><li>Ask your card company for a lower rate, or look into a 0% balance transfer.</li><li>Put tax refunds and bonuses straight toward your target debt.</li></ul>""")

PM = (mini("pm1", "Profit margin from cost and price", N("c", "Cost", 40, "$") + N("p", "Selling price", 65, "$"),
          "v=>{if(!(v.p>0))return null;const pr=v.p-v.c;return{big:['Profit margin',pct(pr/v.p*100,2)],rows:[['Profit',money(pr)],['Markup',v.c>0?pct(pr/v.c*100,2):'—']]}}") +
      mini("pm2", "Price for a target margin", N("c", "Cost", 40, "$") + N("m", "Desired margin", 35, suf="%"),
          "v=>{if(!(v.m<100))return{error:'Margin must be under 100%'};const p=v.c/(1-v.m/100);return{big:['Sell it for',money(p)],rows:[['Profit',money(p-v.c)],['Markup',pct((p-v.c)/v.c*100,2)]]}}") +
      mini("pm3", "Price from a markup", N("c", "Cost", 40, "$") + N("k", "Markup", 50, suf="%"),
          "v=>{if(!(v.c>0))return null;const p=v.c*(1+v.k/100);return{big:['Selling price',money(p)],rows:[['Profit',money(p-v.c)],['Profit margin',pct((p-v.c)/p*100,2)]]}}"))
add("profit-margin-calculator", "Business", "📈", "Profit Margin Calculator", "Margin, markup and selling price",
    "Profit Margin Calculator – Margin, Markup & Selling Price",
    "Free profit margin calculator. Find your profit margin and markup from cost and price, or work out the selling price you need for a target margin.",
    '<div class="stack" style="margin-top:-14px;position:relative">' + PM + "</div>",
    """<h2>Margin vs. markup</h2><p><b>Margin</b> is profit as a percent of the selling price. <b>Markup</b> is profit as a percent of the cost. If something costs $40 and sells for $65, the profit is $25: a 38.5% margin but a 62.5% markup.</p>
<p class="formula">Margin = (price − cost) ÷ price &nbsp;·&nbsp; Markup = (price − cost) ÷ cost</p>
<h2>What's a good profit margin?</h2><p>It depends on the industry. Grocery stores run on 1–3% net margins, restaurants 3–10%, and software or services can reach 20% or more. For product pricing, many small businesses aim for at least a 30–50% gross margin to cover overhead.</p>""")

add("break-even-calculator", "Business", "⚖️", "Break-Even Calculator", "Units and sales needed to profit",
    "Break-Even Calculator – Find Your Break-Even Point",
    "Free break-even calculator. Find how many units you need to sell to cover your costs, your break-even revenue and the sales needed to hit a profit goal.",
    calc_box(N("fixed", "Fixed costs per month", 5000, "$", full=True) + N("price", "Price per unit", 50, "$") + N("varc", "Variable cost per unit", 20, "$") + N("goal", "Profit goal per month (optional)", 0, "$", full=True),
        """calc(v=>{const cm=v.price-v.varc;if(!(v.price>0))return null;if(!(cm>0))return{error:"Your price must be higher than your variable cost per unit"};
const u=(v.fixed||0)/cm,ug=((v.fixed||0)+(v.goal||0))/cm;return{big:["Break-even point",num(Math.ceil(u),0)+" units"],sub:money(Math.ceil(u)*v.price,0)+" in sales per month",rows:[["Profit per unit",money(cm)],["Contribution margin",pct(cm/v.price*100,1)],...(v.goal>0?[["Units for your profit goal",num(Math.ceil(ug),0)],["Sales for your profit goal",money(Math.ceil(ug)*v.price,0)]]:[]),["Units per day (30-day month)",num(u/30,1)]]}})"""),
    """<h2>How to calculate break-even</h2><p>Each sale brings in its price minus its variable cost (materials, shipping, fees). That's your <b>contribution margin</b>. Divide your fixed costs (rent, salaries, software) by it to see how many sales cover them.</p>
<p class="formula">Break-even units = fixed costs ÷ (price − variable cost per unit)</p>
<h2>How to lower your break-even point</h2><ul><li>Raise prices, even slightly.</li><li>Cut variable costs with better suppliers or cheaper shipping.</li><li>Reduce fixed costs like rent or unused subscriptions.</li></ul>""")

add("self-employment-tax-calculator", "Business", "🧾", "Self-Employment Tax Calculator", "1099 and quarterly tax estimate",
    "Self-Employment Tax Calculator 2026 – 1099 & Quarterly Taxes",
    "Free 2026 self-employment tax calculator for freelancers and 1099 workers. Estimate SE tax, federal income tax and your quarterly estimated payments.",
    calc_box(N("inc", "1099 / business income", 75000, "$", suf="/ yr") + N("exp", "Business expenses", 12000, "$", suf="/ yr") +
        S("status", "Filing status", [("single", "Single"), ("mfj", "Married filing jointly"), ("hoh", "Head of household")], "single") +
        N("w2", "Other W-2 wages (optional)", 0, "$") + N("srate", "State income tax rate", 0, suf="%", full=True),
        """calc(v=>{const net=(v.inc||0)-(v.exp||0);if(!(net>0))return null;const w2=v.w2||0,base=net*.9235,ssr=Math.max(0,TAX2026.ssBase-w2),ss=Math.min(base,ssr)*.124,med=base*.029,addl=Math.max(0,base+w2-TAX2026.addlMedicare[v.status])*.009,se=ss+med+addl;
const std=TAX2026.std[v.status],all=fedTax(Math.max(0,net+w2-(ss+med)/2-std),v.status),w2only=fedTax(Math.max(0,w2-std),v.status),fed=all.tax-w2only.tax,st=net*(v.srate||0)/100,tot=se+fed+st;
return{big:["Quarterly estimated payment",money(tot/4,0)],sub:money(tot,0)+" total for the year",rows:[["Net profit",money(net,0)],["Self-employment tax",money(se,0)],["Federal income tax on this income",money(fed,0)],...(st?[["State income tax",money(st,0)]]:[]),["Set aside from each payment",pct(tot/net*100,1)],["Federal tax bracket",Math.round(all.top*100)+"%"],["2026 due dates","Apr 15 · Jun 15 · Sep 15 · Jan 15"]],
chart:donut([["Self-employment tax",se,"#ec4899"],["Federal income tax",fed,"#6366f1"],["State tax",st,"#f59e0b"],["You keep",net-tot,"#10b981"]].filter(x=>x[1]>0)),note:"2026 estimate. Doesn't include the 20% QBI deduction or credits, which may lower your bill. Check with a tax pro."}})"""),
    """<h2>How self-employment tax works</h2><p>When you work for yourself, you pay both the employee and employer share of Social Security and Medicare: <b>15.3%</b> (12.4% + 2.9%). It applies to 92.35% of your net profit, and the Social Security part stops at $184,500 in 2026. You can deduct half of it from your income before federal tax.</p>
<p class="formula">SE tax = net profit × 92.35% × 15.3%</p>
<h2>Quarterly estimated taxes</h2><p>Nobody withholds taxes from 1099 income, so the IRS expects you to pay four times a year. For 2026 income, payments are due April 15, June 15, September 15 and January 15, 2027. Paying late can mean an underpayment penalty.</p>
<h2>How to lower your tax bill</h2><ul><li>Track every business expense: mileage, equipment, software, phone and home office.</li><li>Contribute to a SEP-IRA or Solo 401(k).</li><li>Keep money for taxes in a separate savings account as you get paid.</li></ul>""")

add("solar-panel-calculator", "Financial", "☀️", "Solar Panel Calculator", "System size, cost and payback",
    "Solar Panel Calculator – Cost, Savings & Payback (2026)",
    "Free solar panel calculator. Estimate how many panels you need, system size, installed cost, yearly savings and payback period from your electric bill.",
    calc_box(N("bill", "Average monthly electric bill", 160, "$") + N("rate", "Electricity rate", .17, "$", suf="/ kWh") +
        N("sun", "Peak sun hours per day", 4.5, suf="hrs") + N("off", "Bill to offset", 100, suf="%") +
        N("watts", "Panel size", 400, suf="watts") + N("cpw", "Installed cost per watt", 3.0, "$") + N("reb", "Rebates & incentives (optional)", 0, "$", full=True),
        """calc(v=>{if(!(v.bill>0&&v.rate>0&&v.sun>0))return null;const kwh=v.bill/v.rate,kw=kwh*12*(v.off||100)/100/(365*v.sun*.8),pan=Math.ceil(kw*1000/(v.watts||400)),cost=kw*1000*(v.cpw||0),net=Math.max(0,cost-(v.reb||0));
let save=v.bill*12*(v.off||100)/100,tot=0,pay=null,cum=0;for(let y=1;y<=25;y++){cum+=save;tot+=save;if(pay===null&&cum>=net)pay=y;save*=1.03*.995}
return{big:["Estimated payback",pay?pay+" years":"25+ years"],sub:num(pan,0)+" panels · "+num(kw,1)+" kW system",rows:[["Installed cost",money(cost,0)],...(v.reb?[["Cost after rebates",money(net,0)]]:[]),["First-year savings",money(v.bill*12*(v.off||100)/100,0)],["25-year savings",money(tot,0)],["25-year net gain",money(tot-net,0)],["Monthly usage",num(kwh,0)+" kWh"]],note:"Assumes 3% yearly electricity price increases and 0.5% yearly panel wear. The 30% federal tax credit ended for homeowner-bought systems after 2025."}})"""),
    """<h2>How many solar panels do I need?</h2><p>Divide your monthly bill by your electricity rate to get your usage in kWh. The calculator then sizes a system using your area's peak sun hours, with an 80% efficiency factor for real-world losses like heat, shade and wiring.</p>
<p class="formula">System size (kW) = yearly kWh ÷ (365 × sun hours × 0.8)</p>
<h2>Is solar still worth it in 2026?</h2><p>The 30% federal tax credit for homeowners who buy solar ended after December 31, 2025, so payback takes longer than it used to. Solar can still pay off in sunny states with high electricity rates. Check for state and utility rebates, and compare cash, loan and lease options.</p>
<h2>Peak sun hours by region</h2><p>Southwest US: 5.5–7 hours. Texas and the Southeast: 4.5–5.5. Midwest and Northeast: 3.5–4.5. Pacific Northwest: 3–4.</p>""")

INV_TOOL = '''<div class="invwrap"><form class="panel" id="inv" autocomplete="off" onsubmit="return false"><h2>Invoice details</h2><div class="fields">
<label class="field">Your business<span class="inp"><input data-f="from" placeholder="Your business name"></span></label>
<label class="field">Invoice #<span class="inp"><input data-f="num" value="1001"></span></label>
<label class="field full">Your address / email<span class="inp"><textarea data-f="fromd" style="min-height:60px" placeholder="123 Main St&#10;City, ST 12345&#10;you@email.com"></textarea></span></label>
<label class="field">Bill to<span class="inp"><input data-f="to" placeholder="Client name"></span></label>
<label class="field">Currency<span class="inp"><select data-f="cur"><option>USD</option><option>CAD</option><option>EUR</option><option>GBP</option><option>AUD</option><option>MXN</option></select></span></label>
<label class="field full">Client address / email<span class="inp"><textarea data-f="tod" style="min-height:60px"></textarea></span></label>
<label class="field">Invoice date<span class="inp"><input type="date" data-f="date"></span></label>
<label class="field">Due date<span class="inp"><input type="date" data-f="due"></span></label>
<div class="field full"><table class="grid"><tr><th>Item</th><th>Qty</th><th>Rate</th><th></th></tr><tbody id="items"></tbody></table><button type="button" class="btn" id="add" style="margin-top:6px">+ Add line</button></div>
<label class="field">Tax %<span class="inp"><input type="number" step="any" data-f="tax" value="0"></span></label>
<label class="field">Discount %<span class="inp"><input type="number" step="any" data-f="disc" value="0"></span></label>
<label class="field full">Notes / payment terms<span class="inp"><textarea data-f="notes" style="min-height:60px" placeholder="Payment due within 30 days. Thank you for your business!"></textarea></span></label>
</div><div class="row noprint" style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap"><button type="button" class="btn primary" id="print">⬇ Download PDF / Print</button><button type="button" class="btn" id="clear">Start over</button></div>
<p class="note" style="color:var(--muted);font-size:.82rem">Your invoice saves automatically in this browser. Choose "Save as PDF" in the print window to download it.</p></form>
<div class="invoice" id="preview"></div></div><script src="invoice.js"></script>'''
add("invoice-generator", "Business", "🧾", "Invoice Generator", "Make and download a PDF invoice",
    "Free Invoice Generator – Create & Download PDF Invoices",
    "Free invoice generator. Create a professional invoice online, add line items, tax and discounts, and download it as a PDF. No sign-up, saved in your browser.",
    INV_TOOL,
    """<h2>How to make an invoice</h2><ol><li>Add your business name and your client's details.</li><li>Enter each product or service with its quantity and rate. Totals update instantly.</li><li>Add tax, a discount and your payment terms.</li><li>Click <b>Download PDF / Print</b> and choose "Save as PDF".</li></ol>
<h2>What should an invoice include?</h2><p>A unique invoice number, the date and due date, your and your client's contact details, a clear list of what you're billing for, the total amount due, and how to pay you. Clear payment terms like "Net 30" help you get paid on time.</p>
<h2>Is my invoice private?</h2><p>Yes. Everything stays in your browser. Nothing is uploaded to our servers.</p>""")

# ---------- business loans & payroll (added) ----------
APR_JS = "const trueAPR=(net,pmt,n)=>{if(!(net>0&&pmt>0&&n>0))return NaN;let lo=0,hi=1;for(let i=0;i<80;i++){const r=(lo+hi)/2,pv=pmt*(1-Math.pow(1+r,-n))/r;pv>net?lo=r:hi=r}return (lo+hi)/2*1200};"
add("sba-loan-calculator", "Business", "🏛️", "SBA Loan Calculator", "Monthly payment on SBA 7(a) & 504 loans",
    "SBA Loan Calculator – SBA 7(a) & 504 Loan Payments",
    "Free SBA loan calculator. Estimate monthly payments, total interest and guarantee fees for SBA 7(a) and 504 loans for working capital, equipment and real estate.",
    calc_box(
        S("years", "Loan use (sets the term)", [(10, "Working capital / equipment – 10 years"), (25, "Real estate – 25 years"), (7, "Short term – 7 years"), (5, "Short term – 5 years")], 10, full=True) +
        N("amt", "Loan amount", 250000, "$", full=True) + N("rate", "Interest rate", 10.5, suf="%") + N("fee", "SBA guarantee & lender fees", 2, suf="% of loan"),
        APR_JS + """calc(v=>{const n=v.years*12,p=payment(v.amt,v.rate||0,n);if(!(v.amt>0)||!ok(p))return null;const fee=v.amt*(v.fee||0)/100,ti=p*n-v.amt;
return{big:["Monthly payment",money(p)],sub:"over "+v.years+" years",rows:[["Total interest",money(ti,0)],["Upfront fees",money(fee,0)],["Total cost of the loan",money(ti+fee,0)],["Total you'll repay",money(p*n,0)],["APR including fees",pct(trueAPR(v.amt-fee,p,n),2)]],chart:donut([["Principal",v.amt],["Interest",ti],["Fees",fee]].filter(x=>x[1]>0))}})"""),
    """<h2>How SBA loan payments work</h2><p>SBA loans are regular amortizing loans, so you pay the same amount every month until the loan is paid off. Terms are long: up to 10 years for working capital and equipment, and up to 25 years for real estate. Long terms keep monthly payments low.</p>
<p class="formula">Payment = loan × r ÷ (1 − (1 + r)⁻ⁿ) &nbsp;·&nbsp; r = yearly rate ÷ 12, n = months</p>
<h2>SBA 7(a) vs. 504 loans</h2><ul><li><b>7(a):</b> the most common SBA loan. Use it for working capital, equipment, inventory, buying a business or real estate.</li><li><b>504:</b> made for big fixed assets like buildings and heavy equipment, usually with a lower, fixed rate on the SBA portion.</li></ul>
<h2>What rate will I get?</h2><p>SBA rates are set by the lender but capped by SBA rules tied to the Prime Rate. Your rate depends on the loan size, term and your business's credit. Ask lenders for a quote and enter it above.</p>""")

add("business-loan-calculator", "Business", "🏦", "Business Loan Calculator", "Payment and true APR with fees",
    "Business Loan Calculator – Payment, Total Cost & True APR",
    "Free business loan calculator. See your monthly payment, total interest and the true APR after origination fees, so you can compare small business loan offers.",
    calc_box(N("amt", "Loan amount", 50000, "$", full=True) + N("rate", "Interest rate", 12, suf="%") + N("term", "Term", 36, suf="months") + N("fee", "Origination fee", 3, suf="%") +
        S("freq", "Payments", [(12, "Monthly"), (52, "Weekly"), (260, "Daily (business days)")], 12),
        APR_JS + """calc(v=>{const f=v.freq,n=Math.round(v.term/12*f);if(!(v.amt>0&&n>0))return null;const r=(v.rate||0)/100/f,p=r?v.amt*r/(1-Math.pow(1+r,-n)):v.amt/n,fee=v.amt*(v.fee||0)/100,ti=p*n-v.amt;
const mp=p*f/12,apr=f===12?trueAPR(v.amt-fee,p,n):NaN,lbl={12:"Monthly",52:"Weekly",260:"Daily"}[f];
return{big:[lbl+" payment",money(p)],sub:f!==12?"about "+money(mp,0)+" a month":"",rows:[["Total interest",money(ti,0)],["Origination fee",money(fee,0)],["Cash you actually receive",money(v.amt-fee,0)],["Total cost of borrowing",money(ti+fee,0)],["Total repaid",money(p*n,0)],...(ok(apr)?[["True APR with fees",pct(apr,2)]]:[])],chart:donut([["Principal",v.amt],["Interest",ti],["Fees",fee]].filter(x=>x[1]>0))}})"""),
    """<h2>Why the true APR matters</h2><p>Many business lenders take an origination fee out of your loan, so you receive less cash but repay the full amount. That makes the real cost higher than the interest rate. The <b>true APR</b> above includes the fee, so you can compare offers fairly.</p>
<h2>Daily and weekly payments</h2><p>Some online lenders collect payments every business day or every week. That can strain cash flow, so check the monthly equivalent before you sign.</p>
<h2>Tips for a better business loan</h2><ul><li>Compare at least three offers using the true APR, not just the rate.</li><li>Check for prepayment penalties.</li><li>SBA loans usually have the lowest rates if you qualify.</li></ul>""")

add("equipment-loan-calculator", "Business", "🚜", "Equipment Loan Calculator", "Payments for machinery, trucks & tools",
    "Equipment Loan Calculator – Equipment Financing Payments",
    "Free equipment loan calculator. Estimate monthly payments on business equipment, trucks and machinery with down payment, sales tax and a balloon payment option.",
    calc_box(N("price", "Equipment price", 85000, "$", full=True) + N("down", "Down payment", 10, suf="%") + N("tax", "Sales tax", 8.25, suf="%") +
        N("rate", "Interest rate", 9, suf="%") + S("months", "Term", [(36, "36 months"), (48, "48 months"), (60, "60 months"), (72, "72 months"), (84, "84 months")], 60) +
        N("balloon", "Balloon at end (optional)", 0, "$", full=True),
        """calc(v=>{const tx=v.price*(v.tax||0)/100,dn=v.price*(v.down||0)/100,L=v.price+tx-dn,n=v.months,r=(v.rate||0)/1200,b=v.balloon||0;if(!(L>0))return null;
const p=r?(L-b/Math.pow(1+r,n))*r/(1-Math.pow(1+r,-n)):(L-b)/n,ti=p*n+b-L;
return{big:["Monthly payment",money(p)],sub:b?"plus a "+money(b,0)+" balloon at the end":"",rows:[["Amount financed",money(L,0)],["Down payment",money(dn,0)],["Sales tax",money(tx,0)],["Total interest",money(ti,0)],["Total cost of equipment",money(p*n+b+dn,0)]],note:"Business equipment may qualify for a big first-year tax deduction (Section 179). Ask your accountant."}})"""),
    """<h2>How equipment financing works</h2><p>The equipment itself is the collateral, so equipment loans are often easier to get than other business loans. You usually put 0–20% down and repay over 2–7 years, matching how long the equipment will last.</p>
<h2>What's a balloon payment?</h2><p>A balloon lowers your monthly payment by leaving a lump sum due at the end. It's useful if you plan to sell or trade in the equipment, but make sure you can cover it when it's due.</p>""")

add("line-of-credit-calculator", "Business", "💳", "Line of Credit Calculator", "Interest and payoff time on a credit line",
    "Business Line of Credit Calculator – Interest & Payoff Time",
    "Free business line of credit calculator. See the monthly interest on what you draw, how long it takes to pay off, and the total interest you'll pay.",
    calc_box(N("bal", "Amount drawn", 25000, "$", full=True) + N("rate", "Interest rate (APR)", 14, suf="%") + N("pay", "Monthly payment", 1200, "$") + N("fee", "Draw fee (optional)", 0, suf="%", full=True),
        """calc(v=>{if(!(v.bal>0))return null;const r=(v.rate||0)/1200,io=v.bal*r,fee=v.bal*(v.fee||0)/100;if(!(v.pay>io))return{big:["Interest-only payment",money(io)],rows:[["Draw fee",money(fee)]],note:"Your payment needs to be more than "+money(io)+" to pay down the balance."};
let b=v.bal,m=0,ti=0;while(b>0&&m<600){const i=b*r;ti+=i;b=b+i-v.pay;m++}
return{big:["Paid off in",Math.floor(m/12)+" yr "+(m%12)+" mo"],sub:m+" monthly payments",rows:[["Interest-only payment",money(io)],["Total interest",money(ti,0)],["Draw fee",money(fee,0)],["Total cost of borrowing",money(ti+fee,0)]],chart:donut([["Amount drawn",v.bal],["Interest",ti],["Fees",fee]].filter(x=>x[1]>0))}})"""),
    """<h2>How a business line of credit works</h2><p>A line of credit works like a business credit card with a lower rate. You get a limit, draw only what you need, and pay interest only on what you've used. As you repay, the money becomes available again.</p>
<h2>Line of credit vs. term loan</h2><p>Use a line of credit for short-term needs like inventory, payroll gaps or seasonal swings. Use a term loan for big one-time purchases you'll pay off over years.</p>""")

PAYROLL_JS = """calc(v=>{const f=v.freq,g=v.type==="hourly"?(v.rate||0)*(v.hours||0)+(v.ot||0)*(v.rate||0)*1.5:v.amt/f;if(!(g>0)||!f)return null;
const yr=g*f,k4=g*(v.k401||0)/100,ss=g*.062,med=g*.0145,ft=fedTax(Math.max(0,yr-k4*f-TAX2026.std[v.status]),v.status).tax/f,st=g*(v.srate||0)/100,net=g-k4-ss-med-ft-st;
const futa=Math.min(g,7000/f)*.006,suta=Math.min(g,(v.sutabase||0)/f)*(v.suta||0)/100,er=ss+med+futa+suta;
return{big:["Employee net pay",money(net)],sub:"per paycheck · total cost to you "+money(g+er),rows:[["Gross pay",money(g)],["Federal income tax (est.)",money(ft)],["Social Security (employee)",money(ss)],["Medicare (employee)",money(med)],...(st?[["State income tax",money(st)]]:[]),...(k4?[["401(k)",money(k4)]]:[]),["Employer Social Security + Medicare",money(ss+med)],["Employer FUTA",money(futa)],["Employer state unemployment",money(suta)],["Total employer taxes",money(er)]],
chart:donut([["Net pay",net,"#10b981"],["Employee taxes",ss+med+ft+st,"#6366f1"],["Employer taxes",er,"#ec4899"],["401(k)",k4,"#06b6d4"]].filter(x=>x[1]>0)),note:"2026 estimate for a single paycheck early in the year. Actual withholding follows the employee's W-4 and IRS Publication 15-T."}})"""
add("payroll-calculator", "Business", "🧑‍💼", "Payroll Calculator", "Employee net pay + employer taxes",
    "Payroll Calculator 2026 – Employee Net Pay & Employer Taxes",
    "Free payroll calculator for small businesses. Work out an employee's net pay, withholding, and your employer payroll taxes (Social Security, Medicare, FUTA, SUTA) per paycheck.",
    calc_box(
        SEG("type", "Employee is paid", [("hourly", "Hourly"), ("salary", "Salary")], "hourly") +
        when("type=hourly", N("rate", "Hourly rate", 22, "$") + N("hours", "Regular hours this period", 80) + N("ot", "Overtime hours (1.5×)", 0, full=True)) +
        when("type=salary", N("amt", "Yearly salary", 55000, "$", full=True)) +
        S("freq", "Pay frequency", [(26, "Every 2 weeks"), (52, "Weekly"), (24, "Twice a month"), (12, "Monthly")], 26) +
        S("status", "Employee filing status", [("single", "Single"), ("mfj", "Married filing jointly"), ("hoh", "Head of household")], "single") +
        N("k401", "401(k) deferral", 0, suf="%") + N("srate", "State income tax rate", 0, suf="%") +
        N("suta", "Your state unemployment (SUTA) rate", 2.7, suf="%") + N("sutabase", "SUTA wage base", 9000, "$", suf="/ yr"),
        PAYROLL_JS, title="Paycheck details"),
    """<h2>How to run payroll</h2><ol><li><b>Gross pay:</b> hours × rate, with overtime at 1.5× for hours over 40 in a week, or salary ÷ pay periods.</li><li><b>Withhold from the employee:</b> federal income tax (based on their W-4), Social Security (6.2%), Medicare (1.45%), state tax and any benefits.</li><li><b>Pay employer taxes:</b> you match Social Security and Medicare, plus federal (FUTA) and state (SUTA) unemployment tax.</li></ol>
<h2>2026 payroll tax rates</h2><ul><li><b>Social Security:</b> 6.2% from the employee + 6.2% from you, on wages up to $184,500.</li><li><b>Medicare:</b> 1.45% + 1.45%, no limit. Employees also pay an extra 0.9% on wages over $200,000.</li><li><b>FUTA:</b> 0.6% on the first $7,000 per employee after the normal state credit.</li><li><b>SUTA:</b> set by your state. New employers often get a starter rate; check your state's workforce agency.</li></ul>""")

add("employer-payroll-tax-calculator", "Business", "🏢", "Employer Payroll Tax Calculator", "What you owe on top of wages",
    "Employer Payroll Tax Calculator 2026 – FICA, FUTA & SUTA",
    "Free employer payroll tax calculator. See how much you owe in Social Security, Medicare, FUTA and state unemployment tax for your employees in 2026.",
    calc_box(N("wage", "Yearly wages per employee", 50000, "$") + N("count", "Number of employees", 5) +
        N("suta", "State unemployment (SUTA) rate", 2.7, suf="%") + N("sutabase", "SUTA wage base", 9000, "$"),
        """calc(v=>{const w=v.wage||0,c=Math.max(1,Math.round(v.count||1));if(!(w>0))return null;const ss=Math.min(w,TAX2026.ssBase)*.062,med=w*.0145,futa=Math.min(w,7000)*.006,suta=Math.min(w,v.sutabase||0)*(v.suta||0)/100,per=ss+med+futa+suta;
return{big:["Employer taxes per year",money(per*c,0)],sub:money(per,0)+" per employee · "+pct(per/w*100,2)+" of wages",rows:[["Social Security (6.2%)",money(ss*c,0)],["Medicare (1.45%)",money(med*c,0)],["FUTA (0.6% of first $7,000)",money(futa*c,0)],["State unemployment",money(suta*c,0)],["Per employee, per month",money(per/12,0)],["Total payroll cost",money((w+per)*c,0)]],chart:donut([["Social Security",ss],["Medicare",med],["FUTA",futa],["SUTA",suta]].filter(x=>x[1]>0))}})"""),
    """<h2>What payroll taxes do employers pay?</h2><p>On top of wages, employers pay their half of FICA (Social Security 6.2% and Medicare 1.45%), federal unemployment tax (FUTA) and state unemployment tax (SUTA). Most small businesses pay about 8–10% of wages in employer payroll taxes.</p>
<h2>About FUTA and SUTA</h2><p>FUTA is 6.0% on the first $7,000 of each employee's wages, but most employers get a 5.4% credit for paying state unemployment tax, so the effective rate is 0.6%. Employers in a few "credit reduction" states pay a bit more. SUTA rates and wage bases are set by each state.</p>""")

add("cost-of-employee-calculator", "Business", "🧮", "Cost of an Employee Calculator", "True cost of hiring with taxes & benefits",
    "Cost of an Employee Calculator – True Cost to Hire in 2026",
    "Free cost of employee calculator. See the true yearly and hourly cost of hiring someone, including payroll taxes, health insurance, retirement match and overhead.",
    calc_box(N("wage", "Yearly salary or wages", 50000, "$", full=True) + N("health", "Health insurance (your share)", 600, "$", suf="/ mo") + N("match", "Retirement match", 3, suf="%") +
        N("wc", "Workers' comp insurance", 1.0, suf="% of pay") + N("suta", "State unemployment rate", 2.7, suf="%") + N("other", "Other benefits & perks", 1000, "$", suf="/ yr") + N("equip", "Equipment, software & space", 3000, "$", suf="/ yr") +
        N("hours", "Hours worked per year", 2080, full=True),
        """calc(v=>{const w=v.wage||0;if(!(w>0))return null;const fica=Math.min(w,TAX2026.ssBase)*.062+w*.0145,futa=Math.min(w,7000)*.006,suta=Math.min(w,9000)*(v.suta||0)/100,tax=fica+futa+suta,hl=(v.health||0)*12,mt=w*(v.match||0)/100,wc=w*(v.wc||0)/100,ben=hl+mt+wc+(v.other||0),tot=w+tax+ben+(v.equip||0);
return{big:["True yearly cost",money(tot,0)],sub:pct(tot/w*100,0)+" of their pay · "+money(tot/(v.hours||2080))+" per hour worked",rows:[["Salary / wages",money(w,0)],["Payroll taxes",money(tax,0)],["Health insurance",money(hl,0)],["Retirement match",money(mt,0)],["Workers' comp",money(wc,0)],["Other benefits",money(v.other||0,0)],["Equipment & space",money(v.equip||0,0)],["Cost per month",money(tot/12,0)]],chart:donut([["Wages",w],["Payroll taxes",tax],["Benefits",ben],["Equipment & space",v.equip||0]].filter(x=>x[1]>0)),note:"State unemployment uses a $9,000 wage base here. Check your state's actual base."}})"""),
    """<h2>How much does an employee really cost?</h2><p>A common rule of thumb is <b>1.25 to 1.4 times their salary</b>. On top of wages you pay payroll taxes, benefits like health insurance and retirement match, workers' comp insurance, and the tools and space they need to do the job.</p>
<h2>Employee vs. contractor</h2><p>Independent contractors cost less in taxes and benefits, but you can't control how and when they work like an employee. Misclassifying workers can lead to back taxes and penalties, so check the IRS rules before deciding.</p>""")

# ---------- home ----------
K = lambda k, cls="", lab=None: f'<button class="{cls}" data-k="{k}">{lab or k}</button>'
KEYS = "".join([
    K("sin(", "fn", "sin"), K("cos(", "fn", "cos"), K("tan(", "fn", "tan"), K("(", "fn"), K(")", "fn"), K("AC", "ac"),
    K("ln(", "fn", "ln"), K("log(", "fn", "log"), K("sqrt(", "fn", "√"), K("^", "fn", "xʸ"), K("!", "fn", "x!"), K("DEL", "ac", "⌫"),
    K("π", "fn"), K("7", "n"), K("8", "n"), K("9", "n"), K("/", "op", "÷"), K("%", "fn"),
    K("ℯ", "fn", "e"), K("4", "n"), K("5", "n"), K("6", "n"), K("*", "op", "×"), K("^2", "fn", "x²"),
    K("±", "fn"), K("1", "n"), K("2", "n"), K("3", "n"), K("-", "op", "−"), K("1/(", "fn", "1/x"),
    '<button class="fn" id="sci-deg">DEG</button>', K("0", "n"), K(".", "n"), K("=", "eq"), K("+", "op"), K("asin(", "fn", "sin⁻¹"),
])

CATS = [("Financial", "💰"), ("Business", "💼"), ("Math", "➗"), ("Health", "❤️"), ("Everyday", "📅")]
CAT_COL = {"Financial": ("#e0e7ff", "#4f46e5"), "Business": ("#e0f2fe", "#0284c7"), "Math": ("#fce7f3", "#db2777"), "Health": ("#dcfce7", "#16a34a"), "Everyday": ("#fef3c7", "#d97706")}

def card(c):
    bg, col = CAT_COL[c["cat"]]
    return f'<a class="card" href="{c["slug"]}" style="--bgc:{bg};--c:{col}"><div class="e">{c["emoji"]}</div><div><b>{c["name"]}</b><span>{c["card"]}</span></div></a>'

def ccard(k):
    c = CV.CATS[k]
    return f'<a class="card" href="{CV.HUB[k]}" style="--bgc:#ede9fe;--c:#7c3aed"><div class="e">{c["emoji"]}</div><div><b>{c["name"]} Converter</b><span>{", ".join(d[2] for d in list(c["units"].values())[:5])}</span></div></a>'
CONV_HTML = '<h2>🔁 Unit converters</h2><div class="grid-cards">' + '<a class="card" href="unit-converter" style="--bgc:#ede9fe;--c:#7c3aed"><div class="e">🔁</div><div><b>Unit Converter</b><span>All units in one place</span></div></a>' + "".join(ccard(k) for k in CV.CATS) + '</div><div class="cv-links" style="margin-top:12px">' + "".join(f'<a href="{s}">{n}</a>' for s, n in [("cm-to-inches", "CM to Inches"), ("kg-to-lbs", "KG to LBS"), ("celsius-to-fahrenheit", "Celsius to Fahrenheit"), ("fahrenheit-to-celsius", "Fahrenheit to Celsius"), ("inches-to-cm", "Inches to CM"), ("lbs-to-kg", "LBS to KG"), ("feet-to-meters", "Feet to Meters"), ("km-to-miles", "KM to Miles"), ("ml-to-oz", "ML to Oz"), ("cm-to-feet", "CM to Feet")]) + "</div>"
CAT_HTML = '<section class="cats">' + "".join(f'<h2>{e} {cat} calculators</h2><div class="grid-cards">' + "".join(card(c) for c in CALCS if c["cat"] == cat and not c["hidden"]) + "</div>" for cat, e in CATS) + CONV_HTML + "</section>"
POPULAR = ["paycheck-calculator", "mortgage-calculator", "percentage-calculator", "tip-calculator", "age-calculator", "gpa-calculator", "hours-calculator"]
BYSLUG = {c["slug"]: c for c in CALCS}
HOME_TOOL = f'''<div class="home"><div id="sci"><div class="screen"><div id="sci-expr"></div><div id="sci-display">0</div></div><div class="keys">{KEYS}</div></div>
<div class="side"><div class="panel"><div class="panelhead"><h2>History</h2><button class="link" id="sci-clearhist">Clear</button></div><ul class="history" id="sci-history"></ul></div>
<div class="panel"><h2>Popular</h2><div class="grid-cards" style="grid-template-columns:1fr">{"".join(card(BYSLUG[s]) for s in POPULAR[:4])}</div></div></div></div>
<script src="sci.js"></script>{CAT_HTML}'''
# x² key helper: "^2" is inserted as text, works with ^ operator

# ---------- page template ----------
UPDATED = "November 2026"
SRC = {
 "irs_brackets": ('IRS Rev. Proc. 2025-32: 2026 tax brackets & standard deduction (summary by Tax Foundation)', "https://taxfoundation.org/data/all/federal/2026-tax-brackets/"),
 "ssa_base": ("Social Security Administration: contribution and benefit base", "https://www.ssa.gov/oact/cola/cbb.html"),
 "irs_se": ("IRS Topic 554: Self-employment tax", "https://www.irs.gov/taxtopics/tc554"),
 "irs_p15": ("IRS Publication 15: Employer's Tax Guide", "https://www.irs.gov/publications/p15"),
 "irs_futa": ("IRS Topic 759: Form 940, federal unemployment (FUTA) tax", "https://www.irs.gov/taxtopics/tc759"),
 "irs_est": ("IRS: Estimated taxes", "https://www.irs.gov/faqs/estimated-tax"),
 "sba": ("U.S. Small Business Administration: loans", "https://www.sba.gov/funding-programs/loans"),
 "cfpb_dti": ("CFPB: What is a debt-to-income ratio?", "https://www.consumerfinance.gov/ask-cfpb/what-is-a-debt-to-income-ratio-en-1791/"),
 "solar": ("EnergySage: Federal solar tax credit in 2026", "https://energysage.com/solar/solar-tax-credit-explained"),
}
PAGE_SRC = {"paycheck": ["irs_brackets", "ssa_base"], "self-employment-tax-calculator": ["irs_se", "irs_brackets", "ssa_base", "irs_est"],
 "payroll-calculator": ["irs_p15", "irs_brackets", "ssa_base", "irs_futa"], "employer-payroll-tax-calculator": ["irs_p15", "ssa_base", "irs_futa"],
 "cost-of-employee-calculator": ["irs_p15", "irs_futa"], "sba-loan-calculator": ["sba"], "house-affordability-calculator": ["cfpb_dti"], "solar-panel-calculator": ["solar"]}
MONEY = {"Financial", "Business"}

def trust(slug, cat):
    if cat not in MONEY: return ""
    keys = PAGE_SRC.get("paycheck" if slug.endswith("paycheck-calculator") else slug, [])
    src = ""
    if keys:
        src = "<h2>Sources</h2><ul>" + "".join(f'<li><a href="{SRC[k][1]}" rel="nofollow noopener" target="_blank">{SRC[k][0]}</a></li>' for k in keys) + "</ul>"
    return src + f'<p class="trustline">✓ Updated {UPDATED} by <a href="about">Aaron Hernandez</a> · <a href="how-we-calculate">How we calculate</a> · Results are estimates for planning, not financial, tax or legal advice.</p>'

def page(slug, title, desc, h1, sub, tool, content, crumb=None, related=""):
    url = DOMAIN + "/" + ("" if slug == "index" else slug)
    nav_items = [("./", "All calculators", "index")] + [(s, BYSLUG[s]["name"].replace(" Calculator", ""), s) for s in ["paycheck-calculator", "mortgage-calculator", "percentage-calculator", "tip-calculator"]] + [("unit-converter", "Converters", "unit-converter")]
    nav = "".join(f'<a href="{u}"{" class=active" if k == slug else ""}>{t}</a>' for u, t, k in nav_items)
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": h1, "url": url, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@type": "Organization", "name": SITE, "url": DOMAIN, "founder": {"@type": "Person", "name": "Aaron Hernandez"}}}
    cr = f'<div class="crumbs"><a href="./">Calculators</a> › {crumb}</div>' if crumb else ""
    foot = "".join(f'<a href="{c["slug"]}">{c["name"]}</a>' for c in CALCS if not c["hidden"]) + '<a href="unit-converter">Unit Converter</a>' + "".join(f'<a href="{CV.HUB[k]}">{CV.CATS[k]["name"]} Converter</a>' for k in CV.CATS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {SITE}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#4f46e5">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='24' fill='%234f46e5'/><text x='50' y='70' font-size='60' text-anchor='middle' fill='white' font-family='Arial' font-weight='bold'>=</text></svg>">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{json.dumps(ld)}</script>
<!-- AdSense script goes here once approved -->
</head>
<body>
<header><div class="wrap topbar"><a class="logo" href="./"><span class="mark">🧮</span><span class="name">Your<em>CalculatorApp</em></span></a><nav>{nav}</nav></div></header>
<main class="wrap">
<section class="hero">{cr}<h1>{h1}</h1><p>{sub}</p><div class="trust"><span>✨ 100% free</span><span>⚡ Instant answers</span><span>🔒 Private</span><span>📱 Works on phone</span></div></section>
<script src="calc.js"></script>
{tool}
<div class="ad"></div>
<section class="content">{content}{trust(slug, crumb)}</section>
{related}
</main>
<footer><div class="wrap"><div class="foot-cols">{foot}</div>© {SITE} · Free online calculators · <a href="about">About</a> · <a href="how-we-calculate">How we calculate</a> · <a href="privacy">Privacy</a></div></footer>
</body>
</html>
"""

pages = []
pages.append(("index", page("index", "Free Online Calculator – Scientific, Math & Money Calculators",
    "Free online calculator with a full scientific keypad, plus mortgage, loan, percentage, tip, GPA, age and more. Fast, private and mobile-friendly.",
    "Free Online Calculator", "A full scientific calculator plus easy calculators for money, math, health and everyday life.", HOME_TOOL,
    """<h2>A free calculator for everything</h2><p>Use the scientific calculator above for quick math. It supports your keyboard, remembers your history and handles trig, logs, powers, roots and factorials. Need something specific? Pick a calculator below for mortgages, loans, tips, percentages, grades, GPA, dates and more.</p>
<h2>Keyboard shortcuts</h2><p>Type numbers and + − * / ^ directly. Press Enter for equals, Backspace to delete and Esc to clear.</p>""")))

for c in CALCS:
    pool = [x for x in CALCS if not x["hidden"] and x is not c]
    rel = [x for x in pool if x["cat"] == c["cat"]][:4]
    rel += [x for x in pool if x not in rel][: 6 - len(rel)]
    related = '<section class="related"><h2>Related calculators</h2><div class="grid-cards">' + "".join(card(x) for x in rel) + "</div></section>"
    pages.append((c["slug"], page(c["slug"], c["title"], c["desc"], c["name"], c["desc"].split(". ")[1] if ". " in c["desc"] else c["desc"],
                                  c["tool"], c["content"], crumb=c["cat"], related=related)))

for cp in CV.all_pages():
    pages.append((cp["slug"], page(cp["slug"], cp["title"], cp["desc"], cp["h1"], cp["sub"], cp["tool"], cp["content"], crumb="Converters")))

pages.append(("about", page("about", "About Us", f"About {SITE}: free, accurate online calculators for money, business, math and everyday life.", "About YourCalculatorApp", "Free, accurate calculators anyone can use.", "",
    f"""<h2>Our mission</h2><p>{SITE} makes free, easy calculators that give clear answers in seconds. Whether you're checking a paycheck, planning a budget, pricing a product or helping with homework, we want you to get a trustworthy number without ads getting in the way, sign-ups or confusing jargon.</p>
<h2>Who's behind it</h2><p>{SITE} is built and maintained by <b>Aaron Hernandez</b>, who creates free online tools that make everyday math, money and business questions easier. Aaron oversees every calculator on the site, keeps the tax and payroll figures up to date each year, and personally reviews reported errors.</p>
<h2>What makes our calculators different</h2><ul><li><b>Accurate and up to date:</b> money and tax tools use official 2026 figures from the IRS, the Social Security Administration and other government sources. See <a href="how-we-calculate">how we calculate</a>.</li><li><b>Tested:</b> every calculator is checked against worked examples and published figures before it goes live.</li><li><b>Private:</b> all calculations run in your browser. The numbers you enter are never sent to our servers.</li><li><b>Explained:</b> each page shows the formula and plain-English tips, so you understand the answer and not just the number.</li></ul>
<h2>Independent</h2><p>{SITE} is an independent site. We aren't affiliated with any bank, lender, tax software company or government agency. We may show ads to keep the site free, but advertisers never influence our calculations.</p>
<h2>Found a mistake? Tell us</h2><p>We fix errors fast. If a result looks wrong or a rate has changed, email us at {CONTACT} and we'll review it.</p>""")))

pages.append(("how-we-calculate", page("how-we-calculate", "How We Calculate – Methods & Sources", f"The formulas, assumptions and official sources behind every {SITE} calculator, including 2026 tax brackets and payroll tax rates.", "How We Calculate", "The formulas, assumptions and sources behind our calculators.", "",
    """<p>Our calculators are built and maintained by Aaron Hernandez. Here's how each one is made and kept accurate.</p><h2>Our process</h2><ol><li>We build each calculator from the standard formula used by lenders, accountants or the government agency involved.</li><li>We pull rates and limits from official sources and note the year they apply to.</li><li>We test results against worked examples and published figures before launch.</li><li>We review tax and payroll figures at least once a year, when the IRS and SSA publish new numbers.</li></ol>
<h2>2026 tax figures we use</h2><ul><li><b>Federal income tax brackets:</b> 10%, 12%, 22%, 24%, 32%, 35% and 37%, with 2026 thresholds from IRS Revenue Procedure 2025-32. For single filers, 12% starts above $12,400, 22% above $50,400 and 37% above $640,600.</li><li><b>Standard deduction:</b> $16,100 single, $32,200 married filing jointly, $24,150 head of household.</li><li><b>Social Security:</b> 6.2% each for employee and employer on wages up to $184,500 (the 2026 wage base).</li><li><b>Medicare:</b> 1.45% each with no limit, plus 0.9% Additional Medicare Tax on employee wages over $200,000.</li><li><b>Self-employment tax:</b> 15.3% on 92.35% of net profit, with half deductible for income tax.</li><li><b>FUTA:</b> 0.6% on the first $7,000 of each employee's wages, after the standard state credit.</li></ul>
<h2>Paycheck and payroll estimates</h2><p>Paycheck calculators annualize your pay, subtract pre-tax 401(k) and health insurance, apply the standard deduction and the 2026 brackets, then divide back to a single paycheck. Real withholding follows your W-4 and the IRS withholding tables in Publication 15-T, so your actual paycheck can differ slightly, especially if you have other income, dependents or extra withholding.</p>
<h2>Loans and mortgages</h2><p>Loan payments use the standard amortization formula: payment = principal × r ÷ (1 − (1 + r)<sup>−n</sup>). Business loan "true APR" includes upfront fees by finding the interest rate that matches the cash you actually receive to the payments you make. Home affordability uses the 28/36 debt-to-income guideline.</p>
<h2>Health calculators</h2><p>BMI uses the standard weight ÷ height² formula with adult categories. Calorie needs use the Mifflin-St Jeor equation with common activity multipliers. These are general estimates, not medical advice.</p>
<h2>Limitations</h2><p>Our calculators give estimates for planning. They don't cover every situation, such as state-specific deductions and credits, local taxes, or special loan terms. For important decisions, check with a tax professional, lender or financial advisor.</p>
<h2>Official sources</h2><ul>""" + "".join(f'<li><a href="{u}" rel="nofollow noopener" target="_blank">{n}</a></li>' for n, u in SRC.values()) + "</ul>")))

pages.append(("privacy", page("privacy", "Privacy Policy", "Privacy policy for " + SITE, "Privacy Policy", "How we handle your data.", "",
    f"""<h2>Your numbers stay on your device</h2><p>Every calculator on this site runs inside your web browser. The numbers you type are never sent to our servers or stored by us. Calculator history is saved only in your own browser.</p>
<h2>Advertising</h2><p>This site may use third-party advertising partners such as Google AdSense, which may use cookies to serve ads based on your visits to this and other websites. You can opt out of personalized advertising at <a href="https://adssettings.google.com">Google Ads Settings</a>.</p>
<h2>Contact</h2><p>Questions? Contact us at {CONTACT}.</p>""")))

PREVIEW = os.environ.get("PREVIEW")
for slug, html in pages:
    if PREVIEW:  # preview hosting needs .html links
        html = re.sub(r'href="([a-z0-9-]+)"', r'href="\1.html"', html).replace('href="./"', 'href="index.html"')
    (OUT / f"{slug}.html").write_text(html)

urls = "".join(f"<url><loc>{DOMAIN}/{'' if s == 'index' else s}</loc></url>" for s, _ in pages if s != "privacy")
(OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
print("built", len(pages), "pages")

import adready, more_content
adready.run(OUT, SITE, DOMAIN, "All calculators and converters on this site", extra=more_content.build_extra())
