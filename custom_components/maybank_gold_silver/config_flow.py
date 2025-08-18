from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN

import voluptuous as vol

DATA_SCHEMA = vol.Schema({})

class MaybankGoldSilverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Maybank Gold & Silver."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step initiated by the user."""
        # Single instance only
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is None:
            # No settings required; just confirm add
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        return self.async_create_entry(title="Maybank Gold & Silver", data={})

    async def async_step_import(self, user_input):
        """Import from configuration.yaml (not used, but kept for completeness)."""
        return await self.async_step_user(user_input)
