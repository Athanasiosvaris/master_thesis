#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRAFANA_URL="http://localhost:3000"
GRAFANA_AUTH="admin:admin"
PHASE_DURATION=${PHASE_DURATION:-180}  # 3 minutes default (in seconds)

# ── Validate arguments ───────────────────────────────────────────────────────
if [ -z "$1" ]; then
    echo "Usage: $0 <csv-directory>"
    echo ""
    echo "Expects in-order, producer-format CSV files in the given directory,"
    echo "one per device, named device_N_in_order_data_2025-12-08.csv for N = 1..MAX_DEVICES."
    echo ""
    echo "Environment variables:"
    echo "  MAX_DEVICES     Number of devices to scale to (default: 20)"
    echo "  PHASE_DURATION  Duration of each phase in seconds (default: 180 = 3 min)"
    exit 1
fi

CSV_DIR="$1"

# Resolve the CSV path for a given device number.
csv_for_device() {
    echo "$CSV_DIR/device_$1_in_order_data_2025-12-08.csv"
}

MAX_DEVICES=${MAX_DEVICES:-20}

# Verify CSV files exist
for i in $(seq 1 "$MAX_DEVICES"); do
    f=$(csv_for_device "$i")
    if [ ! -f "$f" ]; then
        echo "ERROR: Missing $f"
        exit 1
    fi
done
echo ">>> All $MAX_DEVICES CSV files found in $CSV_DIR"

# ── Helper: create Grafana annotation ─────────────────────────────────────────
annotate() {
    local text="$1"
    local tags="$2"
    local now_ms=$(($(date +%s) * 1000))
    curl -s -X POST "$GRAFANA_URL/api/annotations" \
        -u "$GRAFANA_AUTH" \
        -H "Content-Type: application/json" \
        -d "{\"dashboardUID\":\"resource-scaling\",\"time\":${now_ms},\"text\":\"${text}\",\"tags\":[${tags}]}" \
        > /dev/null 2>&1 || echo "    (annotation failed — is Grafana running?)"
}

# ── Helper: stop all app-level processes ──────────────────────────────────────
stop_all_apps() {
    echo ">>> Stopping all app processes..."

    # Stop Java processes (producer, consumer, postgres sink)
    for class in "mqttProducerClient_package.MqttClientProducerFinal" \
                 "mqttClient.MqttClientConsumerFinal" \
                 "postgress_sink.TestConsumerFinal"; do
        pids=$(pgrep -f "exec.mainClass=$class" 2>/dev/null || true)
        [ -n "$pids" ] && kill $pids 2>/dev/null && echo "    Stopped $class"
    done

    # Stop Python consumers
    pids=$(pgrep -f "coordinator_service.py" 2>/dev/null || true)
    [ -n "$pids" ] && kill $pids 2>/dev/null && echo "    Stopped coordinator_service.py"

    # Cancel all Flink jobs
    job_ids=$(docker exec taskmanager flink list -m jobmanager:8081 -r 2>/dev/null \
        | grep -oP '[0-9a-f]{32}' || true)
    for jid in $job_ids; do
        docker exec taskmanager flink cancel -m jobmanager:8081 "$jid" 2>/dev/null \
            && echo "    Cancelled Flink job $jid"
    done

    # Wait for processes to die
    sleep 5
    echo ">>> All app processes stopped."
}

# ── Helper: start a single device ─────────────────────────────────────────────
start_device() {
    local device_num=$1
    echo "    Launching device${device_num}..."
    "$SCRIPT_DIR/start_app.sh" "$(csv_for_device "$device_num")" "device${device_num}" &
    # Wait for the device pipeline to settle
    sleep 10
    echo "    device${device_num} running."
}

# ── Cleanup on Ctrl+C ────────────────────────────────────────────────────────
cleanup() {
    echo ""
    echo ">>> Experiment interrupted. Cleaning up..."
    annotate "Experiment ABORTED" "\"abort\""
    stop_all_apps
    exit 1
}
trap cleanup SIGINT

# ── Experiment ────────────────────────────────────────────────────────────────

TOTAL_TIME=$(( MAX_DEVICES * PHASE_DURATION / 60 ))

echo ""
echo "============================================="
echo "  Resource Consumption Scaling Experiment"
echo "============================================="
echo "  Devices:  1 -> $MAX_DEVICES (add one every $((PHASE_DURATION / 60)) min)"
echo "  Duration: $((PHASE_DURATION / 60)) min per phase"
echo "  Total:    ~${TOTAL_TIME} min"
echo "============================================="
echo ""
echo ">>> Make sure Grafana is open at $GRAFANA_URL"
echo ">>> Dashboard: Resource Consumption Scaling"
echo ""
read -p "Press ENTER to start the experiment..."

annotate "Experiment START" "\"experiment\",\"start\""

for device_num in $(seq 1 $MAX_DEVICES); do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Phase $device_num/$MAX_DEVICES: Adding device${device_num} ($device_num device(s) total)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    annotate "Phase $device_num: Added device${device_num} ($device_num total)" "\"phase\",\"${device_num}-devices\""

    start_device "$device_num"

    echo ">>> Waiting $((PHASE_DURATION / 60)) minutes with $device_num device(s) running..."
    remaining=$PHASE_DURATION
    while [ $remaining -gt 0 ]; do
        mins=$((remaining / 60))
        secs=$((remaining % 60))
        printf "\r    Time remaining: %02d:%02d " $mins $secs
        sleep 10
        remaining=$((remaining - 10))
    done
    echo ""
done

echo ""
echo "============================================="
echo "  Experiment COMPLETE"
echo "============================================="
annotate "Experiment END" "\"experiment\",\"end\""

echo ""
echo ">>> Stopping all processes..."
stop_all_apps

echo ""
echo ">>> Go to Grafana ($GRAFANA_URL) and review the dashboard."
echo ">>> Use the time picker to select the full experiment window."
echo ">>> Annotations mark each phase transition."
echo ">>> Export the dashboard or take screenshots for your thesis."
