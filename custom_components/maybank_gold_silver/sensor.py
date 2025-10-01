from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any, Dict, Optional

from aiohttp import ClientError

from homeassistant.components.sensor import SensorEntity, SensorStateClass
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

# Shared device info to avoid recreating for each entity
DEVICE_INFO = DeviceInfo(
    identifiers={(DOMAIN, "maybank_gold_silver")},
    name="Maybank Gold & Silver Prices",
    manufacturer="Cikgu Saleh",
    model="Gold & Silver Price Feed",
    configuration_url=SOURCE_URL,
    sw_version="1.0.2",
)

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
    """Set up the Maybank metals sensors via YAML (deprecated, use config flow)."""
    _LOGGER.warning(
        "Setting up Maybank Gold & Silver via YAML is deprecated. "
        "Please use the UI configuration instead."
    )
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    if isinstance(scan_interval, int):
        update_interval = timedelta(seconds=scan_interval)
    else:
        update_interval = scan_interval

    session = async_get_clientsession(hass)

    coordinator = MaybankMetalsCoordinator(hass, session, update_interval)
    
    # Create entities first, then refresh in background to avoid blocking setup
    entities: list[SensorEntity] = []
    for key, desc in SENSOR_TYPES.items():
        entities.append(MaybankMetalPriceSensor(coordinator, key, desc))

    add_entities(entities)
    
    # Start background refresh without blocking
    await coordinator.async_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry (UI)."""
    # Reuse coordinator if already exists, otherwise create new one
    if entry.entry_id not in hass.data.setdefault(DOMAIN, {}):
        session = async_get_clientsession(hass)
        update_interval = timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES)
        coordinator = MaybankMetalsCoordinator(hass, session, update_interval)
        # Store coordinator for lifecycle management
        hass.data[DOMAIN][entry.entry_id] = coordinator
    else:
        coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create entities first
    entities: list[SensorEntity] = []
    for key, desc in SENSOR_TYPES.items():
        entities.append(MaybankMetalPriceSensor(coordinator, key, desc))

    async_add_entities(entities)
    
    _LOGGER.info("Maybank Gold & Silver: Entities added, starting background refresh")
    # Start background refresh without blocking setup
    await coordinator.async_refresh()
    _LOGGER.info("Maybank Gold & Silver: Initial refresh completed")


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
        """Fetch data from Maybank with proper error handling."""
        _LOGGER.debug("Maybank metals: starting fetch from source")
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
            # Browser client hints and fetch metadata to better mimic a real browser
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }
        
        try:
            async with self._session.get(SOURCE_URL, headers=headers, timeout=30, allow_redirects=True) as resp:
                if resp.status != 200:
                    _LOGGER.error("Maybank metals: HTTP status %s", resp.status)
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
                _LOGGER.debug("Maybank metals: fetching from %s (status %s)", final_url, resp.status)
                html = await resp.text()
                _LOGGER.debug("Maybank metals: fetched %d chars of HTML", len(html))
        except UpdateFailed:
            # Re-raise UpdateFailed as-is
            raise
        except (asyncio.TimeoutError, ClientError) as err:
            # Retry once with SSL verification disabled, only for the strict Maybank host
            _LOGGER.info("Maybank metals: request error on first attempt: %s, retrying with SSL disabled", err)
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = f"request_error: {err}"
            try:
                async with self._session.get(
                    SOURCE_URL,
                    headers=headers,
                    timeout=30,
                    allow_redirects=True,
                    ssl=False,
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error("Maybank metals: HTTP status (ssl=False) %s", resp.status)
                        raise UpdateFailed(f"HTTP {resp.status}")
                    final_url = resp.url
                    final_host = getattr(final_url, "host", "")
                    final_path = getattr(final_url, "path", "")
                    if not final_host.endswith("maybank2u.com.my") or "gold_and_silver" not in final_path:
                        raise UpdateFailed(
                            f"Unexpected redirect to {final_url} (ssl=False); refusing to parse as per user requirement"
                        )
                    _LOGGER.debug("Maybank metals: retry (ssl=False) from %s (status %s)", final_url, resp.status)
                    html = await resp.text()
                    _LOGGER.debug("Maybank metals: fetched %d chars of HTML (ssl=False)", len(html))
            except Exception as err2:  # any failure in retry
                msg = f"request_error_retry: {err2}"
                self.hass.data.setdefault(DOMAIN, {})["last_error"] = msg
                _LOGGER.error("Maybank metals: request error on retry: %s", err2)
                raise UpdateFailed(f"Request error: {err2}") from err2
        except Exception as err:
            # Catch-all to prevent any unhandled exception from crashing HA
            msg = f"Unexpected error: {type(err).__name__}: {err}"
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = msg
            _LOGGER.error("Maybank metals: %s", msg)
            raise UpdateFailed(msg) from err
        
        try:
            _LOGGER.debug("Maybank metals: parsing HTML for prices")
            prices = _parse_prices(html)
            if not prices:
                # Log a small sanitized snippet to help troubleshoot without spamming logs
                snippet = re.sub(r"\s+", " ", html)[:800]
                self.hass.data.setdefault(DOMAIN, {})["last_error"] = "parse_failed"
                _LOGGER.error(
                    "Maybank metals parsing returned no data. First 800 chars: %s",
                    snippet,
                )
                raise UpdateFailed("Failed to parse metals prices from Maybank page")
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = None
            _LOGGER.info("Maybank metals: successfully parsed prices %s", prices)
            return prices
        except UpdateFailed:
            raise
        except Exception as err:
            # Catch parsing errors
            msg = f"Parse error: {type(err).__name__}: {err}"
            self.hass.data.setdefault(DOMAIN, {})["last_error"] = msg
            _LOGGER.error("Maybank metals: %s", msg)
            raise UpdateFailed(msg) from err


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
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{DOMAIN}_{self._metal}_{self._field}"
        self._attr_device_info = DEVICE_INFO
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
        last_error = self.hass.data.get(DOMAIN, {}).get("last_error")
        
        base_attrs = {
            "source": SOURCE_URL,
            "metal": self._metal,
            "type": self._field,
            "last_update_success": self.coordinator.last_update_success,
            "last_error": last_error or "None",
        }
        
        if not metal_data:
            # Add diagnostic info when unavailable
            base_attrs["status"] = "unavailable"
            base_attrs["help"] = "Check HA logs for 'maybank_gold_silver' errors"
            return base_attrs
            
        return base_attrs


# ---------- Parsing helpers ----------

# Optimized regex patterns to avoid catastrophic backtracking
# Strategy A: Simple pattern for Buy/Sell with limited lookahead
_RE_BUY_SELL_ROW = re.compile(
    r"\b(Gold|Silver)\b[^<]{0,200}?\bBuy\b[^\d]{0,50}(\d[\d.,]{0,10})[^<]{0,200}?\bSell\b[^\d]{0,50}(\d[\d.,]{0,10})",
    re.IGNORECASE
)

# Strategy B: Two numbers after metal label with limited search window
_RE_METAL_TWO_NUMBERS = re.compile(
    r"\b(Gold|Silver)\b[^\d]{0,100}(\d[\d.,]{1,10})[^\d]{1,100}(\d[\d.,]{1,10})",
    re.IGNORECASE
)

# Strategy C: With currency marker - simplified
_RE_WITH_CURRENCY = re.compile(
    r"\b(Gold|Silver)\b.{0,200}?(?:RM|MYR)\s*(\d[\d.,]{1,10})[^\d]{1,100}(?:RM|MYR)\s*(\d[\d.,]{1,10})",
    re.IGNORECASE
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
    # Normalize whitespace inline - more efficient than full HTML copy
    html_normalized = re.sub(r"\s+", " ", html)
    prices: Dict[str, Dict[str, float]] = {"gold": {}, "silver": {}}

    # Try Strategy A first (most reliable)
    match = _RE_BUY_SELL_ROW.search(html_normalized)
    if match:
        for m in _RE_BUY_SELL_ROW.finditer(html_normalized):
            metal = m.group(1).lower()
            buy_val = m.group(2)
            sell_val = m.group(3)
            if buy_val and sell_val:
                prices[metal]["buy"] = _to_float(buy_val)
                prices[metal]["sell"] = _to_float(sell_val)
    
    # Only try Strategy B if Strategy A didn't find complete data
    if not (prices["gold"].get("buy") and prices["gold"].get("sell")):
        for m in _RE_METAL_TWO_NUMBERS.finditer(html_normalized):
            metal = m.group(1).lower()
            first = m.group(2)
            second = m.group(3)
            if first and second and "buy" not in prices[metal]:
                prices[metal]["buy"] = _to_float(first)
                prices[metal]["sell"] = _to_float(second)

    # Only try Strategy C if still no complete data
    if not (prices["gold"].get("buy") and prices["gold"].get("sell")):
        for m in _RE_WITH_CURRENCY.finditer(html_normalized):
            metal = m.group(1).lower()
            first = m.group(2)
            second = m.group(3)
            if first and second:
                prices[metal]["buy"] = prices[metal].get("buy") or _to_float(first)
                prices[metal]["sell"] = prices[metal].get("sell") or _to_float(second)

    # Validate and clean up
    for metal in list(prices.keys()):
        if not prices[metal].get("buy") or not prices[metal].get("sell"):
            prices.pop(metal, None)

    return prices
