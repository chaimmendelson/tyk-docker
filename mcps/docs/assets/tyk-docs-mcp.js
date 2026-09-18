#!/usr/bin/env node
'use strict';

// Local, air-gap-safe launcher for @tyk-technologies/docs-mcp.
//
// Setup (once, while online): run build.sh in this directory (mcps/docs).
// It bundles docs-mcp's native-ESM code into a single CJS file (so it can
// be `require()`'d in-process -- pkg has no working `import()` support for
// packaged executables), then packages this whole launcher into a single
// standalone binary with @yao-pkg/pkg.
//
// docs-mcp shells out to @buger/probe, a compiled (Rust) search binary,
// and reads its bundled docs content from real files on disk -- neither
// can live only inside a pkg snapshot (a separate OS process can't read
// pkg's virtual filesystem). So on first run from the packaged executable,
// this script extracts both (once, cached under the OS temp dir) to real
// files and points PROBE_PATH / DATA_DIR at them. When running via plain
// node (dist/docs-mcp-bundle.cjs + node_modules present normally), it
// points straight at the real node_modules paths instead -- no extraction.
//
// Env vars: see --help.

const fs = require('fs');
const path = require('path');
const os = require('os');

const PKG_ROOT = __dirname;
const IS_PACKAGED = typeof process.pkg !== 'undefined';
const BUNDLE_PATH = path.join(PKG_ROOT, 'docs-mcp-bundle.cjs');

const HELP_TEXT = `tyk-docs-mcp - MCP server exposing Tyk documentation search (search_tyk_docs)

Usage:
  tyk-docs-mcp            Run the server (stdio transport, for MCP clients)
  tyk-docs-mcp --help     Show this help

No configuration required. Optional env vars (all passthrough to docs-mcp,
see https://github.com/TykTechnologies/docs-mcp):
  GIT_URL, GIT_REF, AUTO_UPDATE_INTERVAL, INCLUDE_DIR, TOOL_NAME, TOOL_DESCRIPTION

Notes:
  - Leave GIT_URL unset to stay fully offline (the default); setting it
    makes docs-mcp fetch over the network itself.
  - stdio only -- there is no HTTP transport.
  - On first run, the bundled search binary + docs content are extracted
    to a small local cache under the OS temp dir (offline, one-time).
`;

function fail(msg) {
  console.error(`ERROR: ${msg}`);
  process.exit(1);
}

if (process.argv.slice(2).some((arg) => arg === '--help' || arg === '-h')) {
  process.stdout.write(HELP_TEXT);
  process.exit(0);
}

function copyFileSyncAcrossFs(src, dest, mode) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, fs.readFileSync(src), mode ? { mode } : undefined);
}

function copyDirSyncAcrossFs(srcDir, destDir) {
  fs.mkdirSync(destDir, { recursive: true });
  for (const name of fs.readdirSync(srcDir)) {
    const srcPath = path.join(srcDir, name);
    const destPath = path.join(destDir, name);
    let stat;
    try {
      stat = fs.statSync(srcPath); // follows symlinks
    } catch (err) {
      continue; // skip broken symlinks etc.
    }
    if (stat.isDirectory()) {
      copyDirSyncAcrossFs(srcPath, destPath);
    } else if (stat.isFile()) {
      copyFileSyncAcrossFs(srcPath, destPath);
    }
  }
}

// Extracts the probe binary + bundled docs data out of the pkg snapshot
// into real files under the OS temp dir (cached across runs via a marker
// file), and returns { probePath, dataDir }.
function extractPackagedAssets() {
  const probeVersion = require('@buger/probe/package.json').version;
  const cacheDir = path.join(os.tmpdir(), `tyk-docs-mcp-${probeVersion}`);
  const marker = path.join(cacheDir, '.extracted');
  const probeSrc = path.join(PKG_ROOT, 'node_modules', '@buger', 'probe', 'bin', 'probe');
  const dataSrc = path.join(PKG_ROOT, 'node_modules', '@tyk-technologies', 'docs-mcp', 'data');
  // The embedded binary's content matches this executable's own target
  // platform (build.sh swaps it in for cross-builds); name the extracted
  // copy accordingly so Windows can actually run it.
  const probeDest = path.join(cacheDir, process.platform === 'win32' ? 'probe.exe' : 'probe');
  const dataDest = path.join(cacheDir, 'data');

  if (!fs.existsSync(marker)) {
    console.error('[tyk-docs-mcp] first run: extracting bundled search binary + docs data to a local cache...');
    copyFileSyncAcrossFs(probeSrc, probeDest);
    fs.chmodSync(probeDest, 0o755);
    copyDirSyncAcrossFs(dataSrc, dataDest);
    fs.writeFileSync(marker, 'ok');
    console.error(`[tyk-docs-mcp] cached at ${cacheDir}`);
  }
  return { probePath: probeDest, dataDir: dataDest };
}

async function main() {
  if (!fs.existsSync(BUNDLE_PATH)) {
    fail(`Bundle not found at ${BUNDLE_PATH}. Run build.sh in mcps/docs (while online) first.`);
  }

  if (IS_PACKAGED) {
    const { probePath, dataDir } = extractPackagedAssets();
    process.env.PROBE_PATH = process.env.PROBE_PATH || probePath;
    process.env.DATA_DIR = process.env.DATA_DIR || dataDir;
  } else {
    process.env.PROBE_PATH =
      process.env.PROBE_PATH || path.join(PKG_ROOT, 'node_modules', '@buger', 'probe', 'bin', 'probe');
    process.env.DATA_DIR =
      process.env.DATA_DIR || path.join(PKG_ROOT, 'node_modules', '@tyk-technologies', 'docs-mcp', 'data');
  }
  // The bundle can't resolve docs-mcp's own bundled docs-mcp.config.json
  // (its relative path resolution doesn't survive bundling), so replicate
  // its defaults here instead.
  process.env.TOOL_NAME = process.env.TOOL_NAME || 'search_tyk_docs';
  process.env.TOOL_DESCRIPTION = process.env.TOOL_DESCRIPTION || 'Search Tyk API management documentation';

  require(BUNDLE_PATH);
}

main().catch((err) => fail(err.message || String(err)));
