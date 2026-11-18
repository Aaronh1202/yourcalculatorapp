import re, json, os, pathlib, shutil, datetime
OUT = pathlib.Path("public")
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
for f in ["style.css", "calc.js", "sci.js"]: shutil.copy("static/" + f, OUT / f)
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
def add(slug, cat, emoji, name, card, title, desc, tool, content, intro=None):
    CALCS.append(dict(slug=slug, cat=cat, emoji=emoji, name=name, card=card, title=title, desc=desc, tool=tool, content=content, intro=intro))

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

CATS = [("Financial", "💰"), ("Math", "➗"), ("Health", "❤️"), ("Everyday", "📅")]
CAT_COL = {"Financial": ("#e0e7ff", "#4f46e5"), "Math": ("#fce7f3", "#db2777"), "Health": ("#dcfce7", "#16a34a"), "Everyday": ("#fef3c7", "#d97706")}

def card(c):
    bg, col = CAT_COL[c["cat"]]
    return f'<a class="card" href="{c["slug"]}" style="--bgc:{bg};--c:{col}"><div class="e">{c["emoji"]}</div><div><b>{c["name"]}</b><span>{c["card"]}</span></div></a>'

CAT_HTML = '<section class="cats">' + "".join(f'<h2>{e} {cat} calculators</h2><div class="grid-cards">' + "".join(card(c) for c in CALCS if c["cat"] == cat) + "</div>" for cat, e in CATS) + "</section>"
POPULAR = ["mortgage-calculator", "percentage-calculator", "tip-calculator", "age-calculator", "gpa-calculator", "hours-calculator"]
BYSLUG = {c["slug"]: c for c in CALCS}
HOME_TOOL = f'''<div class="home"><div id="sci"><div class="screen"><div id="sci-expr"></div><div id="sci-display">0</div></div><div class="keys">{KEYS}</div></div>
<div class="side"><div class="panel"><div class="panelhead"><h2>History</h2><button class="link" id="sci-clearhist">Clear</button></div><ul class="history" id="sci-history"></ul></div>
<div class="panel"><h2>Popular</h2><div class="grid-cards" style="grid-template-columns:1fr">{"".join(card(BYSLUG[s]) for s in POPULAR[:4])}</div></div></div></div>
<script src="sci.js"></script>{CAT_HTML}'''
# x² key helper: "^2" is inserted as text, works with ^ operator

# ---------- page template ----------
def page(slug, title, desc, h1, sub, tool, content, crumb=None, related=""):
    url = DOMAIN + "/" + ("" if slug == "index" else slug)
    nav_items = [("./", "All calculators", "index")] + [(s, BYSLUG[s]["name"].replace(" Calculator", ""), s) for s in ["mortgage-calculator", "percentage-calculator", "tip-calculator", "age-calculator", "gpa-calculator"]]
    nav = "".join(f'<a href="{u}"{" class=active" if k == slug else ""}>{t}</a>' for u, t, k in nav_items)
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": h1, "url": url, "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    cr = f'<div class="crumbs"><a href="./">Calculators</a> › {crumb}</div>' if crumb else ""
    foot = "".join(f'<a href="{c["slug"]}">{c["name"]}</a>' for c in CALCS)
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
<div class="ad">Ad space</div>
<section class="content">{content}</section>
{related}
</main>
<footer><div class="wrap"><div class="foot-cols">{foot}</div>© {SITE} · Free online calculators · <a href="privacy">Privacy</a></div></footer>
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
    rel = [x for x in CALCS if x["cat"] == c["cat"] and x is not c][:4]
    rel += [x for x in CALCS if x not in rel and x is not c][: 6 - len(rel)]
    related = '<section class="related"><h2>Related calculators</h2><div class="grid-cards">' + "".join(card(x) for x in rel) + "</div></section>"
    pages.append((c["slug"], page(c["slug"], c["title"], c["desc"], c["name"], c["desc"].split(". ")[1] if ". " in c["desc"] else c["desc"],
                                  c["tool"], c["content"], crumb=c["cat"], related=related)))

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
