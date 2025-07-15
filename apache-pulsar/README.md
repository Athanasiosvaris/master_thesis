# Energy consumption forecasting app - Master Thesis Project
  
The thesis focused on creating a real-time forecasting app for the consumption of varius energy sensors.The forecasting was created and updated in real-time,as soon as the messages were created by the sensors.   
The software stack used was the following:

- **Mqtt protocol** to receive messages from sensors,  
- **Apache Pulsar** to stream the messages,  
- **Apache Flink** to compute forecasting,
- **PostegresSQL** database to store the data
  
The project was built in containerized environment using **Docker Desktop**.  
Below follows a detailed guide in order to recreate and test the project.

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
