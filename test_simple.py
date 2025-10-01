"""Simple test to check Maybank website accessibility."""
import re

try:
    import requests
    
    url = 'https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    print('Fetching from Maybank...')
    resp = requests.get(url, headers=headers, timeout=15, verify=False)
    print(f'Status: {resp.status_code}')
    print(f'URL: {resp.url}')
    print(f'HTML length: {len(resp.text)} chars')
    
    # Save for inspection
    with open('maybank_test.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)
    print('Saved to maybank_test.html')
    
    # Test parsing
    html_n = re.sub(r'\s+', ' ', resp.text)
    
    # Pattern 1
    pattern = r'\b(Gold|Silver)\b[^<]{0,200}?\bBuy\b[^\d]{0,50}(\d[\d.,]{0,10})[^<]{0,200}?\bSell\b[^\d]{0,50}(\d[\d.,]{0,10})'
    matches = list(re.finditer(pattern, html_n, re.IGNORECASE))
    print(f'\nPattern 1 found {len(matches)} matches:')
    for m in matches:
        print(f'  {m.group(1)}: Buy={m.group(2)}, Sell={m.group(3)}')
    
    # Pattern 2
    pattern2 = r'\b(Gold|Silver)\b[^\d]{0,100}(\d[\d.,]{1,10})[^\d]{1,100}(\d[\d.,]{1,10})'
    matches2 = list(re.finditer(pattern2, html_n, re.IGNORECASE))
    print(f'\nPattern 2 found {len(matches2)} matches (showing first 3):')
    for m in matches2[:3]:
        print(f'  {m.group(1)}: {m.group(2)}, {m.group(3)}')
    
    # Show snippet
    if 'gold' in html_n.lower():
        idx = html_n.lower().find('gold')
        print(f'\nSnippet: ...{html_n[max(0,idx-100):idx+200]}...')
        
except ImportError:
    print("requests not installed. Install with: pip install requests")
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
