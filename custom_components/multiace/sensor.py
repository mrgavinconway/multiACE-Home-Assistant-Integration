"""Sensors for multiACE."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SLOT_COUNT
from .coordinator import MultiAceCoordinator
from .entity import MultiAceAceEntity, MultiAceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up multiACE sensors."""
    coordinator: MultiAceCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        MultiAceStateSensor(coordinator, "printer_state", "Printer state"),
        MultiAceStateSensor(coordinator, "ace_status", "ACE status"),
        MultiAceStateSensor(coordinator, "mode", "Mode"),
        MultiAceStateSensor(coordinator, "active_device", "Active ACE"),
    ]

    for ace_data in coordinator.data.get("aces", []) if coordinator.data else []:
        ace = ace_data.get("idx")
        if ace is None:
            continue
        entities.extend(
            [
                MultiAceTemperatureSensor(coordinator, ace),
                MultiAceHumiditySensor(coordinator, ace),
                MultiAceDryerStatusSensor(coordinator, ace),
            ]
        )
        slot_indices = [
            slot.get("idx")
            for slot in ace_data.get("slots", [])
            if slot.get("idx") is not None
        ]
        for slot in slot_indices or range(SLOT_COUNT):
            entities.append(MultiAceSlotSensor(coordinator, ace, slot))

    for toolhead in range(SLOT_COUNT):
        entities.append(MultiAceToolheadSensor(coordinator, toolhead))

    async_add_entities(entities)


class MultiAceStateSensor(MultiAceEntity, SensorEntity):
    """Top-level multiACE state sensor."""

    def __init__(self, coordinator: MultiAceCoordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.api.base_url}_{key}"

    @property
    def native_value(self) -> Any:
        """Return the state value."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self._key)


class MultiAceTemperatureSensor(MultiAceAceEntity, SensorEntity):
    """ACE temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MultiAceCoordinator, ace_index: int) -> None:
        super().__init__(coordinator, ace_index)
        self._attr_name = f"ACE {ace_index + 1} temperature"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_temperature"

    @property
    def native_value(self) -> Any:
        """Return the ACE temperature."""
        return self.ace.get("temp") if self.ace else None


class MultiAceHumiditySensor(MultiAceAceEntity, SensorEntity):
    """ACE humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MultiAceCoordinator, ace_index: int) -> None:
        super().__init__(coordinator, ace_index)
        self._attr_name = f"ACE {ace_index + 1} humidity"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_humidity"

    @property
    def native_value(self) -> Any:
        """Return the ACE humidity."""
        return self.ace.get("humidity") if self.ace else None


class MultiAceDryerStatusSensor(MultiAceAceEntity, SensorEntity):
    """ACE dryer status sensor."""

    def __init__(self, coordinator: MultiAceCoordinator, ace_index: int) -> None:
        super().__init__(coordinator, ace_index)
        self._attr_name = f"ACE {ace_index + 1} dryer status"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_dryer_status"

    @property
    def native_value(self) -> str | None:
        """Return the dryer status."""
        if not self.ace:
            return None
        return (self.ace.get("dryer") or {}).get("status")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return dryer details."""
        if not self.ace:
            return {}
        dryer = self.ace.get("dryer") or {}
        return {
            "target_temp": dryer.get("target_temp"),
            "duration": dryer.get("duration"),
            "remain_time": dryer.get("remain_time"),
        }


class MultiAceSlotSensor(MultiAceEntity, SensorEntity):
    """Filament slot sensor."""

    def __init__(self, coordinator: MultiAceCoordinator, ace_index: int, slot_index: int) -> None:
        super().__init__(coordinator)
        self.ace_index = ace_index
        self.slot_index = slot_index
        self._attr_name = f"ACE {ace_index + 1} slot {slot_index + 1}"
        self._attr_unique_id = f"{coordinator.api.base_url}_ace_{ace_index}_slot_{slot_index}"

    @property
    def available(self) -> bool:
        """Return if this slot currently exists."""
        return super().available and self.coordinator.slot(self.ace_index, self.slot_index) is not None

    @property
    def native_value(self) -> str | None:
        """Return a concise filament label for the slot."""
        slot = self.coordinator.slot(self.ace_index, self.slot_index)
        if not slot:
            return None
        if slot.get("state") == "empty":
            return "empty"
        parts = [slot.get("material"), slot.get("brand"), slot.get("sku")]
        return " ".join(str(part) for part in parts if part) or slot.get("state")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return slot metadata."""
        slot = self.coordinator.slot(self.ace_index, self.slot_index)
        if not slot:
            return {}
        loaded_toolhead = None
        for wiring in self.coordinator.data.get("wiring", []):
            if wiring.get("ace") == self.ace_index and wiring.get("slot") == self.slot_index:
                loaded_toolhead = wiring.get("toolhead")
                break
        return {
            "ace": self.ace_index,
            "slot": self.slot_index,
            "display_ace": self.ace_index + 1,
            "display_slot": self.slot_index + 1,
            "state": slot.get("state"),
            "status": slot.get("status"),
            "material": slot.get("material"),
            "brand": slot.get("brand"),
            "sku": slot.get("sku"),
            "color": slot.get("color"),
            "rfid": slot.get("rfid"),
            "loaded_toolhead": loaded_toolhead,
        }


class MultiAceToolheadSensor(MultiAceEntity, SensorEntity):
    """Toolhead loaded-filament sensor."""

    def __init__(self, coordinator: MultiAceCoordinator, toolhead_index: int) -> None:
        super().__init__(coordinator)
        self.toolhead_index = toolhead_index
        self._attr_name = f"Toolhead {toolhead_index + 1}"
        self._attr_unique_id = f"{coordinator.api.base_url}_toolhead_{toolhead_index}"

    @property
    def available(self) -> bool:
        """Return if this toolhead currently exists."""
        return super().available and self.coordinator.toolhead(self.toolhead_index) is not None

    @property
    def native_value(self) -> str | None:
        """Return the loaded filament label."""
        toolhead = self.coordinator.toolhead(self.toolhead_index)
        if not toolhead:
            return None
        if not toolhead.get("filament_detected"):
            return "empty"
        material = toolhead.get("material")
        ace = toolhead.get("ace")
        slot = toolhead.get("slot")
        source = f"ACE {ace + 1} slot {slot + 1}" if ace is not None and slot is not None else "unknown source"
        return f"{material} from {source}" if material else source

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return toolhead metadata."""
        toolhead = self.coordinator.toolhead(self.toolhead_index)
        if not toolhead:
            return {}
        return {
            "ace": toolhead.get("ace"),
            "slot": toolhead.get("slot"),
            "display_ace": toolhead.get("ace") + 1 if toolhead.get("ace") is not None else None,
            "display_slot": toolhead.get("slot") + 1 if toolhead.get("slot") is not None else None,
            "filament_detected": toolhead.get("filament_detected"),
            "filament_in_ace": toolhead.get("filament_in_ace"),
            "filament_in_toolhead": toolhead.get("filament_in_toolhead"),
            "filament_at_extruder": toolhead.get("filament_at_extruder"),
            "channel_state": toolhead.get("channel_state"),
            "channel_error": toolhead.get("channel_error"),
            "color": toolhead.get("color"),
            "material": toolhead.get("material"),
        }
