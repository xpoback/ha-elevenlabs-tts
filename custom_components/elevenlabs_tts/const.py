"""Constants for the ElevenLabs TTS integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "elevenlabs_tts"

CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION: Final = "apply_language_text_normalization"
CONF_APPLY_TEXT_NORMALIZATION: Final = "apply_text_normalization"
CONF_LANGUAGE_CODE: Final = "language_code"
CONF_MODEL: Final = "model"
CONF_PROFILE_NAME: Final = "profile_name"
CONF_SEED: Final = "seed"
CONF_SEED_ENABLED: Final = "seed_enabled"
CONF_SIMILARITY_BOOST: Final = "similarity_boost"
CONF_SPEAKER_BOOST: Final = "speaker_boost"
CONF_SPEED: Final = "speed"
CONF_STABILITY: Final = "stability"
CONF_STREAMING_MODE: Final = "streaming_mode"
CONF_STYLE: Final = "style"
CONF_VOICE_ID: Final = "voice_id"

SUBENTRY_TYPE_VOICE: Final = "voice"
MODEL_ELEVEN_V3: Final = "eleven_v3"

DEFAULT_MODEL: Final = "eleven_multilingual_v2"
DEFAULT_APPLY_LANGUAGE_TEXT_NORMALIZATION: Final = False
DEFAULT_APPLY_TEXT_NORMALIZATION: Final = "auto"
DEFAULT_SEED_ENABLED: Final = False
DEFAULT_STABILITY: Final = 0.5
DEFAULT_SIMILARITY_BOOST: Final = 0.75
DEFAULT_STYLE: Final = 0.0
DEFAULT_SPEAKER_BOOST: Final = True
DEFAULT_SPEED: Final = 1.0
DEFAULT_STREAMING_MODE: Final = "convert"

STREAMING_MODE_CONVERT: Final = "convert"
STREAMING_MODE_STREAM: Final = "stream"

MODEL_OPTIONS: tuple[str, ...] = (
    "eleven_multilingual_v2",
    "eleven_turbo_v2_5",
    MODEL_ELEVEN_V3,
)

OUTPUT_FORMAT_MP3: Final = "mp3_44100_128"
STREAMING_STARTUP_BUFFER_BYTES: Final = 32 * 1024

API_BASE_URL: Final = "https://api.elevenlabs.io"

# Broad ISO 639-1 coverage for Home Assistant language validation.
# The integration does not try to enforce model-specific language support and
# simply forwards the requested language_code to ElevenLabs.
SUPPORTED_LANGUAGES: tuple[str, ...] = (
    "af", "am", "ar", "az", "be", "bg", "bn", "bs", "ca", "cs", "cy", "da",
    "de", "el", "en", "es", "et", "eu", "fa", "fi", "fr", "ga", "gl", "gu",
    "he", "hi", "hr", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "km",
    "kn", "ko", "lo", "lt", "lv", "mk", "ml", "mn", "mr", "ms", "mt", "my",
    "ne", "nl", "no", "pa", "pl", "ps", "pt", "ro", "si", "sk", "sl",
    "sq", "sr", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "uz",
    "vi", "zh",
)
