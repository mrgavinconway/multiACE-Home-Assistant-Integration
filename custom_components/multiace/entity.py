"""Entity helpers for multiACE."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MultiAceCoordinator


class MultiAceEntity(CoordinatorEntity[MultiAceCoordinator]):
    """Base class for multiACE entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MultiAceCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the printer device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.api.base_url)},
            manufacturer="multiACE",
            name="multiACE",
            configuration_url=self.coordinator.api.base_url,
        )


class MultiAceAceEntity(MultiAceEntity):
    """Base class for one ACE unit."""

    def __init__(self, coordinator: MultiAceCoordinator, ace_index: int) -> None:
        super().__init__(coordinator)
        self.ace_index = ace_index

    @property
    def ace(self) -> dict[str, Any] | None:
        """Return this ACE data."""
        return self.coordinator.ace(self.ace_index)

    @property
    def available(self) -> bool:
        """Return if this ACE currently exists."""
        return super().available and self.ace is not None
