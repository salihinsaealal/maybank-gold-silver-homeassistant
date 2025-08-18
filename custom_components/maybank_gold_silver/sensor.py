from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any, Dict, Optional

from aiohttp import ClientError

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from .const import (
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    SENSOR_TYPES,
    SOURCE_URL,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL, default=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES)
        ): vol.Any(cv.time_period, cv.positive_timedelta),
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Maybank metals sensors via YAML."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    if isinstance(scan_interval, int):
        update_interval = timedelta(seconds=scan_interval)
    else:
        update_interval = scan_interval

    session = async_get_clientsession(hass)

    coordinator = MaybankMetalsCoordinator(hass, session, update_interval)
    # Schedule initial refresh in background; don't block entity creation
    hass.async_create_task(coordinator.async_config_entry_first_refresh())

    entities: list[SensorEntity] = []
    for key, desc in SENSOR_TYPES.items():
        entities.append(MaybankMetalPriceSensor(coordinator, key, desc))

    add_entities(entities)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry (UI)."""
    session = async_get_clientsession(hass)
    update_interval = timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES)
    coordinator = MaybankMetalsCoordinator(hass, session, update_interval)
    # Schedule initial refresh in background; don't block entity creation
    hass.async_create_task(coordinator.async_config_entry_first_refresh())

    entities: list[SensorEntity] = []
    for key, desc in SENSOR_TYPES.items():
        entities.append(MaybankMetalPriceSensor(coordinator, key, desc))

    async_add_entities(entities)


class MaybankMetalsCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator to fetch and parse metals prices from Maybank page."""

    def __init__(self, hass: HomeAssistant, session, update_interval: timedelta) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Maybank Gold & Silver Prices",
            update_interval=update_interval,
        )
        self._session = session

    async def _async_update_data(self) -> Dict[str, Any]:
        _LOGGER.warning("Maybank metals: starting fetch from source")
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-MY,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": SOURCE_URL,
            "Origin": "https://www.maybank2u.com.my",
        }
        try:
            async with self._session.get(SOURCE_URL, headers=headers, timeout=60, allow_redirects=True) as resp:
                if resp.status != 200:
                    _LOGGER.warning("Maybank metals: HTTP status %s", resp.status)
                    raise UpdateFailed(f"HTTP {resp.status}")
                # Enforce that the final URL is still the Maybank page we were told to use
                final_url = resp.url
                final_host = getattr(final_url, "host", "")
                final_path = getattr(final_url, "path", "")
                # Allow any subdomain of maybank2u.com.my (e.g., www, origin variations) and flexible path
                if not final_host.endswith("maybank2u.com.my") or "gold_and_silver" not in final_path:
                    raise UpdateFailed(
                        f"Unexpected redirect to {final_url}; refusing to parse as per user requirement"
                    )
                _LOGGER.warning("Maybank metals: fetching from %s (status %s)", final_url, resp.status)
                html = await resp.text()
                _LOGGER.warning("Maybank metals: fetched %d chars of HTML", len(html))
        except (asyncio.TimeoutError, ClientError) as err:
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = f"request_error: {err}"
            _LOGGER.warning("Maybank metals: request error %s", err)
            raise UpdateFailed(f"Request error: {err}") from err

        _LOGGER.warning("Maybank metals: parsing HTML for prices")
        prices = _parse_prices(html)
        if not prices:
            # Log a small sanitized snippet to help troubleshoot without spamming logs
            snippet = re.sub(r"\s+", " ", html)[:800]
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = "parse_failed"
            _LOGGER.warning(
                "Maybank metals parsing returned no data. First 800 chars: %s",
                snippet,
            )
            raise UpdateFailed("Failed to parse metals prices from Maybank page")
        self.hass.data.setdefault(DOMAIN, {})["last_error"] = None
        _LOGGER.warning("Maybank metals: parsed prices %s", prices)
        return prices


class MaybankMetalPriceSensor(CoordinatorEntity[MaybankMetalsCoordinator], SensorEntity):
    """Sensor entity representing one metal price (buy/sell)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MaybankMetalsCoordinator, key: str, desc: Dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._key = key
        self._desc = desc
        self._metal = desc["metal"]
        self._field = desc["field"]
        self._attr_name = desc["name"]
        self._attr_icon = desc.get("icon")
        self._attr_native_unit_of_measurement = desc.get("unit", "MYR/g")
        self._attr_unique_id = f"{DOMAIN}_{self._metal}_{self._field}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "maybank_gold_silver")},
            name="Maybank Gold & Silver Prices",
            manufacturer="Maybank",
            model="Gold & Silver",
            configuration_url=SOURCE_URL,
        )
        self._attr_suggested_display_precision = 2

    @property
    def native_value(self) -> Optional[float]:
        data = self.coordinator.data or {}
        metal_data = data.get(self._metal)
        if not metal_data:
            return None
        value = metal_data.get(self._field)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        data = self.coordinator.data or {}
        metal_data = data.get(self._metal)
        if not metal_data:
            # still surface diagnostics if present
            diag = self.hass.data.get(DOMAIN, {}).get("last_error")
            return {
                "source": SOURCE_URL,
                "metal": self._metal,
                "type": self._field,
                "last_error": diag,
            }
        return {
            "source": SOURCE_URL,
            "metal": self._metal,
            "type": self._field,
            "last_error": self.hass.data.get(DOMAIN, {}).get("last_error"),
        }

    async def async_added_to_hass(self) -> None:
        # Trigger an immediate refresh attempt when entity is added
        await self.coordinator.async_request_refresh()


# ---------- Parsing helpers ----------

# Normalize whitespace to make regex simpler across minified or formatted HTML
def _normalize_html(html: str) -> str:
    return re.sub(r"\s+", " ", html)

# Several regex strategies to make parsing resilient to minor site structure changes.
# Strategy A: Explicit Buy/Sell headings near the metal name
_RE_BUY_SELL_ROW = re.compile(
    r"(?is)\b(Gold|Silver)\b[^<]*?(?:</?\w+[^>]*>[^<]*)*?\bBuy\b[^\d]*(\d[\d.,]*)(?:[^<]*?(?:</?\w+[^>]*>[^<]*)*?)\bSell\b[^\d]*(\d[\d.,]*)"
)

# Strategy B: Table row where two numbers follow the metal label; often presented as RM/g
_RE_METAL_TWO_NUMBERS = re.compile(
    r"(?is)\b(Gold|Silver)\b[^\d]*(\d[\d.,]*)[^\d]+(\d[\d.,]*)"
)

# Strategy C: Include currency label RM explicitly if present
_RE_WITH_CURRENCY = re.compile(
    r"(?is)\b(Gold|Silver)\b.*?(?:RM|MYR)\s*(\d[\d.,]*)[^\d]+(?:RM|MYR)\s*(\d[\d.,]*)"
)


def _to_float(val: str) -> float:
    return float(val.replace(",", "").strip())


def _parse_prices(html: str) -> Dict[str, Dict[str, float]]:
    """Parse metals prices from Maybank HTML.

    Returns example structure:
    {
        'gold': {'buy': 3.1, 'sell': 3.3},
        'silver': {'buy': 2.9, 'sell': 3.0}
    }
    """
    html_n = _normalize_html(html)
    prices: Dict[str, Dict[str, float]] = {"gold": {}, "silver": {}}

    # Strategy A: Metal with explicit Buy then Sell labels
    for m in _RE_BUY_SELL_ROW.finditer(html_n):
        metal = m.group(1).lower()
        buy_val = m.group(2)
        sell_val = m.group(3)
        if buy_val:
            prices[metal]["buy"] = _to_float(buy_val)
        if sell_val:
            prices[metal]["sell"] = _to_float(sell_val)

    # Strategy B: Two numbers after metal label (assume first=buy, second=sell)
    for m in _RE_METAL_TWO_NUMBERS.finditer(html_n):
        metal = m.group(1).lower()
        first = m.group(2)
        second = m.group(3)
        if first and "buy" not in prices[metal]:
            prices[metal]["buy"] = _to_float(first)
        if second and "sell" not in prices[metal]:
            prices[metal]["sell"] = _to_float(second)

    # Strategy C: With currency marker
    for m in _RE_WITH_CURRENCY.finditer(html_n):
        metal = m.group(1).lower()
        first = m.group(2)
        second = m.group(3)
        prices.setdefault(metal, {})
        if first:
            prices[metal]["buy"] = prices[metal].get("buy") or _to_float(first)
        if second:
            prices[metal]["sell"] = prices[metal].get("sell") or _to_float(second)

    # Validate
    for metal in list(prices.keys()):
        if not prices[metal].get("buy") or not prices[metal].get("sell"):
            # remove incomplete entries
            prices.pop(metal, None)

    return prices
