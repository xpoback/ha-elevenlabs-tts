[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# ElevenLabs TTS for Home Assistant

---------

Custom Home Assistant TTS integration for ElevenLabs with a focus on practical day-to-day use:
- one ElevenLabs account entry
- **multiple configurable voice entities**
- **support for `eleven_v3`**
- **support for** both conversion and **streaming**
- a broad set of **per-voice parameters**
- modern Home Assistant UI configuration

## Features

-----

- Config entry setup through the Home Assistant UI
- Reconfigurable ElevenLabs API key
- Multiple voice entities under one ElevenLabs account
- Support for `eleven_multilingual_v2`, `eleven_turbo_v2_5`, and `eleven_v3`
- Support for conversion and streaming TTS
- Per-voice parameters such as model, voice ID, streaming mode, stability, similarity, style, speed, normalization, seed, and speaker boost where supported
- Assist / pipeline friendly TTS entities
- Automation-friendly `tts.*` entities
- Model-specific UI behavior for `eleven_v3`, including hiding unsupported options

## Why This Exists

-----

This integration focuses on a combination that is especially useful in Home Assistant: strong `eleven_v3` support, practical streaming, and flexible per-voice configuration under one ElevenLabs account.

This project aims to provide:
- one integration-level API key
- many per-voice TTS entities in Home Assistant
- support for modern ElevenLabs models, including `eleven_v3`
- practical streaming support for Home Assistant playback
- per-voice settings that work well in automations and Assist pipelines



## Installation

-----

### HACS

1. Open HACS.
2. Add `https://github.com/xpoback/ha-elevenlabs-tts` as a custom repository of type `Integration`.
3. Install `ElevenLabs TTS`.
4. Restart Home Assistant.

### Manual

1. Copy `custom_components/elevenlabs_tts` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

-----

1. In Home Assistant, go to `Settings -> Devices & Services -> Add Integration`.
2. Add `ElevenLabs`.
3. Enter your ElevenLabs API key.
4. Open the integration and add one or more voice entries.
5. For each voice, configure:
   - display name
   - ElevenLabs voice ID
   - model
   - conversion vs streaming
   - model-specific voice options

Each configured voice becomes its own TTS entity.

## Notes

------

- Multiple Home Assistant voice entities can reuse the same ElevenLabs voice ID with different settings.
- `eleven_v3` behaves differently from older models, and the UI adapts to that.
- Streaming uses a startup buffer to reduce clipped audio at playback start.

## Inspiration

----

This integration was built with reference implementations in:

- [loryanstrant/HA-ElevenLabs-Custom-TTS](https://github.com/loryanstrant/HA-ElevenLabs-Custom-TTS), which helped validate ElevenLabs-specific behavior.
- [sfortis/openai_tts](https://github.com/sfortis/openai_tts), which helped shape the streaming and multi-voice Home Assistant patterns.
