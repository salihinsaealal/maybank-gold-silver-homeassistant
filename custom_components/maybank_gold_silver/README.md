# Maybank Gold & Silver Prices (Home Assistant)

Home Assistant custom integration that provides sensors for Maybank Malaysia Gold and Silver prices (Buy/Sell) scraped from the public rates page.

Source: https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page

## Entities
- sensor.gold_buy_price (MYR/g)
- sensor.gold_sell_price (MYR/g)
- sensor.silver_buy_price (MYR/g)
- sensor.silver_sell_price (MYR/g)

## Installation
1. Copy this folder to your Home Assistant `config/custom_components/` directory as `maybank_gold_silver/`.
2. Restart Home Assistant.

## Configuration (YAML)
Add to your `configuration.yaml`:

```yaml
sensor:
  - platform: maybank_gold_silver
    # Optional: default is 30 minutes
    scan_interval: '00:30:00'
```

Note: This is a YAML-only platform setup. There is no UI config flow.

## Notes
- Scraping is performed with aiohttp using a browser-like User-Agent and resilient regex parsing.
- If the website markup changes significantly, parsing may fail; check logs for messages from `maybank_metals` and open an issue.
- Prices are expressed in MYR per gram, matching the site presentation.

## Troubleshooting
- Check Home Assistant logs for entries from `maybank_metals`.
- Increase `scan_interval` to reduce request frequency if rate-limited.
- Verify that the source page is reachable from your Home Assistant host.
