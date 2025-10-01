# Maybank Gold & Silver (Home Assistant)

**Version:** 1.0.0  
**Developer:** Cikgu Saleh

Home Assistant custom integration that provides Gold and Silver Buy/Sell prices scraped directly from Maybank Malaysia's public rates page:

https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page

## Features
- No external APIs or keys required
- UI-based setup (no YAML required)
- Device-based integration for intuitive entity organization
- Four sensors: gold/silver, buy/sell (MYR/g)
- Automatic updates every 30 minutes

## Installation

### Via HACS (Custom Repository)
1. Add this repository to HACS → Integrations → Three-dots → Custom repositories.
2. Category: Integration. Add.
3. Find "Maybank Gold & Silver" in HACS and install.
4. Restart Home Assistant.
5. Go to Settings → Devices & Services → Add Integration → "Maybank Gold & Silver".

### Manual
1. Copy `custom_components/maybank_gold_silver/` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration from Settings → Devices & Services.
## Device & Entities

The integration creates a single device: **Maybank Gold & Silver Prices**

All entities are grouped under this device for easy management:
- `sensor.gold_buy_price` - Gold buying price (MYR/g)
- `sensor.gold_sell_price` - Gold selling price (MYR/g)
- `sensor.silver_buy_price` - Silver buying price (MYR/g)
- `sensor.silver_sell_price` - Silver selling price (MYR/g)

All values are in MYR per gram. Attributes include the data source URL and last update status.

## Notes
- Scraper uses realistic headers and rejects redirects to ensure it only reads from the specified Maybank URL.
- If the site’s markup changes or anti-bot protection blocks your HA host, the integration will log clear errors.

## Changelog

### Version 1.0.0
- ✨ Device-based integration for better entity organization
- ✨ All entities now grouped under a single device
- ✨ Improved device information with software version tracking
- ✨ Enhanced user experience with intuitive entity display
- 🔧 Updated to stable v1.0.0 release

## Support & Issues
Please open issues on the repository Issues page.

## Developer
**Cikgu Saleh** - [@salihinsaealal](https://github.com/salihinsaealal)

## License
MIT
