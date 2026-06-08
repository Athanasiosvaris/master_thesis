#!/usr/bin/env bash
set -e

export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../apache-pulsar"
LOG_DIR="$SCRIPT_DIR/../logs"
mkdir -p "$LOG_DIR"

# ── Validate arguments ───────────────────────────────────────────────────────
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <path-to-csv> <device-name>"
    exit 1
fi
CSV_PATH="$1"
device="$2"

# ── Cleanup on Ctrl+C ─────────────────────────────────────────────────────────
cleanup() {
    echo ""
    echo ">>> Caught Ctrl+C, cleaning up..."

    for class in "mqttProducerClient_package.MqttProducerBatches" \
                 "mqttClient.MqttConsumerBatches" \
                 "postgress_sink.MqttHelperClientBatches"; do
        pids=$(pgrep -f "exec.mainClass=$class" 2>/dev/null || true)
        [ -n "$pids" ] && kill $pids && echo ">>> Stopped $class"
    done

    pgrep -f "pulsarConsumer60Batches.py" | xargs -r kill && echo ">>> Stopped pulsarConsumer60Batches"

    echo ">>> Done."
    exit 0
}

trap cleanup SIGINT

# ── Clear old logs ────────────────────────────────────────────────────────────
rm -f "$LOG_DIR"/*_"${device}".log "$LOG_DIR"/*"-${device}"
echo ">>> Old logs for ${device} cleared."

# ── Compile ───────────────────────────────────────────────────────────────────
echo ">>> Compiling..."
mvn -f "$PROJECT_DIR/pom.xml" compile -q
echo ">>> Done."

# ── Run helper ────────────────────────────────────────────────────────────────
run() {
    local class="$1"
    shift
    local log="$LOG_DIR/${class##*.}.log"
    echo ">>> Starting $class"
    if [ $# -gt 0 ]; then
        mvn -f "$PROJECT_DIR/pom.xml" exec:java -Dexec.mainClass="$class" "-Dexec.args=$*" -Dexec.workingdir="$PROJECT_DIR" >> "$log-${device}" 2>&1 &
    else
        mvn -f "$PROJECT_DIR/pom.xml" exec:java -Dexec.mainClass="$class" -Dexec.workingdir="$PROJECT_DIR" >> "$log-${device}" 2>&1 &
    fi
    echo "    PID $!  |  tail -f $log-${device}"
}

# ── Reset Pulsar topics (only the two used by architecture 2 — no ${device}_sink) ─
docker exec -d pulsar pulsar-admin topics delete "persistent://public/default/${device}" -f
docker exec -d pulsar pulsar-admin topics delete "persistent://public/default/${device}_model_consume" -f
sleep 2

echo ">>> Creating Pulsar topics..."
docker exec -d pulsar pulsar-admin topics create "persistent://public/default/${device}"
docker exec -d pulsar pulsar-admin topics create "persistent://public/default/${device}_model_consume"
docker exec  pulsar pulsar-admin topics list public/default
echo ">>> Pulsar topics created."

# ── Start the Python coordinator first (so it's subscribed before data arrives) ─
MODEL_DIR="$SCRIPT_DIR/../model"
source "$MODEL_DIR/.venv/bin/activate"
python3 -u "$MODEL_DIR/pulsarConsumer60Batches.py" --topic "${device}_model_consume" --device_name "${device}" >> "$LOG_DIR/pulsarConsumer60Batches_${device}.log" 2>&1 &
echo "    PID $!  | tail -f $LOG_DIR/pulsarConsumer60Batches_${device}.log"

sleep 2

# ── Start the bytes-to-Avro bridge between Pulsar topics ──────────────────────
run "postgress_sink.MqttHelperClientBatches" "${device}" "${device}_model_consume"
sleep 2
# ── Start the Mosquitto-to-Pulsar bridge ──────────────────────────────────────
run "mqttClient.MqttConsumerBatches" "${device}"
sleep 1
# ── Start the producer last ───────────────────────────────────────────────────
run "mqttProducerClient_package.MqttProducerBatches" "$CSV_PATH" "${device}"

echo ""
echo ">>> All processes started for ${device} (architecture 2 - no Flink)."
echo ">>> Logs: $LOG_DIR/*${device}*"

# Keep script alive so trap can fire on Ctrl+C
wait
