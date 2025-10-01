# Maybank Gold & Silver Prices (Home Assistant)

**Version:** 1.0.0  
**Developer:** Cikgu Saleh

Home Assistant custom integration that provides sensors for Maybank Malaysia Gold and Silver prices (Buy/Sell) scraped from the public rates page.

**Source:** https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page

## Features
- ✅ Device-based integration for intuitive organization
- ✅ UI-based setup (Config Flow) - no YAML required
- ✅ Automatic updates every 30 minutes
- ✅ All entities grouped under a single device
- ✅ No external APIs or authentication needed

## Device & Entities

The integration creates a single device: **Maybank Gold & Silver Prices**

All entities are grouped under this device:
- `sensor.gold_buy_price` (MYR/g)
- `sensor.gold_sell_price` (MYR/g)
- `sensor.silver_buy_price` (MYR/g)
- `sensor.silver_sell_price` (MYR/g)

## Installation
1. Copy this folder to your Home Assistant `config/custom_components/` directory as `maybank_gold_silver/`.
2. Restart Home Assistant.
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Maybank Gold & Silver" and configure it through the UI.

## Notes
- Scraping is performed with aiohttp using a browser-like User-Agent and resilient regex parsing.
- If the website markup changes significantly, parsing may fail; check logs for messages from `custom_components.maybank_gold_silver` and open an issue.
- Prices are expressed in MYR per gram, matching the site presentation.
- Error notifications will appear in Home Assistant if data fetching fails.

## Troubleshooting
- Check Home Assistant logs for entries from `custom_components.maybank_gold_silver`.
- Verify that the source page is reachable from your Home Assistant host.
- Check the device page in Home Assistant for diagnostic information.

## Changelog

### Version 1.0.0
- ✨ Device-based integration for better entity organization
- ✨ All entities now grouped under a single device
- ✨ UI-based configuration with Config Flow
- ✨ Improved device information with software version tracking
- ✨ Enhanced error handling with persistent notifications
- 🔧 Updated to stable v1.0.0 release

## Developer
**Cikgu Saleh** - [@salihinsaealal](https://github.com/salihinsaealal)
