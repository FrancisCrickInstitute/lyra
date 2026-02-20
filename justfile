set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default: dev

dev:
    if [ ! -d .venv ]; then uv venv .venv; fi
    source .venv/bin/activate && uv sync --group dev && python -V && which python && exec $SHELL
