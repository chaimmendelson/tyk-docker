from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import respx

from tandoor_mcp import server as server_module
from tandoor_mcp.client import TandoorClient
from tandoor_mcp.config import Settings

BASE_URL = "http://tandoor.test"
TOKEN = "tda_test_token"


@pytest.fixture
def settings() -> Settings:
    return Settings(base_url=BASE_URL, api_token=TOKEN, timeout=5.0)


@pytest.fixture
def mock_api() -> AsyncIterator[respx.MockRouter]:
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router


@pytest_asyncio.fixture
async def client(settings: Settings, mock_api: respx.MockRouter) -> AsyncIterator[TandoorClient]:
    c = TandoorClient(settings)
    try:
        yield c
    finally:
        await c.aclose()


@pytest_asyncio.fixture
async def mcp_client(client: TandoorClient) -> AsyncIterator[TandoorClient]:
    """Wire the module-level singleton used by server.py tools to a mocked client."""
    server_module.set_client(client)
    try:
        yield client
    finally:
        server_module.set_client(None)
