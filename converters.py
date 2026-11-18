# Unit converter data + page generation for YourCalculatorApp
import json, math

# unit: id -> (singular, plural, symbol, factor to base)  (temperature handled separately)
CATS = {
 "length": dict(name="Length", emoji="📏", base="m", units={
   "mm": ("millimeter", "millimeters", "mm", 0.001), "cm": ("centimeter", "centimeters", "cm", 0.01), "m": ("meter", "meters", "m", 1),
   "km": ("kilometer", "kilometers", "km", 1000), "in": ("inch", "inches", "in", 0.0254), "ft": ("foot", "feet", "ft", 0.3048),
   "yd": ("yard", "yards", "yd", 0.9144), "mi": ("mile", "miles", "mi", 1609.344), "nmi": ("nautical mile", "nautical miles", "nmi", 1852)}),
 "weight": dict(name="Weight", emoji="⚖️", base="kg", units={
   "mg": ("milligram", "milligrams", "mg", 1e-6), "g": ("gram", "grams", "g", 0.001), "kg": ("kilogram", "kilograms", "kg", 1),
   "t": ("metric ton", "metric tons", "t", 1000), "oz": ("ounce", "ounces", "oz", 0.028349523125), "lb": ("pound", "pounds", "lb", 0.45359237),
   "st": ("stone", "stone", "st", 6.35029318), "ton": ("US ton", "US tons", "ton", 907.18474)}),
 "temperature": dict(name="Temperature", emoji="🌡️", base="c", units={
   "c": ("degree Celsius", "degrees Celsius", "°C", None), "f": ("degree Fahrenheit", "degrees Fahrenheit", "°F", None), "k": ("kelvin", "kelvins", "K", None)}),
 "volume": dict(name="Volume", emoji="🧪", base="l", units={
   "ml": ("milliliter", "milliliters", "mL", 0.001), "l": ("liter", "liters", "L", 1), "tsp": ("teaspoon", "teaspoons", "tsp", 0.00492892159375),
   "tbsp": ("tablespoon", "tablespoons", "tbsp", 0.01478676478125), "floz": ("fluid ounce", "fluid ounces", "fl oz", 0.0295735295625),
   "cup": ("cup", "cups", "cup", 0.2365882365), "pt": ("pint", "pints", "pt", 0.473176473), "qt": ("quart", "quarts", "qt", 0.946352946),
   "gal": ("gallon", "gallons", "gal", 3.785411784), "m3": ("cubic meter", "cubic meters", "m³", 1000), "ft3": ("cubic foot", "cubic feet", "ft³", 28.316846592)}),
 "area": dict(name="Area", emoji="🗺️", base="m2", units={
   "cm2": ("square centimeter", "square centimeters", "cm²", 1e-4), "m2": ("square meter", "square meters", "m²", 1), "km2": ("square kilometer", "square kilometers", "km²", 1e6),
   "ha": ("hectare", "hectares", "ha", 1e4), "in2": ("square inch", "square inches", "in²", 0.00064516), "ft2": ("square foot", "square feet", "ft²", 0.09290304),
   "yd2": ("square yard", "square yards", "yd²", 0.83612736), "ac": ("acre", "acres", "ac", 4046.8564224), "mi2": ("square mile", "square miles", "mi²", 2589988.110336)}),
 "speed": dict(name="Speed", emoji="🚀", base="ms", units={
   "ms": ("meter per second", "meters per second", "m/s", 1), "kmh": ("kilometer per hour", "kilometers per hour", "km/h", 1 / 3.6),
   "mph": ("mile per hour", "miles per hour", "mph", 0.44704), "kn": ("knot", "knots", "kn", 1852 / 3600), "fts": ("foot per second", "feet per second", "ft/s", 0.3048)}),
 "time": dict(name="Time", emoji="⏱️", base="s", units={
   "ms": ("millisecond", "milliseconds", "ms", 0.001), "s": ("second", "seconds", "s", 1), "min": ("minute", "minutes", "min", 60), "h": ("hour", "hours", "h", 3600),
   "d": ("day", "days", "d", 86400), "wk": ("week", "weeks", "wk", 604800), "mo": ("month", "months", "mo", 2629746), "yr": ("year", "years", "yr", 31556952)}),
 "data": dict(name="Data Storage", emoji="💾", base="B", units={
   "bit": ("bit", "bits", "bit", 0.125), "B": ("byte", "bytes", "B", 1), "KB": ("kilobyte", "kilobytes", "KB", 1e3), "MB": ("megabyte", "megabytes", "MB", 1e6),
   "GB": ("gigabyte", "gigabytes", "GB", 1e9), "TB": ("terabyte", "terabytes", "TB", 1e12), "KiB": ("kibibyte", "kibibytes", "KiB", 1024),
   "MiB": ("mebibyte", "mebibytes", "MiB", 1024 ** 2), "GiB": ("gibibyte", "gibibytes", "GiB", 1024 ** 3)}),
}
HUB = {"length": "length-converter", "weight": "weight-converter", "temperature": "temperature-converter", "volume": "volume-converter",
       "area": "area-converter", "speed": "speed-converter", "time": "time-converter", "data": "data-storage-converter"}

# (slug, category, from, to, display name for title, value set)
STD = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100]
PAIRS = [
 ("cm-to-inches", "length", "cm", "in", "CM to Inches", STD + [150, 200]),
 ("inches-to-cm", "length", "in", "cm", "Inches to CM", STD),
 ("mm-to-inches", "length", "mm", "in", "MM to Inches", [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]),
 ("inches-to-mm", "length", "in", "mm", "Inches to MM", [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12]),
 ("cm-to-feet", "length", "cm", "ft", "CM to Feet", [100, 120, 140, 150, 152, 155, 157, 160, 163, 165, 168, 170, 173, 175, 178, 180, 183, 185, 188, 190, 193, 200]),
 ("feet-to-cm", "length", "ft", "cm", "Feet to CM", [1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8, 10]),
 ("meters-to-feet", "length", "m", "ft", "Meters to Feet", STD),
 ("feet-to-meters", "length", "ft", "m", "Feet to Meters", STD + [200, 500, 1000]),
 ("km-to-miles", "length", "km", "mi", "KM to Miles", [1, 2, 3, 5, 8, 10, 15, 20, 21.0975, 25, 30, 42.195, 50, 80, 100, 160, 200, 500, 1000]),
 ("miles-to-km", "length", "mi", "km", "Miles to KM", [1, 2, 3, 5, 6.2, 10, 13.1, 15, 20, 26.2, 30, 50, 60, 100, 200, 500]),
 ("feet-to-inches", "length", "ft", "in", "Feet to Inches", STD),
 ("inches-to-feet", "length", "in", "ft", "Inches to Feet", [6, 12, 18, 24, 30, 36, 40, 48, 50, 60, 66, 70, 72, 80, 84, 96, 100, 120, 144]),
 ("meters-to-yards", "length", "m", "yd", "Meters to Yards", STD + [200, 400, 800, 1500]),
 ("yards-to-meters", "length", "yd", "m", "Yards to Meters", STD),
 ("meters-to-inches", "length", "m", "in", "Meters to Inches", [0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 10]),
 ("inches-to-meters", "length", "in", "m", "Inches to Meters", STD),
 ("cm-to-mm", "length", "cm", "mm", "CM to MM", STD),
 ("mm-to-cm", "length", "mm", "cm", "MM to CM", [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 150, 200, 500, 1000]),
 ("cm-to-meters", "length", "cm", "m", "CM to Meters", [1, 10, 25, 50, 75, 100, 120, 150, 160, 170, 180, 200, 250, 500, 1000]),
 ("meters-to-cm", "length", "m", "cm", "Meters to CM", [0.01, 0.1, 0.25, 0.5, 1, 1.5, 1.6, 1.7, 1.75, 1.8, 2, 3, 5, 10]),
 ("feet-to-yards", "length", "ft", "yd", "Feet to Yards", STD),
 ("yards-to-feet", "length", "yd", "ft", "Yards to Feet", STD),
 ("miles-to-feet", "length", "mi", "ft", "Miles to Feet", [0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10]),
 ("km-to-meters", "length", "km", "m", "KM to Meters", [0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5, 10, 21.1, 42.2]),
 ("kg-to-lbs", "weight", "kg", "lb", "KG to LBS", STD + [45, 55, 60, 65, 70, 80, 90, 150, 200]),
 ("lbs-to-kg", "weight", "lb", "kg", "LBS to KG", STD + [110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 220, 250, 300]),
 ("grams-to-ounces", "weight", "g", "oz", "Grams to Ounces", [1, 5, 10, 25, 50, 100, 125, 150, 200, 250, 300, 400, 454, 500, 750, 1000]),
 ("ounces-to-grams", "weight", "oz", "g", "Ounces to Grams", [0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 32]),
 ("ounces-to-pounds", "weight", "oz", "lb", "Ounces to Pounds", [1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 100]),
 ("pounds-to-ounces", "weight", "lb", "oz", "Pounds to Ounces", [0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 10]),
 ("grams-to-pounds", "weight", "g", "lb", "Grams to Pounds", [50, 100, 200, 250, 300, 454, 500, 750, 1000, 1500, 2000, 2500, 5000]),
 ("pounds-to-grams", "weight", "lb", "g", "Pounds to Grams", [0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10]),
 ("kg-to-grams", "weight", "kg", "g", "KG to Grams", [0.1, 0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 5, 10]),
 ("grams-to-kg", "weight", "g", "kg", "Grams to KG", [1, 10, 50, 100, 250, 500, 750, 1000, 1500, 2000, 5000]),
 ("stone-to-lbs", "weight", "st", "lb", "Stone to LBS", [1, 2, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20]),
 ("stone-to-kg", "weight", "st", "kg", "Stone to KG", [1, 2, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20]),
 ("kg-to-stone", "weight", "kg", "st", "KG to Stone", [40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120]),
 ("mg-to-grams", "weight", "mg", "g", "MG to Grams", [1, 5, 10, 50, 100, 200, 250, 500, 750, 1000, 2000, 5000]),
 ("tons-to-pounds", "weight", "ton", "lb", "Tons to Pounds", [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10, 20]),
 ("celsius-to-fahrenheit", "temperature", "c", "f", "Celsius to Fahrenheit", [-40, -30, -20, -10, -5, 0, 5, 10, 15, 20, 22, 25, 30, 35, 37, 38, 40, 50, 100, 180, 200]),
 ("fahrenheit-to-celsius", "temperature", "f", "c", "Fahrenheit to Celsius", [-40, -10, 0, 10, 20, 32, 40, 50, 60, 68, 70, 72, 75, 80, 90, 98.6, 100, 212, 350, 400]),
 ("celsius-to-kelvin", "temperature", "c", "k", "Celsius to Kelvin", [-273.15, -100, -40, -20, 0, 10, 20, 25, 37, 50, 100, 200, 500, 1000]),
 ("kelvin-to-celsius", "temperature", "k", "c", "Kelvin to Celsius", [0, 100, 200, 250, 273.15, 280, 290, 300, 310, 350, 373.15, 500, 1000]),
 ("fahrenheit-to-kelvin", "temperature", "f", "k", "Fahrenheit to Kelvin", [-459.67, -40, 0, 32, 50, 68, 98.6, 100, 212, 500]),
 ("ml-to-oz", "volume", "ml", "floz", "ML to Oz", [5, 10, 15, 30, 50, 60, 75, 100, 120, 150, 200, 250, 300, 355, 400, 500, 750, 1000]),
 ("oz-to-ml", "volume", "floz", "ml", "Oz to ML", [0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 64]),
 ("liters-to-gallons", "volume", "l", "gal", "Liters to Gallons", [1, 2, 3, 4, 5, 10, 15, 20, 25, 40, 50, 60, 75, 100, 200, 1000]),
 ("gallons-to-liters", "volume", "gal", "l", "Gallons to Liters", [0.5, 1, 2, 3, 4, 5, 10, 12, 15, 20, 50, 100]),
 ("cups-to-ml", "volume", "cup", "ml", "Cups to ML", [0.125, 0.25, 0.333, 0.5, 0.667, 0.75, 1, 1.5, 2, 3, 4]),
 ("ml-to-cups", "volume", "ml", "cup", "ML to Cups", [30, 50, 60, 100, 120, 150, 200, 240, 250, 300, 400, 500, 750, 1000]),
 ("cups-to-oz", "volume", "cup", "floz", "Cups to Oz", [0.25, 0.333, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8]),
 ("oz-to-cups", "volume", "floz", "cup", "Oz to Cups", [1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64]),
 ("tablespoons-to-teaspoons", "volume", "tbsp", "tsp", "Tablespoons to Teaspoons", [0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 16]),
 ("teaspoons-to-tablespoons", "volume", "tsp", "tbsp", "Teaspoons to Tablespoons", [0.5, 1, 1.5, 2, 3, 4, 5, 6, 9, 12]),
 ("tablespoons-to-cups", "volume", "tbsp", "cup", "Tablespoons to Cups", [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 32]),
 ("cups-to-tablespoons", "volume", "cup", "tbsp", "Cups to Tablespoons", [0.125, 0.25, 0.333, 0.5, 0.667, 0.75, 1, 2]),
 ("ml-to-teaspoons", "volume", "ml", "tsp", "ML to Teaspoons", [1, 2, 2.5, 5, 7.5, 10, 15, 20, 25, 30]),
 ("ml-to-tablespoons", "volume", "ml", "tbsp", "ML to Tablespoons", [5, 10, 15, 20, 30, 45, 50, 60, 75, 100]),
 ("ml-to-liters", "volume", "ml", "l", "ML to Liters", [50, 100, 250, 330, 500, 750, 1000, 1500, 2000, 5000]),
 ("liters-to-oz", "volume", "l", "floz", "Liters to Oz", [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5]),
 ("quarts-to-cups", "volume", "qt", "cup", "Quarts to Cups", [0.5, 1, 1.5, 2, 3, 4, 5, 6, 8]),
 ("gallons-to-cups", "volume", "gal", "cup", "Gallons to Cups", [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 5]),
 ("square-feet-to-square-meters", "area", "ft2", "m2", "Square Feet to Square Meters", [1, 10, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 5000]),
 ("square-meters-to-square-feet", "area", "m2", "ft2", "Square Meters to Square Feet", [1, 5, 10, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500, 1000]),
 ("acres-to-square-feet", "area", "ac", "ft2", "Acres to Square Feet", [0.1, 0.25, 0.33, 0.5, 0.75, 1, 1.5, 2, 5, 10]),
 ("square-feet-to-acres", "area", "ft2", "ac", "Square Feet to Acres", [1000, 5000, 7500, 10000, 15000, 20000, 43560, 50000, 100000, 250000]),
 ("acres-to-hectares", "area", "ac", "ha", "Acres to Hectares", [1, 2, 5, 10, 20, 25, 40, 50, 80, 100, 160, 640, 1000]),
 ("hectares-to-acres", "area", "ha", "ac", "Hectares to Acres", [0.5, 1, 2, 5, 10, 20, 50, 100, 500, 1000]),
 ("square-miles-to-square-km", "area", "mi2", "km2", "Square Miles to Square KM", [1, 2, 5, 10, 25, 50, 100, 500, 1000]),
 ("square-km-to-square-miles", "area", "km2", "mi2", "Square KM to Square Miles", [1, 2, 5, 10, 25, 50, 100, 500, 1000]),
 ("kmh-to-mph", "speed", "kmh", "mph", "KM/H to MPH", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 160, 200, 300]),
 ("mph-to-kmh", "speed", "mph", "kmh", "MPH to KM/H", [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 100, 120, 150, 200]),
 ("knots-to-mph", "speed", "kn", "mph", "Knots to MPH", [1, 5, 10, 15, 20, 25, 30, 40, 50, 64, 100, 150]),
 ("mph-to-knots", "speed", "mph", "kn", "MPH to Knots", [5, 10, 20, 30, 40, 50, 74, 100, 150, 200]),
 ("meters-per-second-to-kmh", "speed", "ms", "kmh", "Meters per Second to KM/H", [1, 2, 5, 10, 15, 20, 25, 30, 50, 100, 343]),
 ("minutes-to-hours", "time", "min", "h", "Minutes to Hours", [5, 10, 15, 20, 30, 40, 45, 50, 60, 75, 90, 100, 120, 150, 180, 240, 300, 480, 600]),
 ("hours-to-minutes", "time", "h", "min", "Hours to Minutes", [0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 8, 10, 24]),
 ("seconds-to-minutes", "time", "s", "min", "Seconds to Minutes", [10, 30, 45, 60, 90, 100, 120, 150, 180, 240, 300, 500, 600, 1000, 3600]),
 ("hours-to-days", "time", "h", "d", "Hours to Days", [6, 12, 18, 24, 36, 48, 72, 96, 100, 120, 168, 200, 500, 1000]),
 ("days-to-weeks", "time", "d", "wk", "Days to Weeks", [1, 3, 5, 7, 10, 14, 21, 28, 30, 45, 60, 90, 100, 180, 365]),
 ("weeks-to-months", "time", "wk", "mo", "Weeks to Months", [1, 2, 4, 6, 8, 10, 12, 13, 16, 20, 26, 36, 40, 52]),
 ("mb-to-gb", "data", "MB", "GB", "MB to GB", [1, 10, 100, 250, 500, 750, 1000, 1500, 2000, 5000, 10000]),
 ("gb-to-mb", "data", "GB", "MB", "GB to MB", [0.1, 0.25, 0.5, 1, 1.5, 2, 4, 5, 8, 10, 16, 32, 64]),
 ("gb-to-tb", "data", "GB", "TB", "GB to TB", [100, 128, 250, 256, 500, 512, 750, 1000, 2000, 4000]),
 ("tb-to-gb", "data", "TB", "GB", "TB to GB", [0.5, 1, 2, 3, 4, 5, 8, 10, 16, 20]),
 ("kb-to-mb", "data", "KB", "MB", "KB to MB", [1, 10, 100, 250, 500, 750, 1000, 2000, 5000, 10000]),
 ("mb-to-kb", "data", "MB", "KB", "MB to KB", [0.1, 0.5, 1, 2, 5, 10, 25, 50, 100]),
 ("bits-to-bytes", "data", "bit", "B", "Bits to Bytes", [1, 8, 16, 32, 64, 128, 256, 512, 1024]),
]

# extra facts for the most-searched pairs
NOTES = {
 "cm-to-inches": "Since 1959 the inch has been defined as exactly 2.54 centimeters, so this conversion is exact.",
 "inches-to-cm": "Since 1959 the inch has been defined as exactly 2.54 centimeters, so this conversion is exact.",
 "kg-to-lbs": "The pound is defined as exactly 0.45359237 kilograms. A quick mental trick: double the kilograms and add 10% (70 kg ≈ 140 + 14 = 154 lb).",
 "lbs-to-kg": "The pound is defined as exactly 0.45359237 kilograms. A quick mental trick: halve the pounds and subtract 10% (150 lb ≈ 75 − 7.5 = 67.5 kg).",
 "celsius-to-fahrenheit": "Water freezes at 0 °C (32 °F) and boils at 100 °C (212 °F). Normal body temperature is about 37 °C (98.6 °F). At −40 the two scales are equal.",
 "fahrenheit-to-celsius": "Water freezes at 32 °F (0 °C) and boils at 212 °F (100 °C). A comfortable room is about 68–72 °F (20–22 °C). At −40 the two scales are equal.",
 "km-to-miles": "A 5K run is 3.11 miles, a 10K is 6.21 miles, a half marathon (21.0975 km) is 13.1 miles and a marathon (42.195 km) is 26.2 miles.",
 "miles-to-km": "A mile is exactly 1,609.344 meters. A half marathon is 13.1 miles (21.1 km) and a marathon is 26.2 miles (42.2 km).",
 "cm-to-feet": "Height tip: the average adult man in the U.S. is about 175 cm (5 ft 9 in) and the average woman about 161 cm (5 ft 3 in).",
 "feet-to-cm": "Height tip: 5 feet is 152.4 cm and 6 feet is 182.88 cm. To convert a height like 5 ft 8 in, convert the feet and inches separately and add them (152.4 + 20.32 = 172.72 cm).",
 "ml-to-oz": "This converter uses US fluid ounces (29.5735 mL). A UK (imperial) fluid ounce is slightly smaller at 28.4131 mL. A standard soda can holds 355 mL, or 12 US fl oz.",
 "oz-to-ml": "This converter uses US fluid ounces (29.5735 mL). A UK (imperial) fluid ounce is slightly smaller at 28.4131 mL. Weight ounces (oz) and fluid ounces (fl oz) are different units.",
 "liters-to-gallons": "This converter uses US gallons (3.785 L). A UK (imperial) gallon is larger at 4.546 L.",
 "gallons-to-liters": "This converter uses US gallons (3.785 L). A UK (imperial) gallon is larger at 4.546 L.",
 "cups-to-ml": "This uses the US customary cup of 236.59 mL. Many recipes round this to 240 mL, and metric cups in Australia and Canada are 250 mL.",
 "square-feet-to-acres": "One acre is exactly 43,560 square feet, about the size of an American football field without the end zones.",
 "acres-to-square-feet": "One acre is exactly 43,560 square feet, about the size of an American football field without the end zones.",
 "mb-to-gb": "This converter uses decimal units (1 GB = 1,000 MB), which is how storage makers and most phones label space. Computers sometimes use binary units, where 1 GiB = 1,024 MiB.",
 "gb-to-mb": "This converter uses decimal units (1 GB = 1,000 MB), which is how storage makers and most phones label space. Computers sometimes use binary units, where 1 GiB = 1,024 MiB.",
 "kmh-to-mph": "Common speed limits: 50 km/h ≈ 31 mph, 100 km/h ≈ 62 mph and 130 km/h ≈ 81 mph.",
 "mph-to-kmh": "Common speed limits: 25 mph ≈ 40 km/h, 55 mph ≈ 89 km/h and 70 mph ≈ 113 km/h.",
 "minutes-to-hours": "To turn decimal hours into hours and minutes, multiply the decimal part by 60. For example, 1.75 hours = 1 hour and 45 minutes.",
 "stone-to-lbs": "A stone is exactly 14 pounds. It's still commonly used for body weight in the UK and Ireland.",
}

def conv(cat, a, b, v):
    if cat == "temperature":
        c = v if a == "c" else (v - 32) * 5 / 9 if a == "f" else v - 273.15
        return c if b == "c" else c * 9 / 5 + 32 if b == "f" else c + 273.15
    U = CATS[cat]["units"]
    return v * U[a][3] / U[b][3]

def fmt(x):
    if x == 0: return "0"
    if abs(x) >= 1e15 or abs(x) < 1e-6: return f"{x:.4e}"
    d = max(0, min(10, 6 - int(math.floor(math.log10(abs(x))))))
    s = f"{round(x, d):,.{d}f}"
    if "." in s: s = s.rstrip("0").rstrip(".")
    return s

def ftin(cm):
    tot = cm / 2.54; ft = int(tot // 12); inch = tot - ft * 12
    if round(inch, 1) >= 12: ft += 1; inch = 0
    return f"{ft} ft {inch:.1f} in".replace(".0 in", " in")

def nm(cat, u, v=2):
    s, p, sym, _ = CATS[cat]["units"][u]
    return s if v == 1 else p

def unit_js():
    out = {k: {"name": c["name"], "units": {u: [d[0], d[1], d[2], d[3]] for u, d in c["units"].items()}} for k, c in CATS.items()}
    return "window.UNITS=" + json.dumps(out) + ";"

def widget(cat, a, b, allunits=False, val=1):
    extra = '<div class="cv-all" id="cv-all"></div>' if allunits else ""
    return f'''<div class="conv panel" id="conv" data-cat="{cat}" data-from="{a}" data-to="{b}"{' data-all="1"' if allunits else ""}>
<div class="cv-row"><input id="cv-a" type="number" inputmode="decimal" step="any" value="{fmt(val).replace(",", "")}" aria-label="From value"><select id="cv-ua" aria-label="From unit"></select></div>
<button class="cv-swap" id="cv-swap" type="button" aria-label="Swap units">⇅</button>
<div class="cv-row"><input id="cv-b" type="number" inputmode="decimal" step="any" aria-label="To value"><select id="cv-ub" aria-label="To unit"></select></div>
<div class="cv-res" id="cv-res"></div>{extra}</div><script src="units.js"></script><script src="convert.js"></script>'''

def formula(cat, a, b):
    U = CATS[cat]["units"]
    if cat == "temperature":
        F = {("c", "f"): "°F = °C × 9/5 + 32", ("f", "c"): "°C = (°F − 32) × 5/9", ("c", "k"): "K = °C + 273.15", ("k", "c"): "°C = K − 273.15",
             ("f", "k"): "K = (°F − 32) × 5/9 + 273.15", ("k", "f"): "°F = (K − 273.15) × 9/5 + 32"}
        return F[(a, b)], None
    r = U[a][3] / U[b][3]
    sig = lambda x: len(fmt(x).replace(",", "").replace(".", "").lstrip("0"))
    if r >= 1 or sig(1 / r) > sig(r) + 1:
        return f"{U[b][1]} = {U[a][1]} × {fmt(r)}", r
    return f"{U[b][1]} = {U[a][1]} ÷ {fmt(1 / r)}", r

def pair_page(slug, cat, a, b, title, vals):
    U = CATS[cat]["units"]; A, B = U[a], U[b]
    f, r = formula(cat, a, b)
    one = conv(cat, a, b, 1); back = conv(cat, b, a, 1)
    ex_v = vals[len(vals) // 2]; ex = conv(cat, a, b, ex_v)
    height = (a == "cm" and b == "ft")
    rows = "".join(f"<tr><td>{fmt(v)} {A[2]}</td><td><b>{fmt(conv(cat, a, b, v))} {B[2]}</b>{' <span class=muted>(' + ftin(v) + ')</span>' if height else ''}</td></tr>" for v in vals)
    title_full = f"{title} Converter – Convert {A[1].title()} to {B[1].title()}"
    desc = f"Convert {A[1]} to {B[1]} instantly. 1 {A[0]} = {fmt(one)} {B[1] if abs(one) != 1 else B[0]}. Free {title.lower()} converter with formula, examples and a conversion chart."
    sub = f"Type a number in either box to convert between {A[1]} and {B[1]} instantly."
    howto = f"<p>{'To convert ' + A[1] + ' to ' + B[1] + ', use this formula:'}</p><p class='formula'>{f}</p>"
    if r is not None:
        howto += f"<p>1 {A[0]} = <b>{fmt(one)}</b> {B[1] if abs(one) != 1 else B[0]}, and 1 {B[0]} = <b>{fmt(back)}</b> {A[1] if abs(back) != 1 else A[0]}.</p>"
    example = f"<h2>Example</h2><p>Convert {fmt(ex_v)} {A[1] if ex_v != 1 else A[0]} to {B[1]}:</p><p class='formula'>{fmt(ex_v)} {A[2]} → <b>{fmt(ex)} {B[2]}</b>{' (' + ftin(ex_v) + ')' if height else ''}</p>"
    note = f"<p>{NOTES[slug]}</p>" if slug in NOTES else ""
    rev = next((p for p in PAIRS if p[1] == cat and p[2] == b and p[3] == a), None)
    rel = [p for p in PAIRS if p[1] == cat and p[0] != slug][:10]
    links = "".join(f'<a href="{p[0]}">{p[4]}</a>' for p in ([rev] if rev else []) + [p for p in rel if p is not rev])
    content = f"""<h2>How to convert {A[1]} to {B[1]}</h2>{howto}{note}{example}
<h2>{title} conversion chart</h2><table class="cv-table"><thead><tr><th>{A[1].title()} ({A[2]})</th><th>{B[1].title()} ({B[2]})</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Frequently asked questions</h2><div class="faq"><details open><summary>How many {B[1]} are in a {A[0]}?</summary><p>There {'is' if abs(one) == 1 else 'are'} {fmt(one)} {B[1] if abs(one) != 1 else B[0]} in 1 {A[0]}.</p></details>
<details><summary>How many {A[1]} are in a {B[0]}?</summary><p>There {'is' if abs(back) == 1 else 'are'} {fmt(back)} {A[1] if abs(back) != 1 else A[0]} in 1 {B[0]}.</p></details>
<details><summary>What is the formula for {A[1]} to {B[1]}?</summary><p>{f}.</p></details></div>
<h2>Related conversions</h2><div class="cv-links">{links}<a href="{HUB[cat]}">All {CATS[cat]['name'].lower()} conversions</a><a href="unit-converter">Unit converter</a></div>"""
    if cat == "temperature":
        content = content.replace(f"<details open><summary>How many {B[1]} are in a {A[0]}?</summary><p>There {'is' if abs(one) == 1 else 'are'} {fmt(one)} {B[1] if abs(one) != 1 else B[0]} in 1 {A[0]}.</p></details>",
            f"<details open><summary>What is 0 {A[2]} in {B[2]}?</summary><p>0 {A[2]} = {fmt(conv(cat, a, b, 0))} {B[2]}.</p></details>")
        content = content.replace(f"<details><summary>How many {A[1]} are in a {B[0]}?</summary><p>There {'is' if abs(back) == 1 else 'are'} {fmt(back)} {A[1] if abs(back) != 1 else A[0]} in 1 {B[0]}.</p></details>",
            f"<details><summary>What is 100 {A[2]} in {B[2]}?</summary><p>100 {A[2]} = {fmt(conv(cat, a, b, 100))} {B[2]}.</p></details>")
    faq = [(f"How do I convert {A[1]} to {B[1]}?", f"Use the formula {f}.")]
    return dict(slug=slug, title=title_full, desc=desc, h1=f"{title} Converter", sub=sub, tool=widget(cat, a, b, val=ex_v), content=content, faq=faq, cat=cat)

HUB_INTRO = {
 "length": "Convert between metric units (millimeters, centimeters, meters, kilometers) and US/imperial units (inches, feet, yards, miles).",
 "weight": "Convert between grams, kilograms, ounces, pounds, stone and tons. Weight and mass use the same units in everyday life.",
 "temperature": "Convert between Celsius, Fahrenheit and Kelvin, the three temperature scales used around the world and in science.",
 "volume": "Convert cooking and liquid measurements: milliliters, liters, teaspoons, tablespoons, cups, fluid ounces, pints, quarts and gallons (US).",
 "area": "Convert square feet, square meters, acres, hectares and more for homes, land and floor plans.",
 "speed": "Convert between km/h, mph, meters per second, feet per second and knots.",
 "time": "Convert milliseconds, seconds, minutes, hours, days, weeks, months and years. Months and years use average lengths (30.44 and 365.24 days).",
 "data": "Convert bits, bytes, kilobytes, megabytes, gigabytes and terabytes, in both decimal (1 GB = 1,000 MB) and binary (1 GiB = 1,024 MiB) units.",
}
def hub_page(cat):
    c = CATS[cat]; us = list(c["units"])
    a, b = us[1], us[min(len(us) - 1, 4)]
    if cat == "temperature": a, b = "c", "f"
    pairs = [p for p in PAIRS if p[1] == cat]
    links = "".join(f'<a href="{p[0]}">{p[4]}</a>' for p in pairs)
    units = "".join(f"<li><b>{d[1].title()}</b> ({d[2]})</li>" for d in c["units"].values())
    content = f"""<h2>About {c['name'].lower()} conversion</h2><p>{HUB_INTRO[cat]} Enter a value above and every unit updates at once.</p>
<h2>Popular {c['name'].lower()} conversions</h2><div class="cv-links">{links}</div>
<h2>Units included</h2><ul class="cv-units">{units}</ul>
<h2>More converters</h2><div class="cv-links">{''.join(f'<a href="{HUB[k]}">{CATS[k]["emoji"]} {CATS[k]["name"]}</a>' for k in CATS if k != cat)}</div>"""
    return dict(slug=HUB[cat], title=f"{c['name']} Converter – Convert {c['name']} Units Online", desc=f"Free {c['name'].lower()} converter. {HUB_INTRO[cat]}",
                h1=f"{c['name']} Converter", sub=f"Convert any {c['name'].lower()} unit and see every result at once.", tool=widget(cat, a, b, True), content=content, faq=[], cat=cat)

def main_hub():
    cards = "".join(f'<a class="card" href="{HUB[k]}" style="--bgc:#ede9fe;--c:#7c3aed"><div class="e">{c["emoji"]}</div><div><b>{c["name"]} Converter</b><span>{", ".join(d[2] for d in list(c["units"].values())[:5])}…</span></div></a>' for k, c in CATS.items())
    top = ["cm-to-inches", "kg-to-lbs", "celsius-to-fahrenheit", "fahrenheit-to-celsius", "inches-to-cm", "lbs-to-kg", "feet-to-meters", "km-to-miles", "ml-to-oz", "cm-to-feet", "mm-to-inches", "oz-to-ml", "liters-to-gallons", "mph-to-kmh", "cups-to-ml", "mb-to-gb"]
    T = {p[0]: p for p in PAIRS}
    tool = f'''{widget("length", "cm", "in").replace('id="conv"', 'id="conv" data-pick="1"')}<section class="cats"><h2>🔁 Choose a converter</h2><div class="grid-cards">{cards}</div></section>'''
    content = f"""<h2>Most popular conversions</h2><div class="cv-links">{''.join(f'<a href="{s}">{T[s][4]}</a>' for s in top)}</div>
<h2>A free unit converter for everything</h2><p>Convert length, weight, temperature, volume, area, speed, time and data storage in one place. Pick a category in the converter above, choose your units, and type a number. The answer appears instantly, and you can type in either box to convert in both directions.</p>
<h2>All conversions</h2>""" + "".join(f"<h3>{CATS[k]['emoji']} {CATS[k]['name']}</h3><div class='cv-links'>" + "".join(f'<a href="{p[0]}">{p[4]}</a>' for p in PAIRS if p[1] == k) + "</div>" for k in CATS)
    return dict(slug="unit-converter", title="Unit Converter – Free Online Conversion Calculator", desc="Free online unit converter for length, weight, temperature, volume, area, speed, time and data. Instant, accurate conversions with formulas and charts.",
                h1="Unit Converter", sub="Convert length, weight, temperature, volume and more, instantly and accurately.", tool=tool, content=content, faq=[], cat=None)

def all_pages():
    return [main_hub()] + [hub_page(k) for k in CATS] + [pair_page(*p) for p in PAIRS]
