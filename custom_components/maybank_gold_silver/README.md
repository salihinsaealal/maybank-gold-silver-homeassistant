# Maybank Gold & Silver Prices (Home Assistant)

**Version:** 1.0.2  
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

### Version 1.0.2 (Parsing Fix - 2025-10-01)
- 🐛 **FIXED:** Parsing failure - updated regex patterns to match current Maybank HTML structure
- ✨ Added table-based parsing strategy (Strategy D) for better reliability
- ✨ Enhanced regex patterns with DOTALL flag for multi-line matching
- ✨ Improved error logging with HTML context when parsing fails
- ✨ Added diagnostic attributes to sensors (last_error, last_update_success)
- ⚡ Increased timeout to 30s for better reliability

### Version 1.0.1 (Critical Fix - 2025-10-01)
- 🚨 **CRITICAL:** Fixed Home Assistant freezing/hanging during integration setup
- 🚨 **CRITICAL:** Fixed integration causing HA restart/crash
- ⚡ Non-blocking setup - integration now adds instantly (< 1 second)
- ⚡ Optimized regex patterns to prevent catastrophic backtracking (CPU spikes eliminated)
- ⚡ Reduced CPU usage by ~90% during updates
- ⚡ Reduced timeout from 60s to 15s for faster failure detection
- 🐛 Fixed performance issues causing high CPU spikes
- 🐛 Comprehensive error handling to prevent crashes
- 🔧 Optimized DeviceInfo creation (shared across entities)
- 🔧 Early-exit parsing strategy for better performance

**Important:** If you experienced HA freezing with v1.0.0, please update immediately!

### Version 1.0.0
- ✨ Device-based integration for better entity organization
- ✨ All entities now grouped under a single device
- ✨ UI-based configuration with Config Flow
- ✨ Improved device information with software version tracking
- ✨ Enhanced error handling with persistent notifications
- 🔧 Updated to stable v1.0.0 release

## Developer
**Cikgu Saleh** - [@salihinsaealal](https://github.com/salihinsaealal)
