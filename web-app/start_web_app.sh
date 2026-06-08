#!/bin/bash

cd "$(dirname "$0")"

echo "Starting backend..."
node src/backend.js &
BACKEND_PID=$!

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both."

wait
