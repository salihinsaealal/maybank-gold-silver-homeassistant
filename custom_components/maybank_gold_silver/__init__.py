"""Maybank Gold & Silver integration (config entry based)."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLATFORMS, SOURCE_URL


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration (no YAML entities)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry (UI)."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "maybank_gold_silver")},
        name="Maybank Gold & Silver Prices",
        manufacturer="Cikgu Saleh",
        model="Gold & Silver Price Feed",
        sw_version="1.0.2",
        configuration_url=SOURCE_URL,
        entry_type=dr.DeviceEntryType.SERVICE,
    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and entry.entry_id in hass.data.get(DOMAIN, {}):
        # Clean up coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
