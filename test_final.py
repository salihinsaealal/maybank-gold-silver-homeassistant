"""Final test - fetch and parse Maybank prices."""
import re
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Copy the exact patterns from our code
_RE_TABLE_PATTERN = re.compile(
    r"<tr[^>]*>.*?\b(Gold|Silver)\b.*?(\d+\.\d{2}).*?(\d+\.\d{2}).*?</tr>",
    re.IGNORECASE | re.DOTALL
)

_RE_BUY_SELL_ROW = re.compile(
    r"\b(Gold|Silver)\b.{0,500}?\bBuy\b.{0,100}?(\d+\.\d{2}).{0,500}?\bSell\b.{0,100}?(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

_RE_METAL_TWO_NUMBERS = re.compile(
    r"\b(Gold|Silver)\b.{0,200}?(\d+\.\d{2}).{1,200}?(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

_RE_WITH_CURRENCY = re.compile(
    r"\b(Gold|Silver)\b.{0,300}?(?:RM|MYR)\s*(\d+\.\d{2}).{1,300}?(?:RM|MYR)\s*(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

def _to_float(val):
    return float(val.replace(",", "").strip())

def test_parse(html):
    """Test parsing with all strategies."""
    prices = {"gold": {}, "silver": {}}
    
    print("\n=== STRATEGY D: Table Pattern ===")
    matches = list(_RE_TABLE_PATTERN.finditer(html))
    print(f"Found {len(matches)} matches")
    for m in matches[:5]:
        print(f"  {m.group(1)}: {m.group(2)}, {m.group(3)}")
        metal = m.group(1).lower()
        try:
            prices[metal]["buy"] = _to_float(m.group(2))
            prices[metal]["sell"] = _to_float(m.group(3))
            print(f"  ✓ Parsed {metal}: buy={prices[metal]['buy']}, sell={prices[metal]['sell']}")
        except:
            pass
    
    if prices["gold"].get("buy"):
        print("✓ Strategy D SUCCESS!")
        return prices
    
    # Normalize for other strategies
    html_n = re.sub(r"\s+", " ", html)
    
    print("\n=== STRATEGY A: Buy/Sell Labels ===")
    matches = list(_RE_BUY_SELL_ROW.finditer(html_n))
    print(f"Found {len(matches)} matches")
    for m in matches[:5]:
        print(f"  {m.group(1)}: Buy={m.group(2)}, Sell={m.group(3)}")
        metal = m.group(1).lower()
        try:
            prices[metal]["buy"] = _to_float(m.group(2))
            prices[metal]["sell"] = _to_float(m.group(3))
            print(f"  ✓ Parsed {metal}: buy={prices[metal]['buy']}, sell={prices[metal]['sell']}")
        except:
            pass
    
    if prices["gold"].get("buy"):
        print("✓ Strategy A SUCCESS!")
        return prices
    
    print("\n=== STRATEGY B: Two Numbers ===")
    matches = list(_RE_METAL_TWO_NUMBERS.finditer(html_n))
    print(f"Found {len(matches)} matches (showing first 10)")
    for m in matches[:10]:
        print(f"  {m.group(1)}: {m.group(2)}, {m.group(3)}")
        metal = m.group(1).lower()
        if "buy" not in prices[metal]:
            try:
                prices[metal]["buy"] = _to_float(m.group(2))
                prices[metal]["sell"] = _to_float(m.group(3))
                print(f"  ✓ Parsed {metal}: buy={prices[metal]['buy']}, sell={prices[metal]['sell']}")
            except:
                pass
    
    if prices["gold"].get("buy"):
        print("✓ Strategy B SUCCESS!")
        return prices
    
    print("\n=== STRATEGY C: Currency Markers ===")
    matches = list(_RE_WITH_CURRENCY.finditer(html_n))
    print(f"Found {len(matches)} matches")
    for m in matches[:5]:
        print(f"  {m.group(1)}: RM {m.group(2)}, RM {m.group(3)}")
        metal = m.group(1).lower()
        try:
            prices[metal]["buy"] = _to_float(m.group(2))
            prices[metal]["sell"] = _to_float(m.group(3))
            print(f"  ✓ Parsed {metal}: buy={prices[metal]['buy']}, sell={prices[metal]['sell']}")
        except:
            pass
    
    if prices["gold"].get("buy"):
        print("✓ Strategy C SUCCESS!")
        return prices
    
    print("\n✗ ALL STRATEGIES FAILED")
    return prices

# Main test
url = 'https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

print('Fetching from Maybank...')
try:
    resp = requests.get(url, headers=headers, timeout=30, verify=False)
    print(f'✓ Status: {resp.status_code}')
    print(f'✓ URL: {resp.url}')
    html = resp.text
    print(f'✓ HTML length: {len(html)} chars')
    
    # Save for inspection
    with open('maybank_test_final.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('✓ Saved to maybank_test_final.html')
    
    # Test parsing
    print("\n" + "="*60)
    print("TESTING PARSING STRATEGIES")
    print("="*60)
    
    result = test_parse(html)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    if result.get("gold", {}).get("buy") and result.get("gold", {}).get("sell"):
        print("✓✓✓ SUCCESS! ✓✓✓")
        print(f"\nGold Buy:  RM {result['gold']['buy']:.2f}/g")
        print(f"Gold Sell: RM {result['gold']['sell']:.2f}/g")
        if result.get("silver", {}).get("buy"):
            print(f"Silver Buy:  RM {result['silver']['buy']:.2f}/g")
            print(f"Silver Sell: RM {result['silver']['sell']:.2f}/g")
    else:
        print("✗✗✗ FAILED ✗✗✗")
        print("\nNo valid prices found. Let me show you what's in the HTML...")
        
        # Show context around gold/silver
        for keyword in ['gold', 'silver']:
            if keyword in html.lower():
                idx = html.lower().find(keyword)
                print(f"\n--- Context around '{keyword}' (position {idx}) ---")
                print(html[max(0, idx-200):idx+400])
                break
    
except Exception as e:
    print(f'\n✗ Error: {e}')
    import traceback
    traceback.print_exc()
