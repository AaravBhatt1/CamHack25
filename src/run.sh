#!/bin/bash
set -euo pipefail

ARGS=("$@")

YDTOOLD_BIN=/usr/bin/ydotoold
DISPLAY=./display.py
SERVER=./managerServer.py
LAUNCH=./main.py
LOGDIR=./logs/
mkdir -p "$LOGDIR"

cleanup() {
    echo "Exiting..."
    kill "$YDTOOLD_PID" "$SERVER_PID" "$DISPLAY_PID" "$LAUNCH_PID" 2>/dev/null || true
}
trap cleanup EXIT


echo "Starting ydotoold..."
sudo nohup "$YDTOOLD_BIN" > "$LOGDIR/ydotoold.out" 2> "$LOGDIR/ydotoold.err" < /dev/null &
YDTOOLD_PID=$!

echo "Starting server..."

python3 "$SERVER" > "$LOGDIR/server.log" 2>&1 &
SERVER_PID=$!

sleep 2

echo "Ydotoold ready, starting display..."

export DISPLAY=:0
if [ "${#ARGS[@]}" -eq 0 ]; then
    python3 "$DISPLAY" > "$LOGDIR/display.log" 2>&1 &
    DISPLAY_PID=$!
else
    python3 "$DISPLAY" "${ARGS[@]}" > "$LOGDIR/display.log" 2>&1 &
    DISPLAY_PID=$!
fi

sleep 1

echo "Starting main..."
if [ "${#ARGS[@]}" -eq 0 ]; then
    sudo python3 "$LAUNCH" > "$LOGDIR/main.log" 2>&1 &
    LAUNCH_PID=$!
else
    sudo python3 "$LAUNCH" "${ARGS[@]}" > "$LOGDIR/main.log" 2>&1 &
    LAUNCH_PID=$!
fi

nano
