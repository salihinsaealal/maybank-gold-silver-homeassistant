"""Test script to verify Maybank scraping works."""
import asyncio
import re
try:
    import aiohttp
except ImportError:
    print("aiohttp not installed. Install with: pip install aiohttp")
    exit(1)

async def test_scrape():
    url = 'https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-MY,en;q=0.9',
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print('Fetching from Maybank...')
            async with session.get(url, headers=headers, timeout=15, ssl=False) as resp:
                print(f'Status: {resp.status}')
                print(f'URL: {resp.url}')
                html = await resp.text()
                print(f'HTML length: {len(html)} chars')
                
                # Save HTML for inspection
                with open('maybank_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print('Saved HTML to maybank_page.html')
                
                # Normalize whitespace
                html_n = re.sub(r'\s+', ' ', html)
                
                # Test regex patterns
                print('\n=== Testing Pattern 1 (Buy/Sell) ===')
                pattern1 = r'\b(Gold|Silver)\b[^<]{0,200}?\bBuy\b[^\d]{0,50}(\d[\d.,]{0,10})[^<]{0,200}?\bSell\b[^\d]{0,50}(\d[\d.,]{0,10})'
                matches = list(re.finditer(pattern1, html_n, re.IGNORECASE))
                print(f'Found {len(matches)} matches')
                for m in matches:
                    print(f'  {m.group(1)}: Buy={m.group(2)}, Sell={m.group(3)}')
                
                print('\n=== Testing Pattern 2 (Two numbers) ===')
                pattern2 = r'\b(Gold|Silver)\b[^\d]{0,100}(\d[\d.,]{1,10})[^\d]{1,100}(\d[\d.,]{1,10})'
                matches = list(re.finditer(pattern2, html_n, re.IGNORECASE))
                print(f'Found {len(matches)} matches')
                for i, m in enumerate(matches[:5]):  # Show first 5
                    print(f'  {m.group(1)}: {m.group(2)}, {m.group(3)}')
                
                # Show snippet around gold/silver
                for keyword in ['gold', 'silver']:
                    if keyword in html_n.lower():
                        idx = html_n.lower().find(keyword)
                        snippet = html_n[max(0,idx-150):idx+250]
                        print(f'\n=== Snippet around "{keyword}" ===')
                        print(snippet)
                        break
                    
    except Exception as e:
        print(f'Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_scrape())
