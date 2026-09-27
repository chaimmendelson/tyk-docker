#!/bin/sh
# Build a single, air-gap-ready standalone executable for tyk-docs-mcp.
# Run this once, while online. The resulting dist/tyk-docs-mcp needs
# nothing else at runtime -- no Node, no npm, no network.
#
# Layout:
#   assets/   source (package.json, the launcher script) + transient build
#             state (node_modules, the intermediate CJS bundle) -- cleaned
#             up after
#   dist/     the final executable(s), nothing else
#
# Cross-platform: by default builds both node22-linux-x64 and node22-win-x64
# (dist/tyk-docs-mcp and dist/tyk-docs-mcp.exe). PKG_TARGET overrides with a
# space-separated list of targets. See `npx @yao-pkg/pkg --help` for other values, e.g.
# node22-win-x64, node22-macos-x64, node22-macos-arm64. When cross-building
# for Windows, the bundled search binary (@buger/probe) is swapped for the
# matching Windows release asset -- `npm install` always downloads the
# binary for the machine running *this script*, not the pkg target, so a
# plain `npm install` on Linux would otherwise embed a Linux binary that
# can't run on Windows.
set -e
cd "$(dirname "$0")"

cd assets

cleanup() {
  rm -rf node_modules docs-mcp-bundle.cjs
}
trap cleanup EXIT

echo "==> npm install"
npm install

# Default: build both Linux and Windows. Set PKG_TARGET to build just one.
TARGETS="${PKG_TARGET:-node22-linux-x64 node22-win-x64}"

swap_probe_for_windows() {
  echo "==> cross-building for Windows: swapping in the Windows search binary"
  PROBE_VERSION=$(node -e "console.log(require('./node_modules/@buger/probe/package.json').version)")
  PROBE_URL="https://github.com/probelabs/probe/releases/download/v${PROBE_VERSION}/probe-v${PROBE_VERSION}-x86_64-pc-windows-msvc.zip"
  curl -sfL -o /tmp/tyk-docs-mcp-probe-win.zip "$PROBE_URL"
  python3 -c "
import zipfile, shutil
with zipfile.ZipFile('/tmp/tyk-docs-mcp-probe-win.zip') as z:
    for n in z.namelist():
        if n.endswith('probe.exe'):
            with z.open(n) as src, open('node_modules/@buger/probe/bin/probe', 'wb') as dst:
                shutil.copyfileobj(src, dst)
            break
    else:
        raise SystemExit('probe.exe not found in ' + '/tmp/tyk-docs-mcp-probe-win.zip')
"
  rm -f /tmp/tyk-docs-mcp-probe-win.zip
}

echo "==> bundling docs-mcp (ESM) into a single CJS file"
npx esbuild node_modules/@tyk-technologies/docs-mcp/src/index.js \
  --bundle --platform=node --format=cjs \
  --inject:./import-meta-url-shim.js --define:import.meta.url=importMetaUrl \
  --outfile=docs-mcp-bundle.cjs

# --public --public-packages "*": V8 bytecode caching is tied to the host
# platform's V8 build; cross-building (e.g. for Windows from Linux) produces
# bytecode the target V8 rejects at startup. This ships plain JS instead,
# avoiding that entirely (pkg's own error message recommends this combo).
# Windows goes last: the probe swap replaces the binary in node_modules.
for TARGET in $TARGETS; do
  case "$TARGET" in
    *win*) swap_probe_for_windows ;;
  esac
  echo "==> packaging single executable (target: $TARGET)"
  npx @yao-pkg/pkg . --targets "$TARGET" --public --public-packages "*" --output ../dist/tyk-docs-mcp
done

echo "==> done: dist/tyk-docs-mcp, dist/tyk-docs-mcp.exe"
