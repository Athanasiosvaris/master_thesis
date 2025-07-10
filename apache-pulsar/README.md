# Apache Pulsar-Master Thesis Project

# 🚀 Apache Pulsar with MQTT Support (via MoP)

This master thesis focuses on real-time energy message forecasting, using Mqqt protocol to communicate with the sensors, Apache Pulsar to stream the messages and Apache Flink to compute forecasting. The messages are
being consumed in real time and the forecasting is being created and updated in real time.

---

## Step 1: Install Apache Pulsar using Docker

Use the following command to download and start a Pulsar standalone container:

```bash
docker run -it \
  -p 6650:6650 \
  -p 8080:8080 \
  -p 1883:1883 \
  --name pulsar \
  --mount source=pulsardata,target=/pulsar/data \
  --mount source=pulsarconf,target=/pulsar/conf \
  apachepulsar/pulsar-all:4.0.3 \
  bin/pulsar standalone
```

## Step 2: Install MQTT Protocol Handler (MoP)
To install MQTT support in Pulsar, integrate the MoP (MQTT on Pulsar) protocol handler.

Follow the official guide here:
👉 https://github.com/streamnative/mop

## Step 3: Run Apache Flink in Docker
