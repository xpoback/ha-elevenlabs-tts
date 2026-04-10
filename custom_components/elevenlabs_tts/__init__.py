"""The ElevenLabs TTS integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .elevenlabs_api import ElevenLabsApiClient

PLATFORMS: list[Platform] = [Platform.TTS]


@dataclass(slots=True)
class ElevenLabsRuntimeData:
    """Runtime data for a config entry."""

    client: ElevenLabsApiClient


type ElevenLabsConfigEntry = ConfigEntry[ElevenLabsRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: ElevenLabsConfigEntry) -> bool:
    """Set up ElevenLabs TTS from a config entry."""
    session = async_get_clientsession(hass)
    client = ElevenLabsApiClient(api_key=entry.data["api_key"], session=session)

    entry.runtime_data = ElevenLabsRuntimeData(client=client)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ElevenLabsConfigEntry) -> bool:
    """Unload an ElevenLabs TTS config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
