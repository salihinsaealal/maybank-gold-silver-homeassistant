"""Test with actual Maybank HTML structure."""
import re

actual_html = """
<div class="col-sm-6"><p class="text-medium black">Maybank Gold Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>534.14</td><td>513.79</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div><p class="text-medium black p-top-50">Kijang Emas Daily Prices</p><div class="table-responsive"><table class="table highlight"><tr><th>Size (oz)</th><th>Selling (RM)</th><th>Buying (RM)</th></tr><td>ONE</td><td>17,271.00</td><td>16,578.00</td></tr> <tr><td>HALF</td><td>8,798.00</td><td>8,289.00</td></tr> <tr><td>QUARTER</td><td>4,481.00</td><td>4,144.00</td></tr></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div></div><div class="col-sm-6"><p class="text-medium black">Maybank Silver Investment Account</p><div class="table-responsive"><table class="table highlight"><tr><th>Date</th><th>Selling (RM/g)</th><th>Buying (RM/g)</th></tr><td>01 Oct 2025</td><td>6.62</td><td>6.10</td></table><p class="text-small">Effective on 01 Oct 2025 01:44 PM</p></div>
"""

print("="*70)
print("TESTING WITH ACTUAL MAYBANK HTML")
print("="*70)

# Pattern 1: Look for "Gold Investment Account" followed by Selling/Buying
pattern_gold = re.compile(
    r"Gold Investment Account.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

# Pattern 2: Look for "Silver Investment Account" followed by Selling/Buying
pattern_silver = re.compile(
    r"Silver Investment Account.*?<td>(\d+\.\d{2})</td><td>(\d+\.\d{2})</td>",
    re.IGNORECASE | re.DOTALL
)

print("\nSearching for Gold prices...")
match_gold = pattern_gold.search(actual_html)
if match_gold:
    selling = match_gold.group(1)  # Bank sells to you (your buy price)
    buying = match_gold.group(2)   # Bank buys from you (your sell price)
    print(f"  Found: Selling={selling}, Buying={buying}")
    print(f"  Interpretation:")
    print(f"    Customer BUY price (bank sells):  RM {selling}/g")
    print(f"    Customer SELL price (bank buys):  RM {buying}/g")
else:
    print("  NOT FOUND")

print("\nSearching for Silver prices...")
match_silver = pattern_silver.search(actual_html)
if match_silver:
    selling = match_silver.group(1)
    buying = match_silver.group(2)
    print(f"  Found: Selling={selling}, Buying={buying}")
    print(f"  Interpretation:")
    print(f"    Customer BUY price (bank sells):  RM {selling}/g")
    print(f"    Customer SELL price (bank buys):  RM {buying}/g")
else:
    print("  NOT FOUND")

print("\n" + "="*70)
print("RESULT")
print("="*70)

if match_gold and match_silver:
    print("\nSUCCESS! Pattern works!")
    print("\nFinal prices:")
    print(f"  Gold Buy:  RM {match_gold.group(1)}/g (what customer pays)")
    print(f"  Gold Sell: RM {match_gold.group(2)}/g (what customer gets)")
    print(f"  Silver Buy:  RM {match_silver.group(1)}/g")
    print(f"  Silver Sell: RM {match_silver.group(2)}/g")
    
    print("\nNOTE: Maybank uses 'Selling' for customer buy price")
    print("      and 'Buying' for customer sell price")
else:
    print("\nFAILED - Pattern doesn't match")
