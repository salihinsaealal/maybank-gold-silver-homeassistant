"""Test MIGA-i parsing."""
import re

html = """<p class="text-medium black p-top-50">Maybank Islamic Gold Account-i (MIGA-i) </p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><tr><td>For 100 grams and above</td><td>534.13</td><td>522.06</td></tr><tr><td>For below 100 grams </td><td>535.88</td><td>521.56</td></tr></table><p class="text-small">Effective on 01 Oct 2025 09:17:39</p></div>"""

# Pattern for MIGA-i 100g and above
pattern_100g = re.compile(
    r"For 100 grams and above.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

# Pattern for MIGA-i below 100g
pattern_below100g = re.compile(
    r"For below 100 grams.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

print("Testing MIGA-i patterns:")
print("="*60)

match_100g = pattern_100g.search(html)
if match_100g:
    print(f"\n100g and above:")
    print(f"  Selling (Buy): {match_100g.group(1)}")
    print(f"  Buying (Sell): {match_100g.group(2)}")
else:
    print("\n100g pattern: NOT FOUND")

match_below100g = pattern_below100g.search(html)
if match_below100g:
    print(f"\nBelow 100g:")
    print(f"  Selling (Buy): {match_below100g.group(1)}")
    print(f"  Buying (Sell): {match_below100g.group(2)}")
else:
    print("\nBelow 100g pattern: NOT FOUND")

if match_100g and match_below100g:
    print("\n" + "="*60)
    print("SUCCESS! Both MIGA-i tiers found!")
    print("="*60)
