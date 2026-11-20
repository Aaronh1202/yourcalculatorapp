"""More calculators for YourCalculatorApp (Nov 20)."""


def register(add, N, S, SEG, D, calc_box):
    add("savings-calculator", "Financial", "🐷", "Savings Calculator", "See how your savings grow",
        "Savings Calculator – How Much Will My Savings Grow?",
        "Free savings calculator. Enter a starting balance, monthly deposit, interest rate and time to see your future balance and interest earned.",
        calc_box(N("start", "Starting balance", 1000, "$") + N("monthly", "Monthly deposit", 200, "$") +
                 N("rate", "Annual interest rate (APY)", 4.0, suf="%") + N("years", "Years", 10, suf="years", mn=0),
                 """calc(v=>{const y=v.years||0,r=(v.rate||0)/100/12,n=Math.round(y*12),p=v.start||0,m=v.monthly||0;if(!(n>0))return null;
let b=p;for(let i=0;i<n;i++){b=b*(1+r)+m;}const c=p+m*n;return{big:["Balance after "+num(y,1)+" years",money(b,0)],rows:[["Total deposits",money(c,0)],["Interest earned",money(b-c,0)],["Monthly deposit",money(m)]],chart:donut([["Deposits",c],["Interest",b-c]])}})"""),
        """<h2>How savings grow</h2><p>Your balance grows from two things: the money you add and the interest it earns. Because interest is added every month, you also earn interest on past interest, which is called compounding. The longer you save, the bigger that effect becomes.</p>
<h2>Example</h2><p>Saving $200 a month for 10 years with $1,000 to start at 4% APY grows to about $30,900. You put in $25,000; the other $5,900 is interest.</p>
<h2>Tips to save more</h2><ul><li>Automate a transfer on payday so saving happens first.</li><li>Keep your emergency fund in a high-yield savings account.</li><li>Raise your monthly deposit whenever you get a raise.</li></ul>""")

    add("retirement-calculator", "Financial", "🏖️", "Retirement Calculator", "Will you have enough to retire?",
        "Retirement Calculator – How Much Will I Have When I Retire?",
        "Free retirement calculator. Estimate your retirement savings from your age, current savings, monthly contributions and expected return, plus the yearly income it could provide.",
        calc_box(N("age", "Current age", 30, suf="years") + N("retire", "Retirement age", 65, suf="years") +
                 N("saved", "Current retirement savings", 20000, "$") + N("monthly", "Monthly contribution", 500, "$") +
                 N("ret", "Expected annual return", 7, suf="%") + N("wd", "Withdrawal rate in retirement", 4, suf="%"),
                 """calc(v=>{const yrs=(v.retire||0)-(v.age||0);if(!(yrs>0))return null;const r=(v.ret||0)/100/12;let b=v.saved||0;for(let i=0;i<yrs*12;i++)b=b*(1+r)+(v.monthly||0);
const c=(v.saved||0)+(v.monthly||0)*yrs*12,inc=b*(v.wd||4)/100;return{big:["Savings at age "+num(v.retire,0),money(b,0)],rows:[["Yearly income at "+num(v.wd||4,1)+"%",money(inc,0)],["Monthly income",money(inc/12,0)],["Your contributions",money(c,0)],["Investment growth",money(b-c,0)]],chart:donut([["Contributions",c],["Growth",b-c]])}})"""),
        """<h2>How this estimate works</h2><p>The calculator grows your current savings and monthly contributions at your expected annual return until retirement. It then applies a withdrawal rate to estimate how much yearly income your savings could support.</p>
<h2>The 4% rule</h2><p>A common guideline says you can withdraw about 4% of your savings in the first year of retirement, then adjust for inflation, with a good chance your money lasts 30 years. Some planners now suggest 3–3.5% to be safer.</p>
<h2>Things to keep in mind</h2><ul><li>Returns aren't guaranteed and vary year to year; 5–7% is a common long-term assumption for a stock-heavy portfolio.</li><li>Inflation means $1 in the future buys less than today.</li><li>Social Security and pensions add to your retirement income.</li></ul><p>This is an estimate, not financial advice. A licensed financial planner can help with a full plan.</p>""")

    add("simple-interest-calculator", "Financial", "➗", "Simple Interest Calculator", "Interest without compounding",
        "Simple Interest Calculator – Calculate Interest Easily",
        "Free simple interest calculator. Find the interest and total amount from principal, rate and time using I = P × r × t.",
        calc_box(N("p", "Principal", 5000, "$") + N("r", "Annual interest rate", 5, suf="%") + N("t", "Time", 3, suf="years"),
                 """calc(v=>{if(!(v.p>0))return null;const i=v.p*(v.r||0)/100*(v.t||0);return{big:["Interest",money(i)],rows:[["Total amount",money(v.p+i)],["Interest per year",money(v.p*(v.r||0)/100)]]}})"""),
        """<h2>Simple interest formula</h2><p class="formula">Interest = Principal × Rate × Time</p><p>With $5,000 at 5% for 3 years: 5,000 × 0.05 × 3 = $750 of interest, for a total of $5,750.</p>
<h2>Simple vs compound interest</h2><p>Simple interest is only charged or earned on the original amount. Compound interest also applies to interest already added, so it grows faster over time. Car loans and some personal loans use simple interest; savings accounts usually compound. Try the <a href="compound-interest-calculator">compound interest calculator</a> to compare.</p>""")

    add("credit-card-payoff-calculator", "Financial", "💳", "Credit Card Payoff Calculator", "How long to pay off your card",
        "Credit Card Payoff Calculator – How Long Will It Take?",
        "Free credit card payoff calculator. See how many months it takes to pay off your balance and how much interest you'll pay.",
        calc_box(N("bal", "Card balance", 5000, "$") + N("apr", "APR", 22.9, suf="%") + N("pay", "Monthly payment", 200, "$"),
                 """calc(v=>{if(!(v.bal>0&&v.pay>0))return null;const r=(v.apr||0)/100/12;let b=v.bal,m=0,int=0;if(v.pay<=b*r)return{big:["Payment too low","Never paid off"],rows:[["Monthly interest",money(b*r)],["Pay at least",money(b*r+1)]]};
while(b>0&&m<1200){const i=b*r;int+=i;b=b+i-v.pay;m++;}return{big:["Paid off in",Math.floor(m/12)+" yrs "+(m%12)+" mos"],rows:[["Total interest",money(int)],["Total paid",money(v.bal+int)],["Months",num(m,0)]],chart:donut([["Balance",v.bal],["Interest",int]])}})"""),
        """<h2>Why credit card debt takes so long</h2><p>Credit cards charge high interest, often 20–30% APR. If you only pay a little more than the interest each month, most of your payment goes to the card company, not your balance.</p>
<h2>Ways to pay it off faster</h2><ul><li>Pay more than the minimum: even an extra $50 a month can save hundreds in interest.</li><li>Use the avalanche method: put extra money toward the highest-APR card first.</li><li>Consider a 0% balance transfer card if you can pay it off before the promo ends.</li><li>Stop adding new charges while you pay it down.</li></ul>""")

    add("pace-calculator", "Health", "🏃", "Pace Calculator", "Running pace per mile or km",
        "Pace Calculator – Running Pace per Mile and Kilometer",
        "Free running pace calculator. Enter your distance and time to get your pace per mile and per kilometer, plus your speed.",
        calc_box(N("dist", "Distance", 3.1, full=False) + S("unit", "Unit", [("mi", "Miles"), ("km", "Kilometers")], "mi") +
                 N("h", "Hours", 0, mn=0) + N("m", "Minutes", 28, mn=0) + N("s", "Seconds", 0, mn=0),
                 """calc(v=>{const t=(v.h||0)*3600+(v.m||0)*60+(v.s||0);if(!(v.dist>0&&t>0))return null;const mi=v.unit==="km"?v.dist/1.609344:v.dist,km=mi*1.609344;
const f=x=>{x=Math.round(x);return Math.floor(x/60)+":"+String(x%60).padStart(2,"0");};return{big:["Pace per mile",f(t/mi)],rows:[["Pace per km",f(t/km)],["Speed",num(mi/(t/3600),2)+" mph · "+num(km/(t/3600),2)+" km/h"],["Distance",num(mi,2)+" mi · "+num(km,2)+" km"]]}})"""),
        """<h2>How to calculate running pace</h2><p>Pace is your time divided by distance. A 5K (3.1 miles) in 28 minutes works out to about 9:02 per mile, or 5:36 per kilometer.</p>
<h2>Common race distances</h2><ul><li><b>5K:</b> 3.1 miles</li><li><b>10K:</b> 6.2 miles</li><li><b>Half marathon:</b> 13.1 miles (21.1 km)</li><li><b>Marathon:</b> 26.2 miles (42.2 km)</li></ul>
<h2>Using pace for training</h2><p>Easy runs are usually 1–2 minutes per mile slower than race pace. Knowing your pace helps you plan workouts and set realistic race goals.</p>""")

    add("due-date-calculator", "Health", "👶", "Due Date Calculator", "Estimate your baby's due date",
        "Due Date Calculator – Estimate Your Pregnancy Due Date",
        "Free pregnancy due date calculator. Enter the first day of your last period to estimate your due date and how many weeks pregnant you are.",
        calc_box(D("lmp", "First day of last period", val="2026-06-01", full=True),
                 """calc(v=>{if(!v.lmp)return null;const l=new Date(v.lmp+"T12:00:00");if(isNaN(l))return null;const due=new Date(l.getTime()+280*864e5),now=new Date(),days=Math.floor((now-l)/864e5);
const fmt=d=>d.toLocaleDateString("en-US",{weekday:"long",month:"long",day:"numeric",year:"numeric"});const w=Math.floor(days/7),dd=days%7;
return{big:["Estimated due date",fmt(due)],rows:[["Weeks pregnant today",days>=0&&days<=300?w+" weeks "+dd+" days":"—"],["Conception (approx.)",fmt(new Date(l.getTime()+14*864e5))],["End of 1st trimester",fmt(new Date(l.getTime()+13*7*864e5))],["End of 2nd trimester",fmt(new Date(l.getTime()+27*7*864e5))]]}})"""),
        """<h2>How the due date is estimated</h2><p>Most due dates are estimated with Naegele's rule: add 280 days (40 weeks) to the first day of the last menstrual period. This assumes a 28-day cycle with ovulation around day 14.</p>
<h2>How accurate is it?</h2><p>Only about 1 in 25 babies arrive exactly on their due date. Most are born within two weeks either side. An early ultrasound can give a more accurate estimate, especially if your cycles are irregular.</p>
<p>This calculator is for general information only. Your doctor or midwife will confirm your due date.</p>""")

    add("body-fat-calculator", "Health", "📏", "Body Fat Calculator", "Estimate body fat with a tape measure",
        "Body Fat Calculator – U.S. Navy Method",
        "Free body fat calculator using the U.S. Navy tape-measure method. Enter height, neck and waist (and hip for women) to estimate body fat percentage.",
        calc_box(SEG("sex", "Sex", [("m", "Male"), ("f", "Female")], "m") + N("ht", "Height", 70, suf="in") + N("neck", "Neck", 15, suf="in") +
                 N("waist", "Waist (at navel)", 34, suf="in") + N("hip", "Hip (women)", 38, suf="in"),
                 """calc(v=>{const L=Math.log10;let bf;if(v.sex==="f"){if(!(v.waist+v.hip-v.neck>0&&v.ht>0))return null;bf=163.205*L(v.waist+v.hip-v.neck)-97.684*L(v.ht)-78.387;}else{if(!(v.waist-v.neck>0&&v.ht>0))return null;bf=86.010*L(v.waist-v.neck)-70.041*L(v.ht)+36.76;}
const c=v.sex==="f"?(bf<14?"Essential fat":bf<21?"Athletes":bf<25?"Fitness":bf<32?"Average":"Above average"):(bf<6?"Essential fat":bf<14?"Athletes":bf<18?"Fitness":bf<25?"Average":"Above average");return{big:["Body fat",pct(bf,1)],rows:[["Category",c]]}})"""),
        """<h2>How the Navy method works</h2><p>The U.S. Navy formula estimates body fat from a few tape measurements and your height. It's quick and needs no special equipment, and it's usually within a few percentage points of more expensive methods.</p>
<h2>How to measure</h2><ul><li><b>Neck:</b> just below the Adam's apple, tape sloping slightly down to the front.</li><li><b>Waist:</b> at the navel for men; at the narrowest point for women.</li><li><b>Hip (women):</b> at the widest point of the buttocks.</li></ul>
<h2>Body fat categories (American Council on Exercise)</h2><p>Men: athletes 6–13%, fitness 14–17%, average 18–24%. Women: athletes 14–20%, fitness 21–24%, average 25–31%. This is an estimate, not a medical assessment.</p>""")

    add("markup-calculator", "Business", "🏷️", "Markup Calculator", "Find selling price from cost",
        "Markup Calculator – Calculate Selling Price, Markup & Margin",
        "Free markup calculator. Enter your cost and markup percentage to get the selling price, profit and profit margin.",
        calc_box(N("cost", "Cost", 40, "$") + N("mu", "Markup", 50, suf="%"),
                 """calc(v=>{if(!(v.cost>0))return null;const p=v.cost*(1+(v.mu||0)/100),g=p-v.cost;return{big:["Selling price",money(p)],rows:[["Profit",money(g)],["Profit margin",pct(g/p*100,1)]]}})"""),
        """<h2>How markup works</h2><p class="formula">Selling price = cost × (1 + markup ÷ 100)</p><p>An item that costs $40 with a 50% markup sells for $60, a $20 profit.</p>
<h2>Markup vs margin</h2><p>Markup is profit as a percentage of cost; margin is profit as a percentage of price. In the example above, the markup is 50% but the margin is 33.3%. Use the <a href="profit-margin-calculator">profit margin calculator</a> to work backwards from a target margin.</p>
<h2>Typical markups</h2><p>Retail clothing often uses 50–100%, restaurants mark food up 200–300%, and grocery items are often 15–30%.</p>""")

    add("roi-calculator", "Business", "📈", "ROI Calculator", "Return on investment",
        "ROI Calculator – Calculate Return on Investment",
        "Free ROI calculator. Find your return on investment and annualized return from the amount invested, the amount returned and the time held.",
        calc_box(N("inv", "Amount invested", 10000, "$") + N("ret", "Amount returned", 15000, "$") + N("yrs", "Time held", 3, suf="years"),
                 """calc(v=>{if(!(v.inv>0&&v.ret>=0))return null;const g=v.ret-v.inv,roi=g/v.inv*100,ann=v.yrs>0?(Math.pow(v.ret/v.inv,1/v.yrs)-1)*100:NaN;return{big:["ROI",pct(roi,2)],rows:[["Gain or loss",money(g)],["Annualized return",pct(ann,2)]]}})"""),
        """<h2>ROI formula</h2><p class="formula">ROI = (amount returned − amount invested) ÷ amount invested × 100</p><p>Investing $10,000 and getting back $15,000 is a 50% ROI.</p>
<h2>Why annualized return matters</h2><p>A 50% return over 3 years is very different from 50% in one year. The annualized return (also called CAGR) shows the equivalent yearly growth rate, about 14.5% per year in this example, so you can compare investments held for different lengths of time.</p>""")

    add("unit-price-calculator", "Everyday", "🛒", "Unit Price Calculator", "Which size is the better deal?",
        "Unit Price Calculator – Compare Prices and Find the Best Deal",
        "Free unit price calculator. Compare two products by price per ounce, item or unit to see which one is the better deal.",
        calc_box(N("p1", "Item A price", 4.99, "$") + N("q1", "Item A size", 16, suf="units") + N("p2", "Item B price", 7.49, "$") + N("q2", "Item B size", 28, suf="units"),
                 """calc(v=>{if(!(v.p1>0&&v.q1>0&&v.p2>0&&v.q2>0))return null;const a=v.p1/v.q1,b=v.p2/v.q2,best=a<b?"Item A":a>b?"Item B":"Same price";const save=Math.abs(a-b)/Math.max(a,b)*100;
return{big:["Better deal",best],rows:[["Item A per unit",money(a,3)],["Item B per unit",money(b,3)],["Savings per unit",pct(save,1)]]}})"""),
        """<h2>How unit pricing works</h2><p>Divide the price by the size (ounces, items, rolls, loads). The lower price per unit is the better value. A 16 oz jar at $4.99 is $0.312 per ounce; a 28 oz jar at $7.49 is $0.268 per ounce, so the bigger jar is about 14% cheaper per ounce.</p>
<h2>When bigger isn't better</h2><ul><li>Sales and coupons can make the smaller size cheaper.</li><li>Only buy in bulk if you'll use it before it expires.</li><li>Compare the same units: ounces to ounces, not ounces to pounds.</li></ul>""")

    add("gas-cost-calculator", "Everyday", "⛽", "Gas Cost Calculator", "Trip fuel cost",
        "Gas Cost Calculator – How Much Will Gas Cost for My Trip?",
        "Free gas cost calculator. Enter trip distance, your car's MPG and the price of gas to estimate fuel cost, one way or round trip.",
        calc_box(N("dist", "Trip distance", 250, suf="miles") + N("mpg", "Fuel economy", 28, suf="MPG") + N("price", "Gas price", 3.25, "$", suf="/gal") +
                 SEG("trip", "Trip", [("1", "One way"), ("2", "Round trip")], "1") + N("people", "Split between", 1, suf="people", mn=1),
                 """calc(v=>{if(!(v.dist>0&&v.mpg>0&&v.price>0))return null;const d=v.dist*parseInt(v.trip||"1"),gal=d/v.mpg,c=gal*v.price,n=Math.max(1,Math.round(v.people||1));
return{big:["Gas cost",money(c)],rows:[["Gallons needed",num(gal,1)],["Total miles",num(d,0)],...(n>1?[["Per person",money(c/n)]]:[]),["Cost per mile",money(c/d,3)]]}})"""),
        """<h2>How to calculate gas cost</h2><p class="formula">Gas cost = distance ÷ MPG × price per gallon</p><p>A 250-mile trip in a car that gets 28 MPG uses about 8.9 gallons; at $3.25 a gallon that's about $29.</p>
<h2>Tips to save on gas</h2><ul><li>Keep tires properly inflated: under-inflated tires lower your MPG.</li><li>Drive at a steady speed; aggressive acceleration burns more fuel.</li><li>Highway MPG is usually higher than city MPG, so long trips often beat the window sticker's combined number.</li></ul>""")

    add("electricity-cost-calculator", "Everyday", "💡", "Electricity Cost Calculator", "What does a device cost to run?",
        "Electricity Cost Calculator – Cost to Run Any Appliance",
        "Free electricity cost calculator. Enter an appliance's watts, hours of use and your electricity rate to see the daily, monthly and yearly cost.",
        calc_box(N("w", "Power use", 1000, suf="watts") + N("hrs", "Hours used per day", 3, suf="hours") + N("rate", "Electricity rate", 0.17, "$", suf="/kWh"),
                 """calc(v=>{if(!(v.w>0&&v.hrs>=0&&v.rate>0))return null;const kwh=v.w/1000*v.hrs,d=kwh*v.rate;return{big:["Cost per month",money(d*30.42)],rows:[["Cost per day",money(d)],["Cost per year",money(d*365)],["Energy per day",num(kwh,2)+" kWh"]]}})"""),
        """<h2>How to calculate electricity cost</h2><p class="formula">Cost = watts ÷ 1,000 × hours × price per kWh</p><p>A 1,000-watt space heater running 3 hours a day uses 3 kWh. At $0.17 per kWh, that's $0.51 a day, about $15.50 a month.</p>
<h2>Where to find the numbers</h2><ul><li><b>Watts:</b> on the appliance label or in the manual.</li><li><b>Rate:</b> on your electric bill, usually in cents per kWh. The U.S. average is roughly 16–18¢.</li></ul>
<h2>Common appliances</h2><p>LED bulb ~10 W, laptop ~50 W, TV ~100 W, refrigerator ~150 W average, space heater ~1,500 W, central AC ~3,500 W.</p>""")
