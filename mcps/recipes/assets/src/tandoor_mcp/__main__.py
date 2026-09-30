"""Entrypoint: run the Tandoor MCP server over stdio."""

from __future__ import annotations

import anyio
from dotenv import load_dotenv

from tandoor_mcp.server import close_client, mcp


async def _run() -> None:
    try:
        await mcp.run_stdio_async()
    finally:
        await close_client()


def main() -> None:
    load_dotenv()
    anyio.run(_run)


if __name__ == "__main__":
    main()
