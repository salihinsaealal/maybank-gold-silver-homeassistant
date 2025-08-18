# Maybank Gold & Silver (Home Assistant)

Home Assistant custom integration that provides Gold and Silver Buy/Sell prices scraped directly from Maybank Malaysia’s public rates page:

https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page

- No external APIs or keys
- UI-based setup (no YAML required)
- Four sensors: gold/silver, buy/sell (MYR/g)

## Installation

### Via HACS (Custom Repository)
1. Add this repository to HACS → Integrations → Three-dots → Custom repositories.
2. Category: Integration. Add.
3. Find “Maybank Gold & Silver” in HACS and install.
4. Restart Home Assistant.
5. Go to Settings → Devices & Services → Add Integration → “Maybank Gold & Silver”.

### Manual
1. Copy `custom_components/maybank_gold_silver/` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration from Settings → Devices & Services.

## Entities
- `sensor.gold_buy_price`
- `sensor.gold_sell_price`
- `sensor.silver_buy_price`
- `sensor.silver_sell_price`

All values are in MYR per gram. Attributes include the data source URL.

## Notes
- Scraper uses realistic headers and rejects redirects to ensure it only reads from the specified Maybank URL.
- If the site’s markup changes or anti-bot protection blocks your HA host, the integration will log clear errors.

## Support & Issues
Please open issues on the repository Issues page.

## License
MIT
