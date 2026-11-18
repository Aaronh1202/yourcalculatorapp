"""Extra help content for YourCalculatorApp pages (AdSense readiness)."""
from adready import faq
import converters as CV

U = {
 "mm": "The millimeter is one thousandth of a meter. It's used for precise measurements like screw sizes, rainfall, jewelry, phone screens and engineering drawings.",
 "cm": "The centimeter is one hundredth of a meter. It's the everyday metric unit for body height, clothing sizes, paper and small objects.",
 "m": "The meter is the base unit of length in the metric system (SI), defined by the distance light travels in 1/299,792,458 of a second. Rooms, buildings, fabric and sports distances are measured in meters.",
 "km": "The kilometer equals 1,000 meters. Most countries use it for road distances, running races (5K, 10K) and maps.",
 "in": "The inch is exactly 2.54 centimeters. It's used in the US for screen sizes, TVs, lumber, tools and body measurements, and worldwide for screen and wheel sizes.",
 "ft": "The foot equals 12 inches or exactly 0.3048 meters. In the US and UK it's used for people's height, room dimensions and aircraft altitude.",
 "yd": "The yard equals 3 feet or exactly 0.9144 meters. It's used for American football fields, fabric, golf distances and landscaping materials.",
 "mi": "The mile equals 5,280 feet or about 1.609 kilometers. The US and UK use miles for road distances and speed limits.",
 "nmi": "The nautical mile equals exactly 1,852 meters, based on one minute of latitude. Ships and aircraft use it for navigation.",
 "mg": "The milligram is one thousandth of a gram. Medicine doses, vitamins and nutrition labels use milligrams.",
 "g": "The gram is one thousandth of a kilogram. Cooking recipes, food packaging and postage use grams.",
 "kg": "The kilogram is the SI base unit of mass. Body weight, groceries, luggage limits and gym weights are measured in kilograms in most of the world.",
 "t": "The metric ton (tonne) equals 1,000 kilograms. Vehicles, cargo and industrial production use tonnes.",
 "oz": "The ounce (avoirdupois) equals about 28.35 grams. In the US it's used for food portions, packaging and postage.",
 "lb": "The pound equals 16 ounces or exactly 0.45359237 kilograms. Americans use pounds for body weight, groceries and gym weights.",
 "st": "The stone equals 14 pounds (about 6.35 kg). In the UK and Ireland, body weight is often given in stones and pounds.",
 "ton": "The US (short) ton equals 2,000 pounds, about 907 kg. It's used for vehicles, freight and air-conditioner capacity in the US.",
 "c": "The Celsius scale sets 0° at the freezing point of water and 100° at its boiling point at sea level. Most of the world uses it for weather and cooking.",
 "f": "The Fahrenheit scale puts water's freezing point at 32° and boiling point at 212°. The US uses it for weather, ovens and body temperature (normal is about 98.6°F).",
 "k": "The kelvin is the SI unit of temperature used in science. It starts at absolute zero (−273.15 °C), the coldest possible temperature, and uses the same step size as Celsius.",
 "ml": "The milliliter is one thousandth of a liter, the same volume as one cubic centimeter. Medicine, drinks and recipes use milliliters.",
 "l": "The liter equals 1,000 milliliters. Bottled drinks, fuel and engine sizes are measured in liters in most countries.",
 "tsp": "The US teaspoon is about 4.93 ml (often rounded to 5 ml). It's used for small amounts of spices, baking powder and medicine.",
 "tbsp": "The US tablespoon equals 3 teaspoons, about 14.79 ml. It's used for oil, butter, sauces and dry ingredients in recipes.",
 "floz": "The US fluid ounce is about 29.57 ml. Drinks, cosmetics and liquid ingredients are labeled in fluid ounces in the US.",
 "cup": "The US cup equals 8 fluid ounces, about 236.6 ml. American recipes measure flour, sugar and liquids in cups.",
 "pt": "The US pint equals 2 cups (16 fl oz), about 473 ml. Milk, beer and ice cream are often sold in pints.",
 "qt": "The US quart equals 2 pints or 4 cups, about 946 ml.",
 "gal": "The US gallon equals 4 quarts or 128 fluid ounces, about 3.785 liters. Gas, milk and paint are sold by the gallon in the US.",
 "m3": "The cubic meter is the SI unit of volume, equal to 1,000 liters. Water usage, concrete and shipping volume use cubic meters.",
 "ft3": "The cubic foot is about 28.32 liters. Refrigerators, storage units and natural gas are measured in cubic feet in the US.",
 "cm2": "The square centimeter is the area of a 1 cm × 1 cm square, used for small surfaces.",
 "m2": "The square meter is the SI unit of area. Apartments, rooms and flooring are measured in square meters in most countries.",
 "km2": "The square kilometer equals 1,000,000 square meters. Countries, cities and lakes are measured in square kilometers.",
 "ha": "The hectare equals 10,000 square meters (100 m × 100 m), about 2.47 acres. Farmland and forests are measured in hectares.",
 "in2": "The square inch is the area of a 1 in × 1 in square, used for small surfaces and pressure (pounds per square inch).",
 "ft2": "The square foot is the standard unit for home and office floor area in the US.",
 "yd2": "The square yard equals 9 square feet. Carpet and turf are often sold by the square yard.",
 "ac": "The acre equals 43,560 square feet, about 4,047 square meters. US land and property lots are measured in acres.",
 "mi2": "The square mile equals 640 acres, about 2.59 square kilometers.",
 "ms": "Meters per second is the SI unit of speed, used in science and for wind speed.",
 "kmh": "Kilometers per hour is the speed unit on road signs and speedometers in most countries.",
 "mph": "Miles per hour is used for speed limits and car speedometers in the US and UK.",
 "kn": "The knot is one nautical mile per hour, used by ships, aircraft and for wind speed in weather forecasts.",
 "fts": "Feet per second is used in US engineering, ballistics and sports science.",
 "s": "The second is the SI base unit of time, defined by the vibrations of cesium atoms in atomic clocks.",
 "min": "A minute equals 60 seconds.",
 "h": "An hour equals 60 minutes or 3,600 seconds.",
 "d": "A day equals 24 hours, the time Earth takes to rotate once relative to the Sun.",
 "wk": "A week equals 7 days.",
 "mo": "A month here is an average calendar month of about 30.44 days (one twelfth of 365.25 days). Real months range from 28 to 31 days.",
 "yr": "A year here is 365.25 days on average, accounting for leap years.",
 "bit": "A bit is the smallest unit of digital data: a single 0 or 1. Internet speeds are measured in bits per second (Mbps).",
 "B": "A byte is 8 bits, enough to store one basic text character. File sizes are measured in bytes.",
 "KB": "A kilobyte is 1,000 bytes (decimal). Small documents and images are measured in kilobytes.",
 "MB": "A megabyte is 1,000,000 bytes. Photos, songs and apps are typically measured in megabytes.",
 "GB": "A gigabyte is 1,000,000,000 bytes. Phone storage, RAM and data plans are measured in gigabytes.",
 "TB": "A terabyte is 1,000 gigabytes. Hard drives and cloud storage plans are measured in terabytes.",
 "KiB": "A kibibyte is 1,024 bytes (binary). Operating systems sometimes show sizes in binary units.",
 "MiB": "A mebibyte is 1,048,576 bytes (1,024 KiB).",
 "GiB": "A gibibyte is 1,073,741,824 bytes. Windows labels these as \"GB\", which is why a 1 TB drive shows about 931 GB.",
}
U_TIME_MS = "A millisecond is one thousandth of a second, used for reaction times, computer timing and audio."

CAT = {
 "length": "Length is measured in two main systems. The metric system (millimeters, centimeters, meters, kilometers) is used by almost every country and all of science. The US customary system (inches, feet, yards, miles) is used in the United States for everyday measurements. Since 1959 the inch has been defined as exactly 2.54 cm, so conversions between the two systems are exact.",
 "weight": "Strictly speaking, grams and pounds measure mass, while weight is the force of gravity on that mass, but in everyday life the words are used interchangeably. The metric system uses grams and kilograms; the US uses ounces and pounds, and the UK still uses stones for body weight. The pound is defined as exactly 0.45359237 kg.",
 "temperature": "Unlike other units, temperature scales don't start at the same zero, so you can't convert by multiplying alone: you also have to add or subtract an offset. The formulas are °F = °C × 9/5 + 32, °C = (°F − 32) × 5/9 and K = °C + 273.15. A useful landmark: −40° is the same in Celsius and Fahrenheit.",
 "volume": "Volume conversions come up all the time in cooking and shopping. Note that US and UK (imperial) units differ: a US gallon is 3.785 liters but an imperial gallon is 4.546 liters, and a US cup (236.6 ml) is a little smaller than a metric cup (250 ml). This converter uses US units.",
 "area": "Area is length squared, so area conversion factors are the length factor squared: 1 foot = 0.3048 m, so 1 square foot = 0.3048² = 0.0929 m². For land, the US uses acres and most other countries use hectares.",
 "speed": "Speed is distance divided by time. Road signs use km/h or mph, science uses meters per second, and ships, planes and weather reports use knots. To roughly convert km/h to mph, multiply by 0.6; for mph to km/h, multiply by 1.6.",
 "time": "Time units are the same worldwide, but conversions involving months and years are averages, because months have 28–31 days and leap years have 366 days. For exact date differences, use the Date Calculator.",
 "data": "There are two ways to count data. Storage makers use decimal units where 1 GB = 1,000,000,000 bytes. Operating systems like Windows often use binary units where 1 GiB = 1,073,741,824 bytes but still label them \"GB\". That's why a new 1 TB drive shows about 931 GB in Windows. Internet speeds use bits, not bytes: 100 Mbps is 12.5 MB per second.",
}

def _u(cat, key):
    if cat == "time" and key == "ms": return U_TIME_MS
    return U.get(key, "")

def pair_extra(cat, a, b, title):
    units = CV.CATS[cat]["units"]
    na = units[a][0] if isinstance(units[a], (list, tuple)) else units[a]
    nb = units[b][0] if isinstance(units[b], (list, tuple)) else units[b]
    return (f"<h2>About the units</h2><p><b>{na[0].upper()+na[1:]}:</b> {_u(cat, a)}</p><p><b>{nb[0].upper()+nb[1:]}:</b> {_u(cat, b)}</p>"
            f"<h2>{CV.CATS[cat]['name']} conversion basics</h2><p>{CAT[cat]}</p>")

def hub_extra(cat):
    return (f"<h2>Understanding {CV.CATS[cat]['name'].lower()} units</h2><p>{CAT[cat]}</p>"
            + faq([("Is this converter accurate?", "Yes. It uses the official definitions of each unit and shows up to 7 significant digits. Results are calculated instantly in your browser."),
                   ("Can I use it on my phone?", "Yes, it works on any phone, tablet or computer with no app needed.")]))

CALC = {
 "fraction-calculator": """<h2>Multiplying and dividing fractions</h2><p><b>Multiplying:</b> multiply the tops and multiply the bottoms (2/3 × 3/4 = 6/12 = 1/2). <b>Dividing:</b> flip the second fraction and multiply (1/2 ÷ 1/4 = 1/2 × 4/1 = 2). You don't need a common denominator for either.</p>
<h2>Simplifying fractions</h2><p>Divide the numerator and denominator by their greatest common divisor. For 18/24 the GCD is 6, so it simplifies to 3/4. Results here are always shown in simplest form, along with the mixed number and decimal.</p>""",
 "age-calculator": """<h2>Ages that matter</h2><p>In the US, common milestone ages include 16 (driver's license in most states), 18 (voting), 21 (legal drinking age), 26 (the last year to stay on a parent's health insurance), 59½ (penalty-free retirement account withdrawals), 62 (earliest Social Security) and 65 (Medicare).</p>
<h2>Leap year birthdays</h2><p>If you were born on February 29, you officially turn a year older on February 28 or March 1 in non-leap years, depending on the country's law. The calculator counts full calendar days, so leap years are always handled correctly.</p>""",
 "bmi-calculator": """<h2>What BMI means</h2><p>Body Mass Index is weight in kilograms divided by height in meters squared. For adults, the CDC and WHO categories are: under 18.5 underweight, 18.5–24.9 healthy weight, 25–29.9 overweight and 30 or more obese.</p>
<h2>Limitations of BMI</h2><p>BMI is a quick screening number, not a diagnosis. It doesn't distinguish muscle from fat, so athletes can show as overweight, and it doesn't account for age, sex or body shape. Waist size and a doctor's assessment give a fuller picture. BMI for children and teens uses age-based percentiles instead.</p>""",
 "date-calculator": """<h2>Common uses</h2><p>Count days until a vacation, wedding or due date, work out the length of a project or lease, check how many days are left in a return or refund window, or find a deadline like 30, 60 or 90 days from today.</p>
<h2>Counting inclusively</h2><p>From Monday to Friday is 4 days apart, but 5 days if you count both the first and last day. Hotel nights and loan interest usually exclude one end; event durations and leave days often include both.</p>""",
 "hours-calculator": """<h2>Converting minutes to decimal hours</h2><p>Payroll systems usually need decimal hours: divide the minutes by 60. 7 hours 45 minutes = 7 + 45/60 = 7.75 hours. Handy values: 15 minutes = 0.25, 30 minutes = 0.5 and 45 minutes = 0.75.</p>
<h2>Overtime</h2><p>Under the US Fair Labor Standards Act, non-exempt employees must be paid at least 1.5 times their regular rate for hours over 40 in a workweek. Some states, like California, also require daily overtime.</p>""",
 "average-calculator": """<h2>What standard deviation tells you</h2><p>Standard deviation measures how spread out the numbers are. A small value means most numbers sit close to the average; a large value means they vary a lot. Two classes can both average 75 on a test, but one with a standard deviation of 3 had very similar scores, while one with 15 had a wide mix of high and low scores.</p>
<h2>Weighted averages</h2><p>When some values count more than others (like a final exam worth 50% of a grade), multiply each value by its weight, add them up and divide by the total weight. Use the Grade Calculator for weighted class grades.</p>""",
 "tip-calculator": """<h2>Tipping in different situations</h2><p>Delivery drivers commonly get 15–20% (at least $3–5), hair stylists and barbers 15–20%, taxi and rideshare drivers 15–20%, and hotel housekeeping $2–5 per night. Tipping customs vary a lot between countries: in much of Europe and Japan, service is included and large tips aren't expected.</p>
<h2>Tip before or after tax?</h2><p>Etiquette experts generally say to tip on the pre-tax amount, but many people tip on the total for simplicity. The difference is usually small.</p>""" + faq([("How do I split the bill fairly?", "Enter the number of people and the calculator divides the total including tip. Use rounding to make paying with cash easier.")]),
 "grade-calculator": """<h2>How weighted grades work</h2><p>Many classes weight categories differently, for example homework 20%, quizzes 30% and the final exam 50%. Your overall grade is each category score times its weight, added together. A 90 on homework, 80 on quizzes and 70 on the final gives 0.2×90 + 0.3×80 + 0.5×70 = 77.</p>
<h2>What do I need on the final?</h2><p>Work backwards: subtract the points you've already earned from your target grade and divide by the final's weight. This shows whether your goal is still within reach.</p>""",
 "percentage-calculator": """<h2>Common percentage formulas</h2><p><b>X% of Y:</b> Y × X ÷ 100 (20% of 50 = 10). <b>X is what % of Y:</b> X ÷ Y × 100 (15 is 30% of 50). <b>Percentage change:</b> (new − old) ÷ old × 100 (from 80 to 100 is a 25% increase).</p>
<h2>Percentage points vs percent</h2><p>If an interest rate goes from 4% to 5%, it rose by one percentage point, but by 25 percent. News reports often mix these up.</p>""",
 "discount-calculator": """<h2>How discounts are calculated</h2><p>Sale price = original price × (1 − discount ÷ 100). A $80 item at 25% off costs $80 × 0.75 = $60, saving $20.</p>
<h2>Stacked discounts</h2><p>Two discounts don't simply add up. 20% off followed by an extra 10% off is 0.8 × 0.9 = 0.72 of the price, a 28% total discount, not 30%.</p>""",
 "compound-interest-calculator": """<h2>How compound interest works</h2><p>Compound interest is interest earned on both your original money and the interest it has already earned. Over time this snowballs: $10,000 at 7% a year grows to about $19,672 in 10 years and $76,123 in 30 years without adding anything.</p>
<h2>The Rule of 72</h2><p>Divide 72 by the annual interest rate to estimate how many years it takes to double your money. At 6%, money doubles in about 12 years; at 9%, about 8 years. Regular monthly contributions speed this up dramatically.</p>""",
 "salary-calculator": """<h2>Converting hourly pay to salary</h2><p>A full-time year is usually counted as 40 hours × 52 weeks = 2,080 hours. So $20 an hour is about $41,600 a year, and a $60,000 salary is about $28.85 an hour.</p>
<h2>Gross vs take-home pay</h2><p>These figures are gross pay before taxes. Federal and state income tax, Social Security and Medicare (7.65% combined) and benefits reduce your take-home pay. Use the Paycheck Calculator for an estimate after taxes.</p>""",
 "loan-calculator": """<h2>How loan payments are calculated</h2><p>Most personal and auto loans are amortized: you pay the same amount every month, but early payments are mostly interest and later payments mostly principal. The payment depends on the loan amount, interest rate and term.</p>
<h2>How to pay less interest</h2><p>A shorter term means higher payments but much less total interest. Extra payments toward principal shorten the loan and cut interest. Improving your credit score before borrowing can lower your rate.</p>""",
 "line-of-credit-calculator": """<h2>How a line of credit works</h2><p>A line of credit lets you borrow up to a limit, repay and borrow again. You only pay interest on the amount you've actually drawn. Home equity lines (HELOCs) and business lines of credit usually have variable rates tied to the prime rate.</p>
<h2>Interest-only vs repayment</h2><p>During the draw period many lines only require interest payments, which keeps payments low but doesn't reduce the balance. Paying extra toward principal saves interest.</p>""",
 "sales-tax-calculator": """<h2>How sales tax works</h2><p>In the US, sales tax is added at checkout and set by states, counties and cities. Combined rates range from 0% in states like Oregon and Delaware to over 9% in parts of Tennessee, Louisiana and Washington.</p>
<h2>Removing tax from a total</h2><p>To find the price before tax, divide the total by 1 plus the tax rate. A $107 total with 7% tax: $107 ÷ 1.07 = $100.</p>""",
 "break-even-calculator": """<h2>What is the break-even point?</h2><p>The break-even point is the number of units you must sell for revenue to cover all costs. Formula: fixed costs ÷ (price per unit − variable cost per unit). The difference between price and variable cost is called the contribution margin.</p>
<h2>Example</h2><p>With $6,000 in monthly fixed costs, a $25 price and a $10 variable cost, you break even at 6,000 ÷ 15 = 400 units a month. Every unit after that adds $15 of profit.</p>""",
 "equipment-loan-calculator": """<h2>Equipment financing basics</h2><p>Equipment loans use the equipment itself as collateral, which often makes them easier to qualify for than unsecured loans. Terms usually match the useful life of the equipment, often 2–7 years.</p>
<h2>Loan vs lease</h2><p>A loan means you own the equipment and may be able to deduct depreciation (Section 179 in the US). A lease has lower payments and is easier to upgrade, but you don't build ownership.</p>""",
 "auto-loan-calculator": """<h2>What affects your car payment</h2><p>The price, down payment, trade-in value, sales tax, interest rate and loan length all change your monthly payment. Longer loans (72–84 months) lower the payment but cost much more in interest and increase the risk of owing more than the car is worth.</p>
<h2>The 20/4/10 rule</h2><p>A popular guideline: put at least 20% down, finance for no more than 4 years, and keep total car costs under 10% of your gross income.</p>""",
 "calorie-calculator": """<h2>How daily calories are estimated</h2><p>The calculator uses the Mifflin-St Jeor equation to estimate your basal metabolic rate (BMR), the calories your body burns at rest, then multiplies it by an activity factor to estimate your total daily energy expenditure (TDEE).</p>
<h2>Using the result</h2><p>Eating around your TDEE maintains weight. These are estimates: individual metabolism varies, so track how your weight changes over a few weeks and adjust. For medical or significant diet changes, talk to a doctor or registered dietitian.</p>""",
 "budget-calculator": """<h2>The 50/30/20 budget rule</h2><p>A simple way to plan: spend about 50% of take-home pay on needs (housing, groceries, utilities, insurance, minimum payments), 30% on wants (dining out, entertainment, travel) and put 20% toward savings and paying off debt.</p>
<h2>Budgeting tips</h2><p>Track your spending for a month to see where money really goes. Automate savings on payday. Build an emergency fund of 3–6 months of expenses before investing heavily.</p>""",
 "debt-payoff-calculator": """<h2>Avalanche vs snowball</h2><p>The <b>avalanche</b> method pays extra toward the highest-interest debt first, which saves the most money. The <b>snowball</b> method pays off the smallest balance first for quick wins that keep you motivated. Both work if you stick with them.</p>
<h2>Speed up payoff</h2><p>Even an extra $50–100 a month can cut years off credit card debt. Consider a balance transfer or consolidation loan if it lowers your interest rate.</p>""",
 "business-loan-calculator": """<h2>Types of business loans</h2><p>Common options include term loans, SBA loans, lines of credit, equipment financing and merchant cash advances. Bank and SBA loans usually offer the lowest rates; online lenders are faster but more expensive.</p>
<h2>What lenders look at</h2><p>Time in business, annual revenue, personal and business credit scores, cash flow and collateral. A debt service coverage ratio of at least 1.25 is often required.</p>""",
 "profit-margin-calculator": """<h2>Margin vs markup</h2><p><b>Margin</b> is profit as a percentage of the selling price. <b>Markup</b> is profit as a percentage of the cost. An item that costs $60 and sells for $100 has a 40% margin but a 66.7% markup. Mixing them up is a common pricing mistake.</p>
<h2>Gross vs net margin</h2><p>Gross margin only subtracts the cost of goods. Net margin subtracts all expenses, including rent, salaries and taxes.</p>""",
 "employer-payroll-tax-calculator": """<h2>Employer payroll taxes in the US</h2><p>Employers pay 6.2% Social Security (up to the annual wage base) and 1.45% Medicare on each employee's wages, plus federal unemployment tax (FUTA) and state unemployment insurance (SUTA). These are on top of the employee's gross pay.</p>""",
 "house-affordability-calculator": """<h2>How much house can I afford?</h2><p>Lenders look at your debt-to-income (DTI) ratio. A common guideline is the 28/36 rule: housing costs under 28% of gross monthly income and total debt payments under 36%. Your down payment, interest rate, property taxes and insurance also change the price you can afford.</p>""",
 "cost-of-employee-calculator": """<h2>The true cost of an employee</h2><p>An employee typically costs 1.25 to 1.4 times their salary once payroll taxes, health insurance, retirement contributions, paid time off, equipment and training are included.</p>""",
}

def build_extra():
    ex = dict(CALC)
    for p in CV.PAIRS:
        ex[p[0]] = pair_extra(p[1], p[2], p[3], p[4])
    hubs = {"length": "length-converter", "weight": "weight-converter", "temperature": "temperature-converter",
            "volume": "volume-converter", "area": "area-converter", "speed": "speed-converter",
            "time": "time-converter", "data": "data-storage-converter"}
    for cat, slug in hubs.items():
        ex[slug] = hub_extra(cat)
    return ex
