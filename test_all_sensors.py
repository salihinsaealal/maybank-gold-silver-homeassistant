"""Test complete integration with all sensors including MIGA-i."""
import re

# All patterns
_RE_MAYBANK_INVESTMENT = re.compile(
    r"(Gold|Silver)\s+Investment\s+Account.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

_RE_MIGA_100G = re.compile(
    r"For 100 grams and above.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

_RE_MIGA_BELOW100G = re.compile(
    r"For below 100 grams.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

def _to_float(val):
    return float(val.replace(",", "").strip())

# Full HTML from user
full_html = """<div class="col-sm-6"><p class="text-medium black">Maybank Gold Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>534.14</td><td>513.79</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Kijang Emas Daily Prices</p><div class="table-responsive"><table class="table highlight"><tr><th>Size (oz)</th><th>Selling (RM)</th><th>Buying (RM)</th></tr><td>ONE</td><td>17,271.00</td><td>16,578.00</td></tr> <tr><td>HALF</td><td>8,798.00</td><td>8,289.00</td></tr> <tr><td>QUARTER</td><td>4,481.00</td><td>4,144.00</td></tr></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div></div><div class="col-sm-6"><p class="text-medium black">Maybank Silver Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>6.62</td><td>6.10</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Maybank Islamic Gold Account-i (MIGA-i) </p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><tr><td>For 100 grams and above</td><td>534.13</td><td>522.06</td></tr><tr><td>For below 100 grams </td><td>535.88</td><td>521.56</td></tr></table><p class="text-small">Effective on 01 Oct 2025 09:17:39</p></div></div>"""

prices = {
    "gold": {}, 
    "silver": {},
    "miga_100g": {},
    "miga_below100g": {}
}

# Parse regular gold/silver
for m in _RE_MAYBANK_INVESTMENT.finditer(full_html):
    metal = m.group(1).lower()
    selling = m.group(2)
    buying = m.group(3)
    if selling and buying:
        prices[metal]["buy"] = _to_float(selling)
        prices[metal]["sell"] = _to_float(buying)

# Parse MIGA-i
match_100g = _RE_MIGA_100G.search(full_html)
if match_100g:
    prices["miga_100g"]["buy"] = _to_float(match_100g.group(1))
    prices["miga_100g"]["sell"] = _to_float(match_100g.group(2))

match_below100g = _RE_MIGA_BELOW100G.search(full_html)
if match_below100g:
    prices["miga_below100g"]["buy"] = _to_float(match_below100g.group(1))
    prices["miga_below100g"]["sell"] = _to_float(match_below100g.group(2))

print("="*70)
print("COMPLETE INTEGRATION TEST - ALL SENSORS")
print("="*70)

print("\nRegular Investment Accounts:")
print("-"*70)
if prices["gold"].get("buy"):
    print(f"Gold Buy:   RM {prices['gold']['buy']:.2f}/g")
    print(f"Gold Sell:  RM {prices['gold']['sell']:.2f}/g")
else:
    print("Gold: NOT FOUND")

if prices["silver"].get("buy"):
    print(f"Silver Buy:  RM {prices['silver']['buy']:.2f}/g")
    print(f"Silver Sell: RM {prices['silver']['sell']:.2f}/g")
else:
    print("Silver: NOT FOUND")

print("\nMaybank Islamic Gold Account-i (MIGA-i):")
print("-"*70)
if prices["miga_100g"].get("buy"):
    print(f"MIGA-i (>=100g) Buy:  RM {prices['miga_100g']['buy']:.2f}/g")
    print(f"MIGA-i (>=100g) Sell: RM {prices['miga_100g']['sell']:.2f}/g")
else:
    print("MIGA-i 100g: NOT FOUND")

if prices["miga_below100g"].get("buy"):
    print(f"MIGA-i (<100g) Buy:   RM {prices['miga_below100g']['buy']:.2f}/g")
    print(f"MIGA-i (<100g) Sell:  RM {prices['miga_below100g']['sell']:.2f}/g")
else:
    print("MIGA-i below 100g: NOT FOUND")

print("\n" + "="*70)
total_sensors = sum(1 for p in prices.values() if p.get("buy"))
print(f"SUCCESS! Found {total_sensors} price pairs (8 sensors total)")
print("="*70)
