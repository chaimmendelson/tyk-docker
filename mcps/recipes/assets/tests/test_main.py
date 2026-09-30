from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tandoor_mcp import __main__ as entrypoint


async def test_run_starts_stdio_server_and_always_closes_client():
    with (
        patch.object(entrypoint.mcp, "run_stdio_async", new=AsyncMock()) as run_stdio,
        patch.object(entrypoint, "close_client", new=AsyncMock()) as close_client,
    ):
        await entrypoint._run()

    run_stdio.assert_awaited_once()
    close_client.assert_awaited_once()


async def test_run_closes_client_even_if_stdio_server_raises():
    with (
        patch.object(
            entrypoint.mcp, "run_stdio_async", new=AsyncMock(side_effect=RuntimeError("boom"))
        ),
        patch.object(entrypoint, "close_client", new=AsyncMock()) as close_client,
    ):
        with pytest.raises(RuntimeError, match="boom"):
            await entrypoint._run()

    close_client.assert_awaited_once()


def test_main_loads_dotenv_and_runs_via_anyio():
    with (
        patch.object(entrypoint, "load_dotenv") as load_dotenv,
        patch.object(entrypoint, "anyio") as anyio_mock,
    ):
        entrypoint.main()

    load_dotenv.assert_called_once()
    anyio_mock.run.assert_called_once_with(entrypoint._run)
