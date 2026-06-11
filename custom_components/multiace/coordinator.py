"""Data coordinator for the multiACE integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MultiAceApi, MultiAceApiError
from .const import DOMAIN, LOGGER, SCAN_INTERVAL_SECONDS


class MultiAceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Keep multiACE state fresh for all entities."""

    def __init__(self, hass: HomeAssistant, api: MultiAceApi) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.async_get_state()
        except MultiAceApiError as err:
            raise UpdateFailed(str(err)) from err

    def ace(self, index: int) -> dict[str, Any] | None:
        """Return one ACE block by index."""
        for ace in self.data.get("aces", []) if self.data else []:
            if ace.get("idx") == index:
                return ace
        return None

    def slot(self, ace_index: int, slot_index: int) -> dict[str, Any] | None:
        """Return one slot block by ACE and slot index."""
        ace = self.ace(ace_index)
        if not ace:
            return None
        for slot in ace.get("slots", []):
            if slot.get("idx") == slot_index:
                return slot
        return None

    def toolhead(self, index: int) -> dict[str, Any] | None:
        """Return one toolhead block by index."""
        for toolhead in self.data.get("toolheads", []) if self.data else []:
            if toolhead.get("idx") == index:
                return toolhead
        return None
