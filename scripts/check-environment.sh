#!/usr/bin/env bash
# Execute com bash: nao depende do bit executavel preservado no clone.
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'ERRO: python3 nao encontrado. Instale Python >= 3.10 e python3-venv.' >&2
    exit 1
fi
if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    printf '%s\n' 'ERRO: use Python 3.10 ou superior (veja docs/AMBIENTE.md).' >&2
    exit 1
fi
cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/check_environment.py" "$@"
