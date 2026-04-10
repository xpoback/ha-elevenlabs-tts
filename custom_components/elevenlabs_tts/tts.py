"""TTS entities for ElevenLabs."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import logging
import re
from typing import Any

from homeassistant.components.tts import (
    TTSAudioRequest,
    TTSAudioResponse,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ElevenLabsConfigEntry
from .const import (
    CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
    CONF_APPLY_TEXT_NORMALIZATION,
    CONF_LANGUAGE_CODE,
    CONF_MODEL,
    CONF_PROFILE_NAME,
    CONF_SEED,
    CONF_SEED_ENABLED,
    CONF_SIMILARITY_BOOST,
    CONF_SPEAKER_BOOST,
    CONF_SPEED,
    CONF_STABILITY,
    CONF_STREAMING_MODE,
    CONF_STYLE,
    CONF_VOICE_ID,
    DEFAULT_APPLY_LANGUAGE_TEXT_NORMALIZATION,
    DEFAULT_APPLY_TEXT_NORMALIZATION,
    DEFAULT_MODEL,
    DEFAULT_SEED_ENABLED,
    DEFAULT_SIMILARITY_BOOST,
    DEFAULT_SPEAKER_BOOST,
    DEFAULT_SPEED,
    DEFAULT_STABILITY,
    DEFAULT_STREAMING_MODE,
    DEFAULT_STYLE,
    DOMAIN,
    STREAMING_MODE_STREAM,
    STREAMING_STARTUP_BUFFER_BYTES,
    SUPPORTED_LANGUAGES,
    SUBENTRY_TYPE_VOICE,
)
from .elevenlabs_api import (
    ElevenLabsApiError,
    ElevenLabsAuthError,
    ElevenLabsConnectionError,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ElevenLabsConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TTS entities from ElevenLabs subentries."""
    entities: list[tuple[ElevenLabsVoiceEntity, str]] = []
    for subentry_id, subentry in entry.subentries.items():
        if getattr(subentry, "subentry_type", None) != SUBENTRY_TYPE_VOICE:
            continue
        entities.append(
            (ElevenLabsVoiceEntity(parent_entry=entry, voice_subentry=subentry), subentry_id)
        )

    for entity, subentry_id in entities:
        async_add_entities([entity], config_subentry_id=subentry_id)


class ElevenLabsVoiceEntity(TextToSpeechEntity):
    """A per-voice ElevenLabs TTS entity."""

    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, *, parent_entry: ElevenLabsConfigEntry, voice_subentry: ConfigEntry) -> None:
        """Initialize the entity."""
        self._parent_entry = parent_entry
        self._voice_subentry = voice_subentry

        self._attr_unique_id = voice_subentry.data["unique_id"]
        self._attr_name = f"ElevenLabs TTS {voice_subentry.data[CONF_PROFILE_NAME]}"
        self._attr_config_entry_id = getattr(voice_subentry, "subentry_id", parent_entry.entry_id)
        profile_slug = re.sub(r"[^a-z0-9_]+", "_", voice_subentry.data[CONF_PROFILE_NAME].lower())
        self.entity_id = f"tts.elevenlabs_tts_{profile_slug.strip('_') or 'voice'}"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return a broad language list for Home Assistant validation."""
        return list(SUPPORTED_LANGUAGES)

    @property
    def supported_options(self) -> list[str]:
        """Return supported TTS options."""
        return [
            CONF_MODEL,
            CONF_VOICE_ID,
            CONF_STREAMING_MODE,
            CONF_STABILITY,
            CONF_SIMILARITY_BOOST,
            CONF_STYLE,
            CONF_SPEED,
            CONF_SPEAKER_BOOST,
            CONF_SEED_ENABLED,
            CONF_SEED,
            CONF_APPLY_TEXT_NORMALIZATION,
            CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
            CONF_LANGUAGE_CODE,
        ]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return options used for cache keys and service defaults."""
        return {
            CONF_MODEL: self._voice_subentry.data.get(CONF_MODEL, DEFAULT_MODEL),
            CONF_VOICE_ID: self._voice_subentry.data[CONF_VOICE_ID],
            CONF_STREAMING_MODE: self._voice_subentry.data.get(
                CONF_STREAMING_MODE, DEFAULT_STREAMING_MODE
            ),
            CONF_STABILITY: self._voice_subentry.data.get(CONF_STABILITY, DEFAULT_STABILITY),
            CONF_SIMILARITY_BOOST: self._voice_subentry.data.get(
                CONF_SIMILARITY_BOOST, DEFAULT_SIMILARITY_BOOST
            ),
            CONF_STYLE: self._voice_subentry.data.get(CONF_STYLE, DEFAULT_STYLE),
            CONF_SPEED: self._voice_subentry.data.get(CONF_SPEED, DEFAULT_SPEED),
            CONF_SPEAKER_BOOST: self._voice_subentry.data.get(
                CONF_SPEAKER_BOOST, DEFAULT_SPEAKER_BOOST
            ),
            CONF_SEED_ENABLED: self._voice_subentry.data.get(
                CONF_SEED_ENABLED, DEFAULT_SEED_ENABLED
            ),
            CONF_SEED: self._voice_subentry.data.get(CONF_SEED),
            CONF_APPLY_TEXT_NORMALIZATION: self._voice_subentry.data.get(
                CONF_APPLY_TEXT_NORMALIZATION, DEFAULT_APPLY_TEXT_NORMALIZATION
            ),
            CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION: self._voice_subentry.data.get(
                CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
                DEFAULT_APPLY_LANGUAGE_TEXT_NORMALIZATION,
            ),
        }

    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict[str, Any] | None = None,
    ) -> TtsAudioType:
        """Generate audio for a full TTS request."""
        merged_options = self._merged_options(language, options)
        client = self._parent_entry.runtime_data.client

        try:
            if merged_options[CONF_STREAMING_MODE] == STREAMING_MODE_STREAM:
                audio = bytearray()
                async for chunk in client.stream_text(
                    voice_id=merged_options[CONF_VOICE_ID],
                    text=message,
                    model=merged_options[CONF_MODEL],
                    voice_settings=self._voice_settings(merged_options),
                    language_code=merged_options.get(CONF_LANGUAGE_CODE),
                    seed=self._seed_value(merged_options),
                    apply_text_normalization=merged_options.get(
                        CONF_APPLY_TEXT_NORMALIZATION
                    ),
                    apply_language_text_normalization=merged_options.get(
                        CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION
                    ),
                ):
                    audio.extend(chunk)
                return ("mp3", bytes(audio))

            audio = await client.convert_text(
                voice_id=merged_options[CONF_VOICE_ID],
                text=message,
                model=merged_options[CONF_MODEL],
                voice_settings=self._voice_settings(merged_options),
                language_code=merged_options.get(CONF_LANGUAGE_CODE),
                seed=self._seed_value(merged_options),
                apply_text_normalization=merged_options.get(
                    CONF_APPLY_TEXT_NORMALIZATION
                ),
                apply_language_text_normalization=merged_options.get(
                    CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION
                ),
            )
            return ("mp3", audio)
        except ElevenLabsAuthError as err:
            _LOGGER.error("Authentication failed for %s: %s", self.entity_id, err)
        except ElevenLabsConnectionError as err:
            _LOGGER.error("Connection failed for %s: %s", self.entity_id, err)
        except ElevenLabsApiError as err:
            _LOGGER.error("ElevenLabs request failed for %s: %s", self.entity_id, err)

        return None

    async def async_stream_tts_audio(
        self, request: TTSAudioRequest
    ) -> TTSAudioResponse:
        """Generate streaming audio for Assist pipelines."""
        merged_options = self._merged_options(request.language, request.options)
        client = self._parent_entry.runtime_data.client

        async def message_to_audio() -> AsyncGenerator[bytes, None]:
            """Collect the incoming text stream and emit audio chunks."""
            text = ""
            async for chunk in request.message_gen:
                text += chunk

            if merged_options[CONF_STREAMING_MODE] != STREAMING_MODE_STREAM:
                audio = await client.convert_text(
                    voice_id=merged_options[CONF_VOICE_ID],
                    text=text,
                    model=merged_options[CONF_MODEL],
                    voice_settings=self._voice_settings(merged_options),
                    language_code=merged_options.get(CONF_LANGUAGE_CODE),
                    seed=self._seed_value(merged_options),
                    apply_text_normalization=merged_options.get(
                        CONF_APPLY_TEXT_NORMALIZATION
                    ),
                    apply_language_text_normalization=merged_options.get(
                        CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION
                    ),
                )
                yield audio
                return

            buffered_chunks: list[bytes] = []
            buffered_bytes = 0
            stream_started = False

            async for audio_chunk in client.stream_text(
                voice_id=merged_options[CONF_VOICE_ID],
                text=text,
                model=merged_options[CONF_MODEL],
                voice_settings=self._voice_settings(merged_options),
                language_code=merged_options.get(CONF_LANGUAGE_CODE),
                seed=self._seed_value(merged_options),
                apply_text_normalization=merged_options.get(
                    CONF_APPLY_TEXT_NORMALIZATION
                ),
                apply_language_text_normalization=merged_options.get(
                    CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION
                ),
            ):
                buffered_chunks.append(audio_chunk)
                buffered_bytes += len(audio_chunk)

                if not stream_started and buffered_bytes < STREAMING_STARTUP_BUFFER_BYTES:
                    continue

                if not stream_started:
                    stream_started = True
                    _LOGGER.debug(
                        "Starting ElevenLabs stream for %s after buffering %d bytes",
                        self.entity_id,
                        buffered_bytes,
                    )
                    for buffered_chunk in buffered_chunks:
                        yield buffered_chunk
                    buffered_chunks.clear()
                    continue

                yield audio_chunk

            if buffered_chunks:
                _LOGGER.debug(
                    "ElevenLabs stream for %s completed before buffer threshold; yielding %d buffered chunks",
                    self.entity_id,
                    len(buffered_chunks),
                )
                for buffered_chunk in buffered_chunks:
                    yield buffered_chunk

        return TTSAudioResponse(extension="mp3", data_gen=message_to_audio())

    def _merged_options(
        self, language: str | None, options: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Merge entity defaults with request overrides."""
        merged = {**self.default_options, **(options or {})}
        if CONF_LANGUAGE_CODE not in merged and language and language != "*":
            merged[CONF_LANGUAGE_CODE] = language
        return merged

    def _voice_settings(self, options: dict[str, Any]) -> dict[str, Any]:
        """Extract ElevenLabs voice settings from merged options."""
        return {
            "stability": float(options[CONF_STABILITY]),
            "similarity_boost": float(options[CONF_SIMILARITY_BOOST]),
            "style": float(options[CONF_STYLE]),
            "speed": float(options[CONF_SPEED]),
            "use_speaker_boost": bool(options[CONF_SPEAKER_BOOST]),
        }

    def _seed_value(self, options: dict[str, Any]) -> int | None:
        """Return the configured seed when enabled."""
        if not options.get(CONF_SEED_ENABLED):
            return None
        seed = options.get(CONF_SEED)
        return int(seed) if seed is not None else None
