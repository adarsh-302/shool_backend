#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/sensor_env"
LOG_DIR="$ROOT_DIR/logs"
STREAMLIT_DIR="$ROOT_DIR/.streamlit"
CONSUMER_LOG="$LOG_DIR/mqtt_consumer.log"
DASHBOARD_LOG="$LOG_DIR/dashboard.log"
DEFAULT_PORT=8501

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found."
    echo "Run: bash setup.sh"
    exit 1
fi

mkdir -p "$LOG_DIR"
mkdir -p "$STREAMLIT_DIR"

CONSUMER_PID=""
DASHBOARD_PID=""

choose_port() {
    local port
    for port in 8501 8502 8503 8504 8505 8506 8507 8508 8509 8510; do
        if ! lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
            echo "$port"
            return 0
        fi
    done

    echo "8501"
    return 1
}

cleanup() {
    if [ -n "${DASHBOARD_PID:-}" ] && kill -0 "$DASHBOARD_PID" 2>/dev/null; then
        kill "$DASHBOARD_PID" 2>/dev/null || true
    fi

    if [ -n "${CONSUMER_PID:-}" ] && kill -0 "$CONSUMER_PID" 2>/dev/null; then
        kill "$CONSUMER_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

echo "Starting MQTT consumer..."
"$VENV_DIR/bin/python" "$ROOT_DIR/mqtt_consumer.py" >"$CONSUMER_LOG" 2>&1 &
CONSUMER_PID=$!

sleep 2

PORT="$(choose_port)"
if [ "$PORT" != "$DEFAULT_PORT" ]; then
    echo "Port $DEFAULT_PORT is busy. Using $PORT instead."
fi

echo "Starting dashboard..."
export STREAMLIT_CONFIG_DIR="$STREAMLIT_DIR"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false
"$VENV_DIR/bin/streamlit" run "$ROOT_DIR/dashboard.py" --server.address 127.0.0.1 --server.port "$PORT" >"$DASHBOARD_LOG" 2>&1 &
DASHBOARD_PID=$!

echo "Consumer log: $CONSUMER_LOG"
echo "Dashboard log: $DASHBOARD_LOG"
echo "Open: http://127.0.0.1:$PORT"
echo "Press Ctrl+C to stop both processes."

while true; do
    if ! kill -0 "$CONSUMER_PID" 2>/dev/null; then
        echo "MQTT consumer stopped. Check $CONSUMER_LOG"
        exit 1
    fi

    if ! kill -0 "$DASHBOARD_PID" 2>/dev/null; then
        echo "Dashboard stopped. Check $DASHBOARD_LOG"
        exit 1
    fi

    sleep 2
done
