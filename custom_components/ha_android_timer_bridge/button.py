"""A button that silences a timer ringing on the tablet."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import api
from .const import CONF_DEVICE_ID, CONF_PAIRING_CODE
from .entity import tablet_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Stop timer button."""
    async_add_entities([StopTimerButton(entry)])


class StopTimerButton(ButtonEntity):
    """Presses Stop on the tablet, the same as tapping it in the Clock notification.

    Pressing it when nothing is ringing does nothing, quietly: a notification button tapped
    after someone already stopped the timer in the kitchen is not an error.
    """

    _attr_has_entity_name = True
    _attr_name = "Stop timer"
    _attr_icon = "mdi:timer-off-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_stop_timer"
        self._attr_device_info = tablet_device_info(entry)

    async def async_press(self) -> None:
        """Ask the tablet to stop whatever timer is ringing."""
        try:
            stopped = await api.async_stop(
                async_get_clientsession(self.hass),
                self._entry.data[CONF_HOST],
                self._entry.data[CONF_PORT],
                self._entry.data[CONF_PAIRING_CODE],
            )
        except api.BridgeError as err:
            raise HomeAssistantError(f"Could not stop the timer: {err}") from err
        _LOGGER.debug("%s stopped %s timer(s)", self._entry.title, stopped)
