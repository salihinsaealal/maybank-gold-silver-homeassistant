"""Test parsing of Maybank HTML."""
import re
import requests

url = 'https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

print('Fetching from Maybank...')
try:
    resp = requests.get(url, headers=headers, timeout=30, verify=False)
    print(f'Status: {resp.status_code}')
    html = resp.text
    print(f'HTML length: {len(html)} chars\n')
    
    # Save full HTML
    with open('maybank_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Saved full HTML to maybank_full.html\n')
    
    # Look for gold/silver keywords
    html_lower = html.lower()
    
    # Find all occurrences of "gold" and "silver"
    print('=== Searching for Gold/Silver mentions ===')
    for keyword in ['gold', 'silver']:
        indices = [i for i in range(len(html_lower)) if html_lower.startswith(keyword, i)]
        print(f'\nFound "{keyword}" {len(indices)} times')
        
        # Show first 3 occurrences with context
        for idx in indices[:3]:
            start = max(0, idx - 100)
            end = min(len(html), idx + 300)
            snippet = html[start:end]
            print(f'\n--- Occurrence at position {idx} ---')
            print(snippet)
            print('---')
    
    # Try to find numbers that look like prices
    print('\n=== Looking for price patterns ===')
    # Look for patterns like: 3.45, 123.45, etc.
    price_pattern = r'\b\d{1,4}\.\d{2}\b'
    prices = re.findall(price_pattern, html)
    print(f'Found {len(prices)} potential prices: {prices[:20]}')
    
    # Look for table structures
    print('\n=== Looking for tables ===')
    tables = re.findall(r'<table[^>]*>.*?</table>', html, re.IGNORECASE | re.DOTALL)
    print(f'Found {len(tables)} tables')
    
    if tables:
        print('\nFirst table content (first 500 chars):')
        print(tables[0][:500])
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
