"""Config flow for ElevenLabs TTS."""

from __future__ import annotations

import hashlib
import random
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

from .const import (
    CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
    CONF_APPLY_TEXT_NORMALIZATION,
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
    MODEL_OPTIONS,
    STREAMING_MODE_CONVERT,
    STREAMING_MODE_STREAM,
    SUBENTRY_TYPE_VOICE,
)
from .elevenlabs_api import (
    ElevenLabsApiClient,
    ElevenLabsApiError,
    ElevenLabsAuthError,
    ElevenLabsConnectionError,
)


def _profile_unique_id(voice_id: str) -> str:
    """Create a stable unique ID for a voice profile."""
    digest = hashlib.sha256(voice_id.encode()).hexdigest()[:16]
    return f"{DOMAIN}_{digest}"


def _voice_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Return the schema for a voice subentry."""
    defaults = defaults or {}
    seed_default = defaults.get(CONF_SEED)
    if seed_default is None:
        seed_default = random.randint(0, 4_294_967_295)
    return vol.Schema(
        {
            vol.Required(
                CONF_PROFILE_NAME,
                default=defaults.get(CONF_PROFILE_NAME, ""),
            ): str,
            vol.Required(
                CONF_VOICE_ID,
                default=defaults.get(CONF_VOICE_ID, ""),
            ): str,
            vol.Required(
                CONF_MODEL,
                default=defaults.get(CONF_MODEL, DEFAULT_MODEL),
            ): selector(
                {
                    "select": {
                        "options": list(MODEL_OPTIONS),
                        "mode": "dropdown",
                    }
                }
            ),
            vol.Required(
                CONF_STREAMING_MODE,
                default=defaults.get(CONF_STREAMING_MODE, DEFAULT_STREAMING_MODE),
            ): selector(
                {
                    "select": {
                        "options": [
                            {"value": STREAMING_MODE_CONVERT, "label": "Convert"},
                            {"value": STREAMING_MODE_STREAM, "label": "Stream"},
                        ],
                        "mode": "list",
                    }
                }
            ),
            vol.Optional(
                CONF_STABILITY,
                default=defaults.get(CONF_STABILITY, DEFAULT_STABILITY),
            ): selector(
                {"number": {"min": 0, "max": 1, "step": 0.01, "mode": "box"}}
            ),
            vol.Optional(
                CONF_SIMILARITY_BOOST,
                default=defaults.get(CONF_SIMILARITY_BOOST, DEFAULT_SIMILARITY_BOOST),
            ): selector(
                {"number": {"min": 0, "max": 1, "step": 0.01, "mode": "box"}}
            ),
            vol.Optional(
                CONF_STYLE,
                default=defaults.get(CONF_STYLE, DEFAULT_STYLE),
            ): selector(
                {"number": {"min": 0, "max": 1, "step": 0.01, "mode": "box"}}
            ),
            vol.Optional(
                CONF_SPEED,
                default=defaults.get(CONF_SPEED, DEFAULT_SPEED),
            ): selector(
                {"number": {"min": 0.7, "max": 1.2, "step": 0.01, "mode": "box"}}
            ),
            vol.Optional(
                CONF_SPEAKER_BOOST,
                default=defaults.get(CONF_SPEAKER_BOOST, DEFAULT_SPEAKER_BOOST),
            ): selector({"boolean": {}}),
            vol.Optional(
                CONF_SEED_ENABLED,
                default=defaults.get(CONF_SEED_ENABLED, DEFAULT_SEED_ENABLED),
            ): selector({"boolean": {}}),
            vol.Optional(
                CONF_SEED,
                default=seed_default,
            ): selector(
                {
                    "number": {
                        "min": 0,
                        "max": 4294967295,
                        "step": 1,
                        "mode": "box",
                    }
                }
            ),
            vol.Optional(
                CONF_APPLY_TEXT_NORMALIZATION,
                default=defaults.get(
                    CONF_APPLY_TEXT_NORMALIZATION, DEFAULT_APPLY_TEXT_NORMALIZATION
                ),
            ): selector(
                {
                    "select": {
                        "options": [
                            {"value": "auto", "label": "Auto"},
                            {"value": "on", "label": "On"},
                            {"value": "off", "label": "Off"},
                        ],
                        "mode": "list",
                    }
                }
            ),
            vol.Optional(
                CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
                default=defaults.get(
                    CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION,
                    DEFAULT_APPLY_LANGUAGE_TEXT_NORMALIZATION,
                ),
            ): selector({"boolean": {}}),
        }
    )


async def _validate_api_key(hass, api_key: str) -> None:
    """Validate an API key."""
    client = ElevenLabsApiClient(
        api_key=api_key,
        session=async_get_clientsession(hass),
    )
    await client.validate_api_key()


class ElevenLabsTtsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle an ElevenLabs TTS config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                if self._async_current_entries():
                    return self.async_abort(reason="single_instance_allowed")

                await _validate_api_key(self.hass, user_input[CONF_API_KEY])

                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="ElevenLabs",
                    data={CONF_API_KEY: user_input[CONF_API_KEY]},
                )
            except ElevenLabsAuthError:
                errors["base"] = "invalid_api_key"
            except ElevenLabsConnectionError:
                errors["base"] = "cannot_connect"
            except ElevenLabsApiError:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return supported subentry types."""
        return {SUBENTRY_TYPE_VOICE: ElevenLabsVoiceSubentryFlow}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return a no-op options flow."""
        return ElevenLabsNoOptionsFlow(config_entry)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Reconfigure the parent entry."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            try:
                await _validate_api_key(self.hass, user_input[CONF_API_KEY])
                await self.async_set_unique_id(entry.unique_id)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_API_KEY: user_input[CONF_API_KEY]},
                    reason="reconfigure_successful",
                )
            except ElevenLabsAuthError:
                errors["base"] = "invalid_api_key"
            except ElevenLabsConnectionError:
                errors["base"] = "cannot_connect"
            except ElevenLabsApiError:
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_KEY,
                    description={"suggested_value": entry.data.get(CONF_API_KEY, "")},
                ): str
            }
        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Start a reauth flow."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            try:
                await _validate_api_key(self.hass, user_input[CONF_API_KEY])
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={**entry.data, CONF_API_KEY: user_input[CONF_API_KEY]},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            except ElevenLabsAuthError:
                errors["base"] = "invalid_api_key"
            except ElevenLabsConnectionError:
                errors["base"] = "cannot_connect"
            except ElevenLabsApiError:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )


class ElevenLabsVoiceSubentryFlow(ConfigSubentryFlow):
    """Manage ElevenLabs voice subentries."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Create a voice profile."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if await self._profile_exists(user_input[CONF_PROFILE_NAME]):
                errors["base"] = "already_exists"
            else:
                data = {
                    **user_input,
                    "unique_id": _profile_unique_id(user_input[CONF_VOICE_ID]),
                }
                return self.async_create_entry(
                    title=user_input[CONF_PROFILE_NAME],
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_voice_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Reconfigure a voice profile."""
        errors: dict[str, str] = {}
        subentry = self._get_reconfigure_subentry()
        if subentry is None:
            return self.async_abort(reason="subentry_not_found")

        if user_input is not None:
            if user_input[CONF_PROFILE_NAME] != subentry.title and await self._profile_exists(
                user_input[CONF_PROFILE_NAME]
            ):
                errors["base"] = "already_exists"
            else:
                return self.async_update_and_abort(
                    self._get_entry(),
                    subentry,
                    data={
                        **subentry.data,
                        **user_input,
                        "unique_id": subentry.data.get(
                            "unique_id", _profile_unique_id(user_input[CONF_VOICE_ID])
                        ),
                    },
                    title=user_input[CONF_PROFILE_NAME],
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_voice_schema(subentry.data),
            errors=errors,
        )

    async def _profile_exists(self, profile_name: str) -> bool:
        """Check whether another voice subentry already uses this profile name."""
        parent = self._get_entry()
        for subentry in parent.subentries.values():
            if subentry.title == profile_name:
                return True
        return False


class ElevenLabsNoOptionsFlow(OptionsFlow):
    """Expose that configuration happens via subentries and reconfigure."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Abort because no parent options are supported."""
        return self.async_abort(reason="no_options_available")
