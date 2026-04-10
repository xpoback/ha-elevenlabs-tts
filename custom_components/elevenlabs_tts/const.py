"""Constants for the ElevenLabs TTS integration."""

from __future__ import annotations

DOMAIN = "elevenlabs_tts"

CONF_APPLY_LANGUAGE_TEXT_NORMALIZATION = "apply_language_text_normalization"
CONF_APPLY_TEXT_NORMALIZATION = "apply_text_normalization"
CONF_LANGUAGE_CODE = "language_code"
CONF_MODEL = "model"
CONF_PROFILE_NAME = "profile_name"
CONF_SEED = "seed"
CONF_SEED_ENABLED = "seed_enabled"
CONF_SIMILARITY_BOOST = "similarity_boost"
CONF_SPEAKER_BOOST = "speaker_boost"
CONF_SPEED = "speed"
CONF_STABILITY = "stability"
CONF_STREAMING_MODE = "streaming_mode"
CONF_STYLE = "style"
CONF_VOICE_ID = "voice_id"

SUBENTRY_TYPE_VOICE = "voice"
MODEL_ELEVEN_V3 = "eleven_v3"

DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_APPLY_LANGUAGE_TEXT_NORMALIZATION = False
DEFAULT_APPLY_TEXT_NORMALIZATION = "auto"
DEFAULT_SEED_ENABLED = False
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0
DEFAULT_SPEAKER_BOOST = True
DEFAULT_SPEED = 1.0
DEFAULT_STREAMING_MODE = "convert"

STREAMING_MODE_CONVERT = "convert"
STREAMING_MODE_STREAM = "stream"

MODEL_OPTIONS: tuple[str, ...] = (
    "eleven_multilingual_v2",
    "eleven_turbo_v2_5",
    MODEL_ELEVEN_V3,
)

OUTPUT_FORMAT_MP3 = "mp3_44100_128"
STREAMING_STARTUP_BUFFER_BYTES = 32 * 1024

API_BASE_URL = "https://api.elevenlabs.io"

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
