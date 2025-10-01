"""Test the FIXED parsing logic to ensure MIGA-i data is fetched."""
import re

# All patterns from the fixed code
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

def _parse_prices(html):
    """FIXED parsing logic - no early returns before MIGA-i."""
    prices = {
        "gold": {}, 
        "silver": {},
        "miga_100g": {},
        "miga_below100g": {}
    }

    # Strategy A: Maybank-specific "Investment Account" pattern
    print("Running Strategy A (Investment Account)...")
    for m in _RE_MAYBANK_INVESTMENT.finditer(html):
        metal = m.group(1).lower()
        selling = m.group(2)
        buying = m.group(3)
        if selling and buying:
            try:
                prices[metal]["buy"] = _to_float(selling)
                prices[metal]["sell"] = _to_float(buying)
                print(f"  Found {metal}: buy={selling}, sell={buying}")
            except (ValueError, AttributeError):
                pass
    
    # NO EARLY RETURN HERE - Continue to MIGA-i parsing
    
    # Parse MIGA-i prices (Islamic Gold Account)
    print("\nRunning MIGA-i parsing...")
    match_100g = _RE_MIGA_100G.search(html)
    if match_100g:
        try:
            prices["miga_100g"]["buy"] = _to_float(match_100g.group(1))
            prices["miga_100g"]["sell"] = _to_float(match_100g.group(2))
            print(f"  Found MIGA-i 100g+: buy={match_100g.group(1)}, sell={match_100g.group(2)}")
        except (ValueError, AttributeError):
            pass
    else:
        print("  MIGA-i 100g+ NOT FOUND")
    
    match_below100g = _RE_MIGA_BELOW100G.search(html)
    if match_below100g:
        try:
            prices["miga_below100g"]["buy"] = _to_float(match_below100g.group(1))
            prices["miga_below100g"]["sell"] = _to_float(match_below100g.group(2))
            print(f"  Found MIGA-i <100g: buy={match_below100g.group(1)}, sell={match_below100g.group(2)}")
        except (ValueError, AttributeError):
            pass
    else:
        print("  MIGA-i <100g NOT FOUND")

    # Validate and clean up
    for metal in list(prices.keys()):
        if not prices[metal].get("buy") and not prices[metal].get("sell"):
            prices.pop(metal, None)

    return prices

# Full HTML from user
full_html = """<div class="col-sm-6"><p class="text-medium black">Maybank Gold Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>534.14</td><td>513.79</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Kijang Emas Daily Prices</p><div class="table-responsive"><table class="table highlight"><tr><th>Size (oz)</th><th>Selling (RM)</th><th>Buying (RM)</th></tr><td>ONE</td><td>17,271.00</td><td>16,578.00</td></tr> <tr><td>HALF</td><td>8,798.00</td><td>8,289.00</td></tr> <tr><td>QUARTER</td><td>4,481.00</td><td>4,144.00</td></tr></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div></div><div class="col-sm-6"><p class="text-medium black">Maybank Silver Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>6.62</td><td>6.10</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Maybank Islamic Gold Account-i (MIGA-i) </p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><tr><td>For 100 grams and above</td><td>534.13</td><td>522.06</td></tr><tr><td>For below 100 grams </td><td>535.88</td><td>521.56</td></tr></table><p class="text-small">Effective on 01 Oct 2025 09:17:39</p></div></div>"""

print("="*70)
print("TESTING FIXED PARSING LOGIC")
print("="*70)

result = _parse_prices(full_html)

print("\n" + "="*70)
print("FINAL RESULT")
print("="*70)

all_found = True
for metal, data in result.items():
    if data.get("buy") and data.get("sell"):
        print(f"\n{metal.upper()}:")
        print(f"  Buy:  RM {data['buy']:.2f}/g")
        print(f"  Sell: RM {data['sell']:.2f}/g")
    else:
        print(f"\n{metal.upper()}: MISSING DATA!")
        all_found = False

print("\n" + "="*70)
if all_found and len(result) == 4:
    print("SUCCESS! All 4 price pairs found (8 sensors)")
    print("Gold: OK, Silver: OK, MIGA-i 100g+: OK, MIGA-i <100g: OK")
else:
    print(f"FAILED! Only found {len(result)} price pairs")
print("="*70)
