"""Test the exact code from integration with actual Maybank HTML."""
import re

# Exact patterns from integration
_RE_MAYBANK_INVESTMENT = re.compile(
    r"(Gold|Silver)\s+Investment\s+Account.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

_RE_SELLING_BUYING = re.compile(
    r"\b(Gold|Silver)\b.*?Selling.*?Buying.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

_RE_TABLE_CELLS = re.compile(
    r"\b(Gold|Silver)\b.*?<td>(\d+\.\d{2})</td>\s*<td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

_RE_TWO_DECIMALS = re.compile(
    r"\b(Gold|Silver)\b.{0,300}?(\d+\.\d{2}).{1,300}?(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

def _to_float(val):
    return float(val.replace(",", "").strip())

def _parse_prices(html):
    """Exact parsing logic from integration."""
    prices = {"gold": {}, "silver": {}}

    # Strategy A: Maybank-specific "Investment Account" pattern
    for m in _RE_MAYBANK_INVESTMENT.finditer(html):
        metal = m.group(1).lower()
        selling = m.group(2)
        buying = m.group(3)
        if selling and buying:
            try:
                prices[metal]["buy"] = _to_float(selling)
                prices[metal]["sell"] = _to_float(buying)
            except (ValueError, AttributeError):
                pass
    
    if prices["gold"].get("buy") and prices["gold"].get("sell"):
        return prices
    
    # Strategy B: Generic Selling/Buying pattern
    for m in _RE_SELLING_BUYING.finditer(html):
        metal = m.group(1).lower()
        selling = m.group(2)
        buying = m.group(3)
        if selling and buying:
            try:
                prices[metal]["buy"] = _to_float(selling)
                prices[metal]["sell"] = _to_float(buying)
            except (ValueError, AttributeError):
                pass
    
    if prices["gold"].get("buy") and prices["gold"].get("sell"):
        return prices
    
    # Strategy C: Table cells pattern
    for m in _RE_TABLE_CELLS.finditer(html):
        metal = m.group(1).lower()
        first = m.group(2)
        second = m.group(3)
        if first and second and "buy" not in prices[metal]:
            try:
                prices[metal]["buy"] = _to_float(first)
                prices[metal]["sell"] = _to_float(second)
            except (ValueError, AttributeError):
                pass

    if prices["gold"].get("buy") and prices["gold"].get("sell"):
        return prices

    # Strategy D: Fallback
    for m in _RE_TWO_DECIMALS.finditer(html):
        metal = m.group(1).lower()
        first = m.group(2)
        second = m.group(3)
        if first and second and "buy" not in prices[metal]:
            try:
                prices[metal]["buy"] = _to_float(first)
                prices[metal]["sell"] = _to_float(second)
            except (ValueError, AttributeError):
                pass

    # Validate
    for metal in list(prices.keys()):
        if not prices[metal].get("buy") or not prices[metal].get("sell"):
            prices.pop(metal, None)

    return prices

# Actual HTML from user
actual_html = """<div class="col-sm-6"><p class="text-medium black">Maybank Gold Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>534.14</td><td>513.79</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Kijang Emas Daily Prices</p><div class="table-responsive"><table class="table highlight"><tr><th>Size (oz)</th><th>Selling (RM)</th><th>Buying (RM)</th></tr><td>ONE</td><td>17,271.00</td><td>16,578.00</td></tr> <tr><td>HALF</td><td>8,798.00</td><td>8,289.00</td></tr> <tr><td>QUARTER</td><td>4,481.00</td><td>4,144.00</td></tr></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div></div><div class="col-sm-6"><p class="text-medium black">Maybank Silver Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>6.62</td><td>6.10</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div>"""

print("="*70)
print("TESTING INTEGRATION CODE WITH ACTUAL MAYBANK HTML")
print("="*70)

result = _parse_prices(actual_html)

print("\nRESULT:")
print("-"*70)

if result.get("gold", {}).get("buy") and result.get("silver", {}).get("buy"):
    print("SUCCESS! Parsing works correctly!")
    print(f"\nGold:")
    print(f"  Buy Price:  RM {result['gold']['buy']:.2f}/g")
    print(f"  Sell Price: RM {result['gold']['sell']:.2f}/g")
    print(f"\nSilver:")
    print(f"  Buy Price:  RM {result['silver']['buy']:.2f}/g")
    print(f"  Sell Price: RM {result['silver']['sell']:.2f}/g")
    print("\nReady to deploy to Home Assistant!")
else:
    print("FAILED - No prices found")
    print(f"Result: {result}")
