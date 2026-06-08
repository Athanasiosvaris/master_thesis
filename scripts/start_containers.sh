#!/usr/bin/bash

# Pass --no-flink (or -n) to skip jobmanager + taskmanager.
SKIP_FLINK=0
for arg in "$@"; do
    case "$arg" in
        --no-flink|-n) SKIP_FLINK=1 ;;
        -h|--help)
            echo "Usage: $0 [--no-flink|-n]"
            echo "  --no-flink, -n   Do not start jobmanager and taskmanager containers"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Usage: $0 [--no-flink|-n]" >&2
            exit 1
            ;;
    esac
done

docker start pulsar
sleep 2

if [ "$SKIP_FLINK" -eq 0 ]; then
    docker start jobmanager
    sleep 2
    docker start taskmanager
    sleep 2
else
    echo "Skipping jobmanager and taskmanager (--no-flink)"
fi

docker start cadvisor
sleep 2
docker start prometheus
sleep 2
docker start grafana
sleep 2
docker start mosquittoo
sleep 2
docker start postgres
sleep 2
docker start rustfs_container
sleep 2
echo "All containers started"
echo "Running:"
echo "docker ps"
docker ps
