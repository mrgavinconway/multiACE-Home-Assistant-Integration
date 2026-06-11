"""HTTP client for multiACE Web."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientError, ClientResponseError, ClientSession
from yarl import URL


class MultiAceApiError(Exception):
    """Base multiACE API error."""


class MultiAceApiConnectionError(MultiAceApiError):
    """Raised when the multiACE endpoint cannot be reached."""


class MultiAceApiAuthError(MultiAceApiError):
    """Raised when the multiACE endpoint rejects the request."""


class MultiAceApi:
    """Small async client for the multiACE REST API."""

    def __init__(self, session: ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = self.normalize_base_url(base_url)

    @property
    def base_url(self) -> str:
        """Return the normalized base URL."""
        return self._base_url

    @staticmethod
    def normalize_base_url(base_url: str) -> str:
        """Normalize printer or multiACE URL to the mounted multiACE root."""
        raw = (base_url or "").strip()
        if not raw:
            raise MultiAceApiError("Base URL is required")
        if "://" not in raw:
            raw = f"http://{raw}"

        url = URL(raw)
        path = url.path.rstrip("/")
        if path.endswith("/api"):
            path = path[:-4]
        if not path.endswith("/multiace"):
            path = f"{path}/multiace" if path else "/multiace"
        return str(url.with_path(path + "/").with_query(None).with_fragment(None))

    def _url(self, path: str) -> str:
        return urljoin(self._base_url, path.lstrip("/"))

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        timeout: int = 20,
    ) -> Any:
        """Send a request and return JSON."""
        try:
            async with self._session.request(
                method,
                self._url(path),
                json=json,
                timeout=timeout,
            ) as response:
                if response.status in (401, 403):
                    raise MultiAceApiAuthError(f"HTTP {response.status}")
                response.raise_for_status()
                return await response.json()
        except MultiAceApiAuthError:
            raise
        except ClientResponseError as err:
            raise MultiAceApiError(f"HTTP {err.status}: {err.message}") from err
        except (ClientError, TimeoutError) as err:
            raise MultiAceApiConnectionError(str(err)) from err

    async def async_get_state(self) -> dict[str, Any]:
        """Fetch the aggregated multiACE state."""
        data = await self.request("GET", "api/state")
        if not isinstance(data, dict):
            raise MultiAceApiError("Unexpected state payload")
        if data.get("error"):
            raise MultiAceApiError(str(data["error"]))
        return data

    async def async_get_version(self) -> dict[str, Any]:
        """Fetch version metadata."""
        data = await self.request("GET", "api/version")
        return data if isinstance(data, dict) else {}

    async def async_start_dryer(
        self,
        ace: int,
        temperature: int,
        duration: int,
    ) -> None:
        """Start drying on one ACE."""
        await self.request(
            "POST",
            "api/macro",
            json={
                "name": "ACE_DRY",
                "args": {"ACE": ace, "TEMP": temperature, "DURATION": duration},
            },
            timeout=1800,
        )

    async def async_stop_dryer(self, ace: int) -> None:
        """Stop drying on one ACE."""
        await self.request(
            "POST",
            "api/macro",
            json={"name": "ACE_STOP_DRYING", "args": {"ACE": ace}},
            timeout=120,
        )
