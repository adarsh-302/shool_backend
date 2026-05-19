#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/sensor_env"

choose_python() {
    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    ./sensor_env/Scripts/streamlit run dashboard.py    if command -v python >/dev/null 2>&1; then
        echo "python"
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
        return
    fi

    echo "python3.12"

}

PYTHON_BIN="$(choose_python)"

echo "Removing existing virtual environment at $VENV_DIR"
rm -rf "$VENV_DIR"

echo "Creating virtual environment with $PYTHON_BIN"
"$PYTHON_BIN" -m venv "$VENV_DIR"

echo "Upgrading packaging tools"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "Installing project dependencies"
"$VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"

echo "Setup complete"
echo "Activate with:"
echo "  source sensor_env/bin/activate"
echo "Run the dashboard with:"
echo "  streamlit run dashboard.py"
