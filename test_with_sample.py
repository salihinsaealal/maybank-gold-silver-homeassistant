"""Test parsing with sample HTML from HA logs."""
import re

# From your HA error log - the first 800 chars
sample_html_start = """<html> <head> <META http-equiv="Content-Type" content="text/html; charset=UTF-8"> <title>Gold & Silver Counter Rates | Maybank Malaysia</title> <!--grid-layout--> <!--ls:begin[stylesheet]--> <style type="text/css"> .iw_container { max-width:800px !important; margin-left: auto !important; margin-right: auto !important; } .iw_stretch { min-width: 100% !important; } </style> <link href="/iwov-resources/grid/bootstrap.css" type="text/css" rel="stylesheet"> <!--ls:end[stylesheet]--> <!--ls:begin[meta-keywords]--> <meta name="keywords" content="Maybank,Maybank Malaysia,Maybank Rates,Maybank2u,Online Banking,Internet Banking,Rates,Gold,Silver,gold counter rates,silver counter rates,maybank counter rates"> <!--ls:end[meta-keywords]--> <!--ls:begin[meta-description]--> <meta name="description" cont"""

# This is incomplete, but let's create a realistic sample based on typical bank HTML
sample_html_full = """
<html>
<head>
<title>Gold & Silver Counter Rates | Maybank Malaysia</title>
</head>
<body>
<div class="rates-container">
    <h1>Gold & Silver Counter Rates</h1>
    <table class="rates-table">
        <thead>
            <tr>
                <th>Metal</th>
                <th>Buy (RM/g)</th>
                <th>Sell (RM/g)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Gold</td>
                <td>345.50</td>
                <td>350.75</td>
            </tr>
            <tr>
                <td>Silver</td>
                <td>4.25</td>
                <td>4.50</td>
            </tr>
        </tbody>
    </table>
</div>
</body>
</html>
"""

# Test patterns
_RE_TABLE_PATTERN = re.compile(
    r"<tr[^>]*>.*?\b(Gold|Silver)\b.*?(\d+\.\d{2}).*?(\d+\.\d{2}).*?</tr>",
    re.IGNORECASE | re.DOTALL
)

print("="*60)
print("TESTING WITH SAMPLE HTML (Table Format)")
print("="*60)

matches = list(_RE_TABLE_PATTERN.finditer(sample_html_full))
print(f"\nFound {len(matches)} matches:")
for m in matches:
    print(f"  {m.group(1)}: Buy={m.group(2)}, Sell={m.group(3)}")

if matches:
    print("\n✓ Table pattern WORKS!")
else:
    print("\n✗ Table pattern FAILED")

# Now test with alternative formats
print("\n" + "="*60)
print("TESTING ALTERNATIVE HTML FORMATS")
print("="*60)

# Format 1: Div-based
alt_html_1 = """
<div class="rate-item">
    <span class="metal">Gold</span>
    <span class="buy">Buy: RM 345.50</span>
    <span class="sell">Sell: RM 350.75</span>
</div>
<div class="rate-item">
    <span class="metal">Silver</span>
    <span class="buy">Buy: RM 4.25</span>
    <span class="sell">Sell: RM 4.50</span>
</div>
"""

_RE_BUY_SELL = re.compile(
    r"\b(Gold|Silver)\b.{0,500}?\bBuy\b.{0,100}?(\d+\.\d{2}).{0,500}?\bSell\b.{0,100}?(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

print("\nFormat 1: Div with Buy/Sell labels")
matches = list(_RE_BUY_SELL.finditer(alt_html_1))
print(f"Found {len(matches)} matches:")
for m in matches:
    print(f"  {m.group(1)}: Buy={m.group(2)}, Sell={m.group(3)}")

# Format 2: Simple text
alt_html_2 = """
Gold: 345.50 / 350.75
Silver: 4.25 / 4.50
"""

_RE_TWO_NUMBERS = re.compile(
    r"\b(Gold|Silver)\b.{0,200}?(\d+\.\d{2}).{1,200}?(\d+\.\d{2})",
    re.IGNORECASE | re.DOTALL
)

print("\nFormat 2: Simple text with numbers")
matches = list(_RE_TWO_NUMBERS.finditer(alt_html_2))
print(f"Found {len(matches)} matches:")
for m in matches:
    print(f"  {m.group(1)}: {m.group(2)}, {m.group(3)}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("\nOur regex patterns work for common HTML formats.")
print("The issue is likely:")
print("1. Maybank website timing out from your network")
print("2. OR the actual HTML structure is different")
print("\nSince HA CAN fetch the HTML (you saw the first 800 chars),")
print("we need to see MORE of the actual HTML to understand the structure.")
print("\nCan you:")
print("1. Check HA logs for the full error message with more HTML")
print("2. Or manually visit the page and inspect the HTML source")
