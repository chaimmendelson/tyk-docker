# Tyk MCP executables

Two single, standalone executables, each wrapping one of Tyk's official [Model Context Protocol](https://modelcontextprotocol.io/) servers for direct use by a local MCP client (OpenCode, Claude Desktop, Cursor, etc.):

| Executable (after build) | Wraps | Purpose |
|---|---|---|
| `docs/dist/tyk-docs-mcp` | [`@tyk-technologies/docs-mcp`](https://github.com/TykTechnologies/docs-mcp) | Search Tyk's documentation (`search_tyk_docs` tool). Fully self-contained, no config, no network needed at all. |
| `dashboard/dist/tyk-dashboard-mcp` | [`@tyk-technologies/tyk-dashboard-mcp`](https://github.com/TykTechnologies/tyk-dashboard-mcp) | Generates MCP tools from a running Tyk Dashboard's Admin API (OpenAPI-driven). Needs a Dashboard URL + API key. |

Each is built (via `build.sh`, on a machine with internet access) into **one self-contained binary** with [`@yao-pkg/pkg`](https://github.com/yao-pkg/pkg) — no Node.js, no npm, no `node_modules` needed on the machine that runs it. This is deliberate: these are meant to run in an **air-gapped network**, where the only thing that can be supplied to the process is its configured key/URL — nothing can be fetched from the internet, and nothing but the one executable file needs to be copied over.

Versions are pinned exactly in each `package.json` (currently `0.1.0-rc7` for both official packages) — bump by editing the version and re-running `build.sh`. stdio only — there is no HTTP transport.

Each project (`docs/`, `dashboard/`) has the same layout:

```
build.sh    builds it (run this)
assets/     source: package.json, the launcher script -- and transient
            build state (node_modules, downloaded/generated files) that
            build.sh cleans up automatically when it's done
dist/       the built executable(s), nothing else
```

## Build (once, while online)

```bash
cd docs && ./build.sh && cd ..
cd dashboard && ./build.sh && cd ..
```

This produces `docs/dist/tyk-docs-mcp` and `dashboard/dist/tyk-dashboard-mcp` — copy just that one file each to wherever the MCP client runs (including an air-gapped machine). By default they're built for `node22-linux-x64`; set `PKG_TARGET` to cross-build for a different platform, e.g.:

```bash
PKG_TARGET=node22-win-x64 ./build.sh      # Windows
PKG_TARGET=node22-macos-x64 ./build.sh    # macOS (Intel)
PKG_TARGET=node22-macos-arm64 ./build.sh  # macOS (Apple Silicon)
```

(see `pkg --help`/[@yao-pkg/pkg's target list](https://github.com/yao-pkg/pkg) for the full set of supported values). Windows/macOS builds produce `dist/tyk-*.exe` alongside the Linux one — run `PKG_TARGET=... ./build.sh` again without deleting `dist/` first if you want both. For `docs`, cross-building for Windows also swaps in the matching Windows release of the bundled search binary (`@buger/probe`) automatically — `npm install` always fetches the binary matching the machine running the build script, not the pkg target, so this step is required for the Windows build to actually work.

**What each build does, and why it's more than a one-liner:**
- `dashboard`: `tyk-dashboard-mcp` is required in-process (not spawned as a subprocess) so it runs cleanly from inside a pkg snapshot — pure CommonJS, no native dependencies, so this "just worked" once wired up. The Dashboard's OpenAPI spec isn't committed to the repo — `build.sh` downloads it fresh (see `SWAGGER_URL` at the top of the script) before packaging, and it's bundled into the executable from there.
- `docs`: `docs-mcp` is native ESM, which pkg can't `import()` from inside a packaged executable, and it shells out to `@buger/probe`, a compiled (Rust) search binary that must exist as a real file (a separate OS process can't read pkg's virtual filesystem) — same for the docs content it searches. `build.sh` first bundles `docs-mcp`'s ESM code into one CommonJS file with `esbuild` (so it can be `require()`'d in-process like dashboard-mcp), then packages that. At first run, the executable extracts the bundled `probe` binary + docs content to a small local cache under the OS temp dir (subsequent runs reuse the cache) — this is the only "setup" that happens, and it's fully offline (copying files already embedded in the executable).

## Run: `tyk-docs-mcp`

No configuration required.

```json
{
  "mcpServers": {
    "tyk-docs": {
      "command": "/absolute/path/to/tyk-docs-mcp"
    }
  }
}
```

Optional passthrough env vars (all optional): `GIT_URL`, `GIT_REF`, `AUTO_UPDATE_INTERVAL`, `INCLUDE_DIR`, `TOOL_NAME`, `TOOL_DESCRIPTION` — see the [upstream README](https://github.com/TykTechnologies/docs-mcp). Leave `GIT_URL` unset to stay fully offline (the default); setting it makes docs-mcp fetch over the network itself, defeating the air-gap setup. `DATA_DIR` is set automatically to the extracted cache; only override it if you know what you're doing.

## Run: `tyk-dashboard-mcp`

Requires a running Tyk Dashboard, reachable from wherever this executable runs. Required env vars:

- `TARGET_API_BASE_URL` — e.g. `http://localhost:3000`
- `DASHBOARD_API_KEY` — a Dashboard API access key (Dashboard UI → your user → API Access Credentials)

```json
{
  "mcpServers": {
    "tyk-dashboard": {
      "command": "/absolute/path/to/tyk-dashboard-mcp",
      "env": {
        "TARGET_API_BASE_URL": "http://localhost:3000",
        "DASHBOARD_API_KEY": "<your-key>"
      }
    }
  }
}
```

### Read-only by default

Defaults to `MCP_WHITELIST_OPERATIONS=GET:/**`, so only read (`GET`) endpoints are exposed as MCP tools — no create/update/delete operations are reachable (verified against a real Dashboard: 69 of 137 spec operations pass the filter, all `GET`; e.g. `getApis` is present, `postApis` and every `delete*` tool are not). To allow write operations too, set `MCP_WHITELIST_OPERATIONS=*` in the client config's `env`. `MCP_BLACKLIST_OPERATIONS` is also available (only used when whitelist is unset) if you'd rather exclude specific operations instead of whitelisting by method.

### Auth header format (verified)

`DASHBOARD_API_KEY` sends `Authorization: Bearer <key>` (the bundled spec declares `bearerAuth` as `type: http, scheme: bearer`). Verified end-to-end against a real running Tyk Dashboard (v5.15.0) — `GET /api/apis` returned `200` with a real API list, no override needed. `HEADER_Authorization` (sends the value through unmodified, no `Bearer ` prefix) remains available as a fallback via the client config's `env` if a particular Dashboard doesn't accept the bearer prefix.
