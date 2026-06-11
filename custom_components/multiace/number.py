"""Number entities for multiACE."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
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
    """Set up multiACE number entities."""
    coordinator: MultiAceCoordinator = hass.data[DOMAIN][entry.entry_id]
    ace_indices = [
        ace.get("idx")
        for ace in coordinator.data.get("aces", [])
        if ace.get("idx") is not None
    ] if coordinator.data else []

    entities: list[NumberEntity] = []
    for ace_index in ace_indices:
        entities.append(MultiAceDryerDurationNumber(coordinator, entry, ace_index))
        entities.append(MultiAceDryerTemperatureNumber(coordinator, entry, ace_index))
    async_add_entities(entities)


class MultiAceOptionsNumber(MultiAceAceEntity, NumberEntity):
    """Base class for a per-ACE option-backed number."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: MultiAceCoordinator,
        entry: ConfigEntry,
        ace_index: int,
        option_key: str,
        default_value: int,
    ) -> None:
        super().__init__(coordinator, ace_index)
        self._entry = entry
        self._option_key = option_key
        self._default_value = default_value

    @property
    def native_value(self) -> int:
        """Return the configured value."""
        return int(self._entry.options.get(self._option_key, self._default_value))

    async def async_set_native_value(self, value: float) -> None:
        """Persist the configured value in the config entry options."""
        new_options: dict[str, Any] = dict(self._entry.options)
        new_options[self._option_key] = int(value)
        self.hass.config_entries.async_update_entry(
            self._entry,
            options=new_options,
        )
        self.async_write_ha_state()


class MultiAceDryerDurationNumber(MultiAceOptionsNumber):
    """Default dryer duration for one ACE."""

    _attr_native_min_value = 1
    _attr_native_max_value = 1440
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(
        self,
        coordinator: MultiAceCoordinator,
        entry: ConfigEntry,
        ace_index: int,
    ) -> None:
        super().__init__(
            coordinator,
            entry,
            ace_index,
            ace_dryer_duration_option(ace_index),
            DEFAULT_DRYER_DURATION,
        )
        self._attr_name = f"ACE {ace_index + 1} dryer duration"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_dryer_duration"


class MultiAceDryerTemperatureNumber(MultiAceOptionsNumber):
    """Default dryer target temperature for one ACE."""

    _attr_native_min_value = 35
    _attr_native_max_value = 70
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: MultiAceCoordinator,
        entry: ConfigEntry,
        ace_index: int,
    ) -> None:
        super().__init__(
            coordinator,
            entry,
            ace_index,
            ace_dryer_temp_option(ace_index),
            DEFAULT_DRYER_TEMP,
        )
        self._attr_name = f"ACE {ace_index + 1} dryer temperature"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_dryer_temperature"
