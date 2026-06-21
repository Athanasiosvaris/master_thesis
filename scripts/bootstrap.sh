#!/usr/bin/env bash
# Bootstrap a fresh checkout so `docker compose up` works first time.
# Creates the .env file, the Mosquitto config/dirs, PostgreSQL and RustFS
# data directories, and verifies the Prometheus config exists.
#
# Safe to re-run: it never overwrites an existing .env or mosquitto.conf.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# When run under sudo, `~` resolves to /root. Use the invoking user's home so
# the bind-mount paths match what HOST_HOME points at.
if [ -n "${SUDO_USER:-}" ]; then
    USER_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
else
    USER_HOME="$HOME"
fi

echo "==> Project dir: $PROJECT_DIR"
echo "==> Host home:   $USER_HOME"

# ---------------------------------------------------------------------------
# 0. .env / HOST_HOME
# ---------------------------------------------------------------------------
ENV_FILE="$PROJECT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "[skip] .env already exists ($ENV_FILE)"
else
    echo "HOST_HOME=$USER_HOME" > "$ENV_FILE"
    echo "[ok]   created .env with HOST_HOME=$USER_HOME"
fi

# ---------------------------------------------------------------------------
# 1. Mosquitto: dirs, config file, empty password file
# ---------------------------------------------------------------------------
mkdir -p "$USER_HOME/mosquitto/config" \
         "$USER_HOME/mosquitto/log" \
         "$USER_HOME/mosquitto/data"
echo "[ok]   created mosquitto config/log/data dirs"

MOSQ_CONF="$USER_HOME/mosquitto/config/mosquitto.conf"
if [ -f "$MOSQ_CONF" ]; then
    echo "[skip] mosquitto.conf already exists"
else
    cat > "$MOSQ_CONF" << 'EOF'
allow_anonymous false
listener 1883
listener 9001
protocol websockets
persistence true
password_file /mosquitto/config/pwfile
persistence_file mosquitto.db
persistence_location /mosquitto/data/
EOF
    echo "[ok]   created mosquitto.conf"
fi

# Must be a FILE, not a directory. Docker auto-creates missing bind-mount
# targets as directories, which makes mosquitto fail to start.
PWFILE="$USER_HOME/mosquitto/config/pwfile"
if [ -d "$PWFILE" ]; then
    echo "[warn] $PWFILE is a directory (Docker likely created it). Removing it."
    rmdir "$PWFILE" 2>/dev/null || rm -rf "$PWFILE"
fi
if [ ! -f "$PWFILE" ]; then
    touch "$PWFILE"
    echo "[ok]   created empty pwfile"
else
    echo "[skip] pwfile already exists"
fi

# ---------------------------------------------------------------------------
# 2. PostgreSQL data dir
# ---------------------------------------------------------------------------
mkdir -p "$USER_HOME/postgres"
echo "[ok]   created postgres data dir"

# ---------------------------------------------------------------------------
# 3. RustFS data dir (/mnt/rustfs/data — needs root)
#    Must be world-writable: the RustFS container runs as a non-root UID and
#    dies with "Permission denied (os error 13)" if it can't write here.
# ---------------------------------------------------------------------------
if [ ! -d /mnt/rustfs/data ]; then
    mkdir -p /mnt/rustfs/data 2>/dev/null || true
fi
if [ -d /mnt/rustfs/data ] && chmod 777 /mnt/rustfs/data 2>/dev/null; then
    echo "[ok]   /mnt/rustfs/data ready (world-writable)"
else
    echo "[warn] could not create/chmod /mnt/rustfs/data (need root). Run:"
    echo "       sudo mkdir -p /mnt/rustfs/data && sudo chmod 777 /mnt/rustfs/data"
fi

# ---------------------------------------------------------------------------
# 4. Prometheus config (shipped in repo — just verify)
# ---------------------------------------------------------------------------
if [ -f "$PROJECT_DIR/apache-pulsar/prometheus/prometheus.yml" ]; then
    echo "[ok]   prometheus.yml present"
else
    echo "[warn] missing apache-pulsar/prometheus/prometheus.yml — Prometheus will not start"
fi

echo
echo "Bootstrap complete. Next steps:"
echo "  1. docker compose up -d"
echo "  2. docker exec -it mosquittoo mosquitto_passwd -c /mosquitto/config/pwfile <username>"
echo "  3. docker restart mosquittoo"
