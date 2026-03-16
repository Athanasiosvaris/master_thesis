# Master Thesis - Docker Compose Setup

This project uses Docker Compose to orchestrate multiple services for a data pipeline architecture. Below you will find the full service list, prerequisites, known issues, and setup instructions.

## Services Overview

| Service         | Image                                         | Host Ports             | Description                                    |
| --------------- | --------------------------------------------- | ---------------------- | ---------------------------------------------- |
| **Pulsar**      | `athanasiosvaris/backupimage_pulsar:version1` | `6650`, `8080`, `1883` | Apache Pulsar standalone (messaging/streaming) |
| **JobManager**  | `flink:1.17.2-scala_2.12-java11`              | `8081`                 | Apache Flink JobManager                        |
| **TaskManager** | `flink:1.17.2-scala_2.12-java11`              | —                      | Apache Flink TaskManager                       |
| **cAdvisor**    | `gcr.io/cadvisor/cadvisor:latest`             | `8079`                 | Container resource monitoring                  |
| **Prometheus**  | `prom/prometheus`                             | `9090`                 | Metrics collection and alerting                |
| **Grafana**     | `grafana/grafana-oss`                         | `3000`                 | Metrics visualization and dashboards           |
| **Mosquitto**   | `eclipse-mosquitto`                           | `1884`, `9001`         | MQTT broker                                    |
| **PostgreSQL**  | `postgres:12`                                 | `5432`                 | Relational database                            |
| **RustFS**      | `rustfs/rustfs:latest`                        | `9000`, `9002`         | S3-compatible object storage                   |

All services are connected via a custom Docker network named `pulsar-mosquitto`.

---

## Prerequisites

Before running `docker compose up`, you **must** create the required directories and configuration files on the host. Docker bind mounts expect these to exist — if they don't, Docker will create them as directories instead of files, causing containers to fail.

### 0. Configure the `.env` file

The `docker-compose.yml` uses a `HOST_HOME` variable for host volume paths, so it works on any machine. Before starting, edit the `.env` file in the project root and set `HOST_HOME` to your home directory:

```bash
cat > .env << 'EOF'
HOST_HOME=/home/<your-username>
EOF
```

> **Note:** This is required because running `docker compose` with `sudo` resolves `~` to `/root/` instead of your user home directory.

### 1. Mosquitto (Eclipse MQTT Broker)

Mosquitto requires a config file, a password file, and log/data directories to exist **before** starting the container.

```bash
# Create directory structure
mkdir -p ~/mosquitto/config ~/mosquitto/log ~/mosquitto/data

# Create the configuration file
cat > ~/mosquitto/config/mosquitto.conf << 'EOF'
allow_anonymous false
listener 1883
listener 9001
protocol websockets
persistence true
password_file /mosquitto/config/pwfile
persistence_file mosquitto.db
persistence_location /mosquitto/data/
EOF

# Create an empty password file
touch ~/mosquitto/config/pwfile
```

> **Important:** With `allow_anonymous false` and an empty password file, no MQTT client will be able to connect. After starting the container, create a user:
> ```bash
> docker exec -it mosquittoo mosquitto_passwd -c /mosquitto/config/pwfile <username>
> ```

### 2. Prometheus

Prometheus expects a configuration file at `./apache-pulsar/prometheus/prometheus.yml` (relative to where `docker compose` is run). Make sure this file exists before starting the stack.

```bash
# Verify the file exists
ls ./apache-pulsar/prometheus/prometheus.yml
```

### 3. RustFS

RustFS mounts `/mnt/rustfs/data` from the host. Create it with proper permissions:

```bash
sudo mkdir -p /mnt/rustfs/data
```

### 4. PostgreSQL

PostgreSQL stores its data at `~/postgres`. Docker will create the directory if it doesn't exist, but it's good practice to create it explicitly:

```bash
mkdir -p ~/postgres
```

---

## Quick Start

```bash
# 1. Complete all prerequisite steps above

# 2. Start all services
docker compose up -d

# 3. Verify all containers are running
docker compose ps

# 4. Check logs for any failing service
docker compose logs <service-name>
```

---

## Known Issues and Troubleshooting

### Port conflict on 1883

Both Pulsar and Mosquitto use MQTT port `1883` internally. They are mapped to **different host ports** (`1883` for Pulsar, `1884` for Mosquitto), so there is no actual conflict. However, be aware of which broker you're connecting to:

- **Pulsar MQTT** — `localhost:1883`
- **Mosquitto MQTT** — `localhost:1884`
- **Mosquitto WebSockets** — `localhost:9001`

### Mosquitto fails to start

**Symptom:** Container exits immediately or restarts in a loop.

**Cause:** The bind-mounted config file (`mosquitto.conf`) or password file (`pwfile`) did not exist on the host before starting the container. Docker created them as empty directories instead of files.

**Fix:**
```bash
# Stop and remove the container
docker compose down

# Remove the incorrectly created directories
rm -rf ~/mosquitto

# Re-create everything properly (see Prerequisites section)
mkdir -p ~/mosquitto/config ~/mosquitto/log ~/mosquitto/data
cat > ~/mosquitto/config/mosquitto.conf << 'EOF'
allow_anonymous false
listener 1883
listener 9001
protocol websockets
persistence true
password_file /mosquitto/config/pwfile
persistence_file mosquitto.db
persistence_location /mosquitto/data/
EOF
touch ~/mosquitto/config/pwfile

# Start again
docker compose up -d
```

### Prometheus fails to start

**Symptom:** Prometheus container exits immediately.

**Cause:** `./apache-pulsar/prometheus/prometheus.yml` does not exist.

**Fix:** Create or verify the Prometheus config file at the expected path before running `docker compose up`.

### RustFS permission errors

**Symptom:** RustFS container logs show permission denied errors.

**Cause:** `/mnt/rustfs/data` was auto-created by Docker with root-only permissions.

**Fix:**
```bash
sudo mkdir -p /mnt/rustfs/data
sudo chmod 777 /mnt/rustfs/data
```

---

## Service Access

| Service         | URL                     |
| --------------- | ----------------------- |
| Pulsar Admin    | `http://localhost:8080` |
| Flink Dashboard | `http://localhost:8081` |
| cAdvisor        | `http://localhost:8079` |
| Prometheus      | `http://localhost:9090` |
| Grafana         | `http://localhost:3000` |
| RustFS Console  | `http://localhost:9002` |

### Default Credentials

| Service    | Username      | Password          |
| ---------- | ------------- | ----------------- |
| PostgreSQL | `postgres`    | `postgres`        |
| RustFS     | `rustfsadmin` | `rustfsadmin`     |
| Grafana    | `admin`       | `admin` (default) |
