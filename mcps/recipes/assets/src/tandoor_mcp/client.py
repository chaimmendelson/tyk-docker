"""Async HTTP client for the Tandoor Recipes REST API.

Thin, resource-agnostic wrapper around ``httpx.AsyncClient``. It knows how to
authenticate and how to turn Tandoor's DRF-style list/detail endpoints into
plain dict/list results, and it turns non-2xx responses into
:class:`TandoorAPIError`. It has no opinions about *which* resources exist -
that mapping lives in ``server.py``, which keeps this module reusable and
easy to unit test in isolation.
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, Self

import httpx

from tandoor_mcp.config import Settings
from tandoor_mcp.errors import TandoorAPIError


class TandoorClient:
    """Async client for the Tandoor Recipes API.

    Usage::

        async with TandoorClient(settings) as client:
            recipes = await client.list("recipe", params={"query": "soup"})
    """

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            timeout=settings.timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {settings.api_token}",
                "Accept": "application/json",
            },
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    @staticmethod
    def _resource_path(resource: str, id_: int | str | None = None) -> str:
        path = f"/api/{resource}/"
        if id_ is not None:
            path = f"{path}{id_}/"
        return path

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        """Perform a raw request against ``path`` and return the decoded JSON body.

        Drops ``None``-valued entries from ``params`` so optional filters can be
        passed straight through without building conditionals at call sites.
        Returns ``None`` for responses with no body (e.g. HTTP 204).
        """
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = await self._http.request(
                method,
                path,
                params=clean_params or None,
                json=json_body,
            )
        except httpx.TimeoutException as exc:
            raise TandoorAPIError(f"Request to {path} timed out") from exc
        except httpx.HTTPError as exc:
            raise TandoorAPIError(f"Request to {path} failed: {exc}") from exc

        payload: Any = None
        if response.content:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text

        if not response.is_success:
            message = (
                self._extract_message(payload) or response.reason_phrase or "Tandoor API error"
            )
            raise TandoorAPIError(message, status_code=response.status_code, payload=payload)

        return payload

    @staticmethod
    def _extract_message(payload: Any) -> str | None:
        if isinstance(payload, dict):
            for key in ("detail", "error", "message"):
                if key in payload and isinstance(payload[key], str):
                    return payload[key]
            # DRF validation errors: {"field": ["error", ...]}
            parts: list[str] = []
            for field, errors in payload.items():
                if isinstance(errors, list):
                    parts.append(f"{field}: {'; '.join(str(e) for e in errors)}")
            if parts:
                return "; ".join(parts)
        if isinstance(payload, str) and payload.strip():
            return payload
        return None

    # -- generic resource helpers ------------------------------------------------

    async def list(self, resource: str, *, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", self._resource_path(resource), params=params)

    async def get(self, resource: str, id_: int | str) -> Any:
        return await self.request("GET", self._resource_path(resource, id_))

    async def create(self, resource: str, data: dict[str, Any]) -> Any:
        return await self.request("POST", self._resource_path(resource), json_body=data)

    async def update(
        self,
        resource: str,
        id_: int | str,
        data: dict[str, Any],
        *,
        partial: bool = True,
    ) -> Any:
        method = "PATCH" if partial else "PUT"
        return await self.request(method, self._resource_path(resource, id_), json_body=data)

    async def delete(self, resource: str, id_: int | str) -> None:
        await self.request("DELETE", self._resource_path(resource, id_))
