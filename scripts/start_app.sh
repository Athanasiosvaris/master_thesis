#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../apache-pulsar"
LOG_DIR="$SCRIPT_DIR/../logs"
mkdir -p "$LOG_DIR"

# ── Clear old logs ────────────────────────────────────────────────────────────
rm -f "$LOG_DIR"/*.log
echo ">>> Old logs cleared."

# ── Compile ───────────────────────────────────────────────────────────────────
echo ">>> Compiling..."
mvn -f "$PROJECT_DIR/pom.xml" compile -q
echo ">>> Done."

# ── Run ───────────────────────────────────────────────────────────────────────
run() {
    local class="$1"
    local log="$LOG_DIR/${class##*.}.log"
    echo ">>> Starting $class"
    mvn -f "$PROJECT_DIR/pom.xml" exec:java -Dexec.mainClass="$class" -Dexec.workingdir="$PROJECT_DIR" >> "$log" 2>&1 &
    echo "    PID $!  |  tail -f $log"
}

run "mqttProducerClient_package.MqttClientProducerFinal"
run "mqttClient.MqttClientConsumerFinal"
run "postgress_sink.TestConsumerFinal"

echo ""
echo ">>> All processes started. Follow logs with:"
echo "    tail -f $LOG_DIR/MqttClientProducerFinal.log $LOG_DIR/MqttClientConsumerFinal.log $LOG_DIR/TestConsumerFinal.log"
