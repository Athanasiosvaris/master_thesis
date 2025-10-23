# Energy consumption forecasting app - Master Thesis Project
  
The thesis focused on creating a real-time forecasting app for the consumption of varius energy sensors.The forecasting was created and updated in real-time,as soon as the messages were created by the sensors.   
The software stack used was the following:

- **Mqtt protocol** to receive messages from sensors,   
- **Apache Pulsar** to stream the messages,  
- **Apache Flink** to compute forecasting,
- **PostegresSQL** database to store the data,
- **WebApp** application to view the results on localhost
  
The project was built in containerized environment using **Docker Desktop**.  
Below follows a detailed guide in order to recreate and test the project.

---
## Step 1: Install Mqtt Mosquitto Broker on Docker
Create a local folder named **mosquitto** with the following structure :  
- /mosquitto/config/mosquitto.conf
- /mosquitto/config/pwfile
- /mosquitto/data
- /mosquitto/log

In mosquitto.conf file add the following **minimalistic** configuration of the container.   
```bash
allow_anonymous false
listener 1883
listener 9001
protocol websockets
persistence true
password_file /mosquitto/config/pwfile
persistence_file mosquitto.db
persistence_location /mosquitto/data/
```
There are many more configurations options for the mosquitto broker and they can be reviewed here under the official [mosquitto documentation](https://mosquitto.org/man/mosquitto-conf-5.html).  
This folders are going to be mounted to the mosquitto container.   
Create the container using the follow docker command:
```bash
docker run -it --name mosquittoo \
-p 1884:1883 \
-p 9001:9001 \
-v PathTo/mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf \
-v PathTo/mosquitto/log:/mosquitto/log -v C:/Users/thano/containers/mosquitto/data:/mosquitto/data \
-v PathTo/mosquitto/config/pwfile:/mosquitto/config/pwfile \
eclipse-mosquitto
```
*Comment: PathTo is your absolute path until mosquitto folder.*   
Once the container is up and running, access it and create a user and it's password with the following commands:  
```bash
docker exec -it mosquitto sh
mosquitto_passwd -c /mosquitto/config/pwfile user1
```
With those credentials your Mqtt client will be able to communicate with the Mqtt broker.  
More details about mosquitto_passwd can be found under the official [mosquitto documentation](https://mosquitto.org/man/mosquitto_passwd-1.html). 

## Step 2: Install Apache Pulsar on Docker

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

## Step 3: Install MQTT Protocol Handler (MoP)
To install MQTT support in Pulsar, integrate the MoP (MQTT on Pulsar) protocol handler.

Follow the official guide here:
👉 https://github.com/streamnative/mop

## Step 4: Install Apache Flink on Docker
## Step 5: Install Postgres on Docker
The following command will pull you the image for postgres 12 and create a container based on that image.
```bash
docker run -d -it --rm \
  --name pulsar-postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=postgres \
  postgres:12
```

 ## Step 6: Docker Configuration
 Create a docker network and add its container to it.At the end your docker network should consist of:  
 1)Pulsar container (Apache Pulsar)  
 2)Taskmanager and Jobmanager containers (Apache Flink)  
 3)Mosquitto broker container (MQTT)  
 4)Postgres container (Postgres database)

 For detailed instructions on creating a Docker network and connecting containers, see the official Docker [documentation](https://docs.docker.com/reference/cli/docker/network/).
