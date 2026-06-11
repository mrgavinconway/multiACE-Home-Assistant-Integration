"""Switches for multiACE."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DRYER_DURATION,
    CONF_DRYER_TEMP,
    DEFAULT_DRYER_DURATION,
    DEFAULT_DRYER_TEMP,
    DOMAIN,
    ace_dryer_duration_option,
    ace_dryer_temp_option,
)
from .coordinator import MultiAceCoordinator
from .entity import MultiAceAceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up multiACE switches."""
    coordinator: MultiAceCoordinator = hass.data[DOMAIN][entry.entry_id]
    ace_indices = [
        ace.get("idx")
        for ace in coordinator.data.get("aces", [])
        if ace.get("idx") is not None
    ] if coordinator.data else []
    async_add_entities(
        MultiAceDryerSwitch(coordinator, entry, ace_index)
        for ace_index in ace_indices
    )


class MultiAceDryerSwitch(MultiAceAceEntity, SwitchEntity):
    """Switch that starts and stops one ACE dryer."""

    def __init__(
        self,
        coordinator: MultiAceCoordinator,
        entry: ConfigEntry,
        ace_index: int,
    ) -> None:
        super().__init__(coordinator, ace_index)
        self._entry = entry
        self._attr_name = f"ACE {ace_index + 1} dryer"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_dryer"

    @property
    def is_on(self) -> bool | None:
        """Return true when drying is active."""
        if not self.ace:
            return None
        status = ((self.ace.get("dryer") or {}).get("status") or "").lower()
        return bool(status and status != "stop")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return dryer details."""
        if not self.ace:
            return {}
        dryer = self.ace.get("dryer") or {}
        return {
            "status": dryer.get("status"),
            "target_temp": dryer.get("target_temp"),
            "duration": dryer.get("duration"),
            "remain_time": dryer.get("remain_time"),
            "configured_temp": self._dryer_temp,
            "configured_duration": self._dryer_duration,
        }

    @property
    def _dryer_temp(self) -> int:
        return int(
            self._entry.options.get(
                ace_dryer_temp_option(self.ace_index),
                self._entry.options.get(CONF_DRYER_TEMP, DEFAULT_DRYER_TEMP),
            )
        )

    @property
    def _dryer_duration(self) -> int:
        return int(
            self._entry.options.get(
                ace_dryer_duration_option(self.ace_index),
                self._entry.options.get(CONF_DRYER_DURATION, DEFAULT_DRYER_DURATION),
            )
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start drying."""
        await self.coordinator.api.async_start_dryer(
            self.ace_index,
            self._dryer_temp,
            self._dryer_duration,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop drying."""
        await self.coordinator.api.async_stop_dryer(self.ace_index)
        await self.coordinator.async_request_refresh()
