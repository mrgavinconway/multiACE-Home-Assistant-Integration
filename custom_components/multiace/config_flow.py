"""Config flow for multiACE."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MultiAceApi, MultiAceApiAuthError, MultiAceApiConnectionError, MultiAceApiError
from .const import (
    CONF_BASE_URL,
    CONF_DRYER_DURATION,
    CONF_DRYER_TEMP,
    DEFAULT_BASE_URL,
    DEFAULT_DRYER_DURATION,
    DEFAULT_DRYER_TEMP,
    DOMAIN,
)


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    api = MultiAceApi(async_get_clientsession(hass), data[CONF_BASE_URL])
    state = await api.async_get_state()
    version = {}
    try:
        version = await api.async_get_version()
    except MultiAceApiError:
        pass

    title = version.get("printer", {}).get("device_name") or "multiACE"
    return {
        CONF_NAME: title,
        CONF_BASE_URL: api.base_url,
        "device_count": state.get("device_count", 0),
    }


class MultiAceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for multiACE."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _validate_input(self.hass, user_input)
            except MultiAceApiAuthError:
                errors["base"] = "auth"
            except MultiAceApiConnectionError:
                errors["base"] = "cannot_connect"
            except MultiAceApiError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info[CONF_BASE_URL])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info[CONF_NAME],
                    data={CONF_BASE_URL: info[CONF_BASE_URL]},
                    options={
                        CONF_DRYER_TEMP: DEFAULT_DRYER_TEMP,
                        CONF_DRYER_DURATION: DEFAULT_DRYER_DURATION,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return MultiAceOptionsFlow(config_entry)


class MultiAceOptionsFlow(config_entries.OptionsFlow):
    """Handle multiACE options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DRYER_TEMP,
                        default=options.get(CONF_DRYER_TEMP, DEFAULT_DRYER_TEMP),
                    ): vol.All(vol.Coerce(int), vol.Range(min=35, max=70)),
                    vol.Required(
                        CONF_DRYER_DURATION,
                        default=options.get(CONF_DRYER_DURATION, DEFAULT_DRYER_DURATION),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
        )
