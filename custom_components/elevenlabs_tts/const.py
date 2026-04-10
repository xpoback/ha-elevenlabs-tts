"""Constants for the ElevenLabs TTS integration."""

from __future__ import annotations

DOMAIN = "elevenlabs_tts"

CONF_LANGUAGE_CODE = "language_code"
CONF_MODEL = "model"
CONF_PROFILE_NAME = "profile_name"
CONF_SIMILARITY_BOOST = "similarity_boost"
CONF_SPEAKER_BOOST = "speaker_boost"
CONF_STABILITY = "stability"
CONF_STREAMING_MODE = "streaming_mode"
CONF_STYLE = "style"
CONF_VOICE_ID = "voice_id"

SUBENTRY_TYPE_VOICE = "voice"

DEFAULT_MODEL = "eleven_multilingual_v2"
DEFAULT_STABILITY = 0.5
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0
DEFAULT_SPEAKER_BOOST = True
DEFAULT_STREAMING_MODE = "convert"

STREAMING_MODE_CONVERT = "convert"
STREAMING_MODE_STREAM = "stream"

MODEL_OPTIONS: tuple[str, ...] = (
    "eleven_multilingual_v2",
    "eleven_turbo_v2_5",
    "eleven_v3",
)

OUTPUT_FORMAT_MP3 = "mp3_44100_128"

API_BASE_URL = "https://api.elevenlabs.io"
