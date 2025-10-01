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
    # MIGA-i sensors - numbered prefixes for deterministic ordering (1=100g+, 2=<100g)
    "miga_1_buy_100g_plus": {
        "name": "1. Buy 100g+",
        "icon": "mdi:cash-plus",
        "metal": "miga_100g",
        "field": "buy",
        "unit": "MYR/g",
        "device": "miga",
    },
    "miga_1_sell_100g_plus": {
        "name": "2. Sell 100g+",
        "icon": "mdi:cash-minus",
        "metal": "miga_100g",
        "field": "sell",
        "unit": "MYR/g",
        "device": "miga",
    },
    "miga_2_buy_below_100g": {
        "name": "3. Buy <100g",
        "icon": "mdi:cash-plus",
        "metal": "miga_below100g",
        "field": "buy",
        "unit": "MYR/g",
        "device": "miga",
    },
    "miga_2_sell_below_100g": {
        "name": "4. Sell <100g",
        "icon": "mdi:cash-minus",
        "metal": "miga_below100g",
        "field": "sell",
        "unit": "MYR/g",
        "device": "miga",
    },
    # Gold sensors (second - regular device)
    "gold_buy": {
        "name": "Gold Buy Price",
        "icon": "mdi:currency-usd",
        "metal": "gold",
        "field": "buy",
        "unit": "MYR/g",
        "device": "regular",
    },
    "gold_sell": {
        "name": "Gold Sell Price",
        "icon": "mdi:currency-usd-off",
        "metal": "gold",
        "field": "sell",
        "unit": "MYR/g",
        "device": "regular",
    },
    # Silver sensors (third - regular device)
    "silver_buy": {
        "name": "Silver Buy Price",
        "icon": "mdi:currency-usd",
        "metal": "silver",
        "field": "buy",
        "unit": "MYR/g",
        "device": "regular",
    },
    "silver_sell": {
        "name": "Silver Sell Price",
        "icon": "mdi:currency-usd-off",
        "metal": "silver",
        "field": "sell",
        "unit": "MYR/g",
        "device": "regular",
    },
}
