#!/bin/sh
# Build standalone executables for tandoor-mcp (Linux + Windows).
# Run this once. The resulting dist/tandoor-mcp (and .exe) need nothing else at
# runtime -- no Python, no venv, no network (except reaching TANDOOR_BASE_URL).
#
# Layout:
#   assets/   Python source (pyproject.toml, src/, tests/)
#   dist/     the final executables, nothing else
#
# Windows cross-build uses Docker (batonogov/pyinstaller-windows). Skip it by
# setting PKG_TARGET=linux.
set -e
cd "$(dirname "$0")"

SOURCE_DIR="$(pwd)/assets"
DIST_DIR="$(pwd)/dist"

# Find uv (preferred) or fall back to system pip
if command -v uv >/dev/null 2>&1; then
    UV=uv
elif [ -f "$HOME/.local/bin/uv" ]; then
    UV="$HOME/.local/bin/uv"
else
    echo "uv not found -- install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

TARGETS="${PKG_TARGET:-linux windows}"

# ── Linux ───────────────────────────────────────────────────────────────────
case " $TARGETS " in *" linux "*)
    WORK_DIR="$(mktemp -d)"
    trap "rm -rf '$WORK_DIR'" EXIT

    echo "==> [linux] creating build environment"
    "$UV" venv "$WORK_DIR/venv" -q

    echo "==> [linux] installing tandoor-mcp + pyinstaller"
    "$UV" pip install --python "$WORK_DIR/venv/bin/python" \
        pyinstaller "$SOURCE_DIR" -q

    echo "==> [linux] building standalone executable"
    "$WORK_DIR/venv/bin/pyinstaller" \
        --onefile \
        --name tandoor-mcp \
        --distpath "$DIST_DIR" \
        --workpath "$WORK_DIR/build" \
        --specpath "$WORK_DIR" \
        "$SOURCE_DIR/src/tandoor_mcp/__main__.py"

    chmod +x "$DIST_DIR/tandoor-mcp"
    echo "==> [linux] done: dist/tandoor-mcp"
esac

# ── Windows (cross-compile via Docker + Wine) ────────────────────────────────
case " $TARGETS " in *" windows "*)
    if ! command -v docker >/dev/null 2>&1; then
        echo "==> [windows] skipping: docker not found"
    else
        echo "==> [windows] building standalone executable via Docker"
        docker run --rm \
            -v "${SOURCE_DIR}:/src:ro" \
            -v "${DIST_DIR}:/out" \
            batonogov/pyinstaller-windows:latest \
            "pip install -e /src -q && \
             pyinstaller --onefile --name tandoor-mcp \
               --distpath /out \
               --workpath /tmp/build \
               --specpath /tmp \
               /src/src/tandoor_mcp/__main__.py"
        echo "==> [windows] done: dist/tandoor-mcp.exe"
    fi
esac

echo "==> all done"
