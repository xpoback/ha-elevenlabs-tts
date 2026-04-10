"""Async ElevenLabs API client."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import aiohttp

from .const import API_BASE_URL, CONF_LANGUAGE_CODE, OUTPUT_FORMAT_MP3


class ElevenLabsApiError(Exception):
    """Base ElevenLabs API error."""


class ElevenLabsAuthError(ElevenLabsApiError):
    """Raised when authentication fails."""


class ElevenLabsConnectionError(ElevenLabsApiError):
    """Raised when the API cannot be reached."""


class ElevenLabsApiClient:
    """Minimal async client for the ElevenLabs TTS API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._api_key = api_key
        self._session = session

    @property
    def _headers(self) -> dict[str, str]:
        """Return request headers."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "xi-api-key": self._api_key,
        }

    async def validate_api_key(self) -> None:
        """Validate the configured API key."""
        await self._request_json("GET", "/v1/user/subscription")

    async def convert_text(
        self,
        *,
        voice_id: str,
        text: str,
        model: str,
        voice_settings: dict[str, Any],
        language_code: str | None = None,
    ) -> bytes:
        """Generate TTS audio and return the full payload."""
        payload = self._build_tts_payload(
            text=text,
            model=model,
            voice_settings=voice_settings,
            language_code=language_code,
        )
        return await self._request_bytes(
            "POST",
            f"/v1/text-to-speech/{voice_id}",
            payload,
            params={"output_format": OUTPUT_FORMAT_MP3},
        )

    async def stream_text(
        self,
        *,
        voice_id: str,
        text: str,
        model: str,
        voice_settings: dict[str, Any],
        language_code: str | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Generate streaming TTS audio."""
        payload = self._build_tts_payload(
            text=text,
            model=model,
            voice_settings=voice_settings,
            language_code=language_code,
        )
        async for chunk in self._stream_bytes(
            "POST",
            f"/v1/text-to-speech/{voice_id}/stream",
            payload,
            params={"output_format": OUTPUT_FORMAT_MP3},
        ):
            yield chunk

    def _build_tts_payload(
        self,
        *,
        text: str,
        model: str,
        voice_settings: dict[str, Any],
        language_code: str | None,
    ) -> dict[str, Any]:
        """Build the ElevenLabs request payload."""
        payload: dict[str, Any] = {
            "text": text,
            "model_id": model,
            "voice_settings": voice_settings,
        }
        if language_code:
            payload[CONF_LANGUAGE_CODE] = language_code
        return payload

    async def _request_json(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a JSON request and parse the response."""
        try:
            async with self._session.request(
                method,
                f"{API_BASE_URL}{path}",
                headers=self._headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                await self._raise_for_status(response)
                return await response.json()
        except aiohttp.ClientError as err:
            raise ElevenLabsConnectionError(str(err)) from err

    async def _request_bytes(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        *,
        params: dict[str, str] | None = None,
    ) -> bytes:
        """Send a request and return the binary response body."""
        try:
            async with self._session.request(
                method,
                f"{API_BASE_URL}{path}",
                headers=self._headers,
                json=payload,
                params=params,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                await self._raise_for_status(response)
                return await response.read()
        except aiohttp.ClientError as err:
            raise ElevenLabsConnectionError(str(err)) from err

    async def _stream_bytes(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        *,
        params: dict[str, str] | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Send a request and yield the response body in chunks."""
        try:
            async with self._session.request(
                method,
                f"{API_BASE_URL}{path}",
                headers=self._headers,
                json=payload,
                params=params,
                timeout=aiohttp.ClientTimeout(total=120),
            ) as response:
                await self._raise_for_status(response)
                async for chunk in response.content.iter_chunked(8192):
                    if chunk:
                        yield chunk
        except aiohttp.ClientError as err:
            raise ElevenLabsConnectionError(str(err)) from err

    async def _raise_for_status(self, response: aiohttp.ClientResponse) -> None:
        """Raise a typed exception on an unsuccessful response."""
        if response.status in (401, 403):
            raise ElevenLabsAuthError(await response.text())
        if response.status >= 400:
            raise ElevenLabsApiError(
                f"ElevenLabs API returned status {response.status}: {await response.text()}"
            )
