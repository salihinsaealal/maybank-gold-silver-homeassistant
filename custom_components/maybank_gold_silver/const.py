DOMAIN = "maybank_gold_silver"
PLATFORMS = ["sensor"]

SOURCE_URL = (
    "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page"
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_SCAN_INTERVAL_MINUTES = 30

SENSOR_TYPES = {
    "gold_buy": {
        "name": "Gold Buy Price",
        "icon": "mdi:finance",
        "metal": "gold",
        "field": "buy",
        "unit": "MYR/g",
    },
    "gold_sell": {
        "name": "Gold Sell Price",
        "icon": "mdi:finance",
        "metal": "gold",
        "field": "sell",
        "unit": "MYR/g",
    },
    "silver_buy": {
        "name": "Silver Buy Price",
        "icon": "mdi:finance",
        "metal": "silver",
        "field": "buy",
        "unit": "MYR/g",
    },
    "silver_sell": {
        "name": "Silver Sell Price",
        "icon": "mdi:finance",
        "metal": "silver",
        "field": "sell",
        "unit": "MYR/g",
    },
}
