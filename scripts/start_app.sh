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
FLINK_JOB_ID=""

cleanup() {
    echo ""
    echo ">>> Caught Ctrl+C, cleaning up..."

    if [ -n "$FLINK_JOB_ID" ]; then
        echo ">>> Cancelling Flink job $FLINK_JOB_ID..."
        docker exec taskmanager flink cancel -m jobmanager:8081 "$FLINK_JOB_ID"
    fi

    for class in "mqttProducerClient_package.MqttClientProducerFinal" \
                 "mqttClient.MqttClientConsumerFinal" \
                 "postgress_sink.TestConsumerFinal"; do
        pids=$(pgrep -f "exec.mainClass=$class" 2>/dev/null || true)
        [ -n "$pids" ] && kill $pids && echo ">>> Stopped $class"
    done

    pgrep -f "coordinator_service.py" | xargs -r kill && echo ">>> Stopped coordinator_service"

    rm -f "./${device}.keras" "./scaler.save"
    echo ">>> Removed local model files for ${device}"
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

# ── Run ───────────────────────────────────────────────────────────────────────
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

docker exec -d pulsar pulsar-admin topics delete "persistent://public/default/${device}" -f
docker exec -d pulsar pulsar-admin topics delete-partitioned-topic "persistent://public/default/${device}_sink" -f
docker exec -d pulsar pulsar-admin topics delete "persistent://public/default/${device}_model_consume" -f
sleep 2


echo ">>> Creating Pulsar topics..."
docker exec -d pulsar pulsar-admin topics create "persistent://public/default/${device}"
docker exec -d pulsar pulsar-admin topics create-partitioned-topic "persistent://public/default/${device}_sink" --partitions 1
docker exec -d pulsar pulsar-admin topics create "persistent://public/default/${device}_model_consume"
docker exec  pulsar pulsar-admin topics list public/default
docker exec  pulsar pulsar-admin topics list-partitioned-topics public/default
echo ">>> Pulsar topics created."

MODEL_DIR="$SCRIPT_DIR/../model"
source "$MODEL_DIR/.venv/bin/activate"
python3 -u "$MODEL_DIR/coordinator_service.py" --topic "${device}_model_consume" --device_name "${device}" >> "$LOG_DIR/coordinator_service_${device}.log" 2>&1 &
echo "    PID $!  | tail -f $LOG_DIR/coordinator_service_${device}.log"

echo "" 
job_output=$(docker exec taskmanager flink run --detached -m jobmanager:8081 ApacheFlink-0.0.1-SNAPSHOT.jar \
    --source-topic "persistent://public/default/${device}" \
    --sink-topic "persistent://public/default/${device}_sink")
FLINK_JOB_ID=$(echo "$job_output" | grep -oP '(?<=JobID )[0-9a-f]{32}')
echo ">>> Flink job started: $FLINK_JOB_ID"

sleep 2
run "postgress_sink.TestConsumerFinal" "${device}_sink" "${device}_model_consume"
run "mqttClient.MqttClientConsumerFinal" "$device"
run "mqttProducerClient_package.MqttClientProducerFinal" "$CSV_PATH" "$device"

echo ""
echo ">>> All processes started for ${device}."
echo ">>> Logs: $LOG_DIR/*${device}*"

# Keep script alive so trap can fire on Ctrl+C
wait
