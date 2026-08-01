#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
  uv venv --clear .venv
  uv pip install --python .venv/bin/python pip
  uv pip install --python .venv/bin/python -r requirements.txt
else
  if ! python3 -m venv .venv; then
    rm -rf .venv
    cat >&2 <<'EOF'
Could not create .venv with python3 -m venv.

On Debian/Ubuntu this usually means the python3-venv package is missing.
Install it once, then rerun this script:

  sudo apt install python3.10-venv

If you use uv, install uv and this script will use `uv venv` automatically.
EOF
    exit 1
  fi
fi

. .venv/bin/activate

if python -m pip --version >/dev/null 2>&1; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

python - <<'PY'
import pandas as pd
import matplotlib

print("pandas:", pd.__version__)
print("matplotlib:", matplotlib.__version__)
print("Environment is ready.")
PY
