#!/bin/sh
# Build a single, air-gap-ready standalone executable for tyk-dashboard-mcp.
# Run this once, while online. The resulting dist/tyk-dashboard-mcp needs
# nothing else at runtime -- no Node, no npm, no network (except reaching
# whatever TARGET_API_BASE_URL you point it at).
#
# Layout:
#   assets/   source (package.json, the launcher script) + transient build
#             state (node_modules, the downloaded spec) -- cleaned up after
#   dist/     the final executable(s), nothing else
set -e
cd "$(dirname "$0")"

SWAGGER_URL="https://raw.githubusercontent.com/TykTechnologies/tyk-docs/refs/heads/production/swagger/nightly/dashboard-swagger.yml"

cd assets

cleanup() {
  rm -rf node_modules dashboard-swagger.yml
}
trap cleanup EXIT

echo "==> npm install --ignore-scripts"
npm install --ignore-scripts

echo "==> fetching dashboard-swagger.yml"
curl -sfL -o dashboard-swagger.yml "$SWAGGER_URL"

TARGET="${PKG_TARGET:-node22-linux-x64}"
echo "==> packaging single executable (target: $TARGET)"
# --public --public-packages "*": V8 bytecode caching is tied to the host
# platform's V8 build; cross-building (e.g. for Windows from Linux) produces
# bytecode the target V8 rejects at startup. This ships plain JS instead,
# avoiding that entirely (pkg's own error message recommends this combo).
npx @yao-pkg/pkg . --targets "$TARGET" --public --public-packages "*" --output ../dist/tyk-dashboard-mcp

echo "==> done: dist/tyk-dashboard-mcp"
