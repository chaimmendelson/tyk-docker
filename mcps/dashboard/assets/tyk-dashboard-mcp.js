#!/usr/bin/env node
'use strict';

// Local, air-gap-safe launcher for @tyk-technologies/tyk-dashboard-mcp.
//
// Setup (once, while online): `npm install --ignore-scripts` in this
// directory (mcps/dashboard) -- or use build.sh to produce a single
// standalone executable instead (see mcps/README.md). After either, this
// script makes NO network calls of its own -- the OpenAPI spec is a local
// file (dashboard-swagger.yml, bundled alongside this script).
//
// Runs the MCP server IN-PROCESS over stdio (require()'d directly, not
// spawned as a subprocess) so this works unmodified from inside a pkg
// single-file executable, which has no real filesystem paths to exec.
//
// Env vars:
//   TARGET_API_BASE_URL   (required)
//   DASHBOARD_API_KEY | HEADER_Authorization   (one required)
//   OPENAPI_SPEC_PATH      (optional; defaults to the bundled local spec)
//   MCP_WHITELIST_OPERATIONS (default: GET:/**)

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const LOCAL_SPEC_PATH = path.join(ROOT, 'dashboard-swagger.yml');

const HELP_TEXT = `tyk-dashboard-mcp - MCP server exposing a Tyk Dashboard's Admin API as tools

Usage:
  tyk-dashboard-mcp            Run the server (stdio transport, for MCP clients)
  tyk-dashboard-mcp --help     Show this help

Required env vars:
  TARGET_API_BASE_URL          e.g. http://localhost:3000
  DASHBOARD_API_KEY            a Dashboard API access key
    (or HEADER_Authorization instead, to send the raw value unmodified)

Optional env vars:
  OPENAPI_SPEC_PATH            override the bundled Dashboard OpenAPI spec
  MCP_WHITELIST_OPERATIONS     default: GET:/** (read-only). Set to "*" for all operations.
  MCP_BLACKLIST_OPERATIONS     used only when whitelist is unset

Notes:
  - Read-only by default (MCP_WHITELIST_OPERATIONS=GET:/**).
  - stdio only -- there is no HTTP transport.
`;

function fail(msg) {
  console.error(`ERROR: ${msg}`);
  process.exit(1);
}

if (process.argv.slice(2).some((arg) => arg === '--help' || arg === '-h')) {
  process.stdout.write(HELP_TEXT);
  process.exit(0);
}

async function main() {
  const targetUrl = process.env.TARGET_API_BASE_URL;
  const apiKey = process.env.DASHBOARD_API_KEY;
  const headerAuth = process.env.HEADER_Authorization;

  if (!targetUrl) fail('TARGET_API_BASE_URL is required (e.g. http://localhost:3000)');
  if (!apiKey && !headerAuth) fail('either DASHBOARD_API_KEY or HEADER_Authorization must be set');

  const specPath = process.env.OPENAPI_SPEC_PATH || LOCAL_SPEC_PATH;
  if (!fs.existsSync(specPath)) {
    fail(`OpenAPI spec not found at ${specPath}.`);
  }

  // Mutate our own process.env *before* requiring the server module --
  // its config is built from process.env at require time, not read
  // lazily inside startServer().
  process.env.OPENAPI_SPEC_PATH = specPath;
  process.env.MCP_WHITELIST_OPERATIONS = process.env.MCP_WHITELIST_OPERATIONS || 'GET:/**';
  if (apiKey && !headerAuth) {
    process.env.SECURITY_SCHEME_NAME = 'bearerAuth';
    process.env.SECURITY_CREDENTIALS = JSON.stringify({ bearerAuth: apiKey });
  }

  let serverModule;
  try {
    serverModule = require('@tyk-technologies/tyk-dashboard-mcp/dist/src/server.js');
  } catch (err) {
    fail(`could not load @tyk-technologies/tyk-dashboard-mcp: ${err.message}`);
  }
  await serverModule.startServer();
}

main().catch((err) => fail(err.message || String(err)));
