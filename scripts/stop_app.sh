#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../apache-pulsar"

CLASSES=(
    "mqttProducerClient_package.MqttClientProducerFinal"
    "mqttClient.MqttClientConsumerFinal"
    "postgress_sink.TestConsumerFinal"
)

any_killed=false

for class in "${CLASSES[@]}"; do
    pids=$(pgrep -f "exec.mainClass=$class" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo ">>> Stopping $class (PIDs: $pids)"
        kill $pids
        any_killed=true
    else
        echo ">>> $class is not running."
    fi
done

if $any_killed; then
    echo ""
    echo ">>> All processes stopped."
else
    echo ""
    echo ">>> No running processes found."
fi
