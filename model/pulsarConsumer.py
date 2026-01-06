import pulsar
from pulsar.schema import *
from dataPreparationFunc import dataPreparation
import pandas as pd


class Sensor(Record):
    __namespace__ = "sensor"

    sensor_energy_value = Double()
    sensor_id = Integer()
    sensor_timestamp = Long()


client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe(
    topic="modelConsumeTopic",
    subscription_name="pythonSubscription",
    schema=AvroSchema(Sensor),
)
print("Python Consumer started")

data = []
SortdedDf = pd.DataFrame()

while True:
    try:
        msg = consumer.receive(5000)

    except pulsar.Timeout:
        print("No new messages received yet.Trying again.....")

        if data:
            print("Current data...")
            SortdedDf = dataPreparation(data)
            print(SortdedDf)
            # -> SortedDf must be sent to the model
            data.clear()
            # print("No data yet in the list")
        # else:
        #   print("The list has the following data")
        #    SortdedDf = dataPreparation(data)
        #    print(SortdedDf)

        continue

    try:
        ex = msg.value()
        # print("Received message sensor_energy_value={} sensor_id ={} sensor_timestamp={}".format(  ex.sensor_energy_value, ex.sensor_id, ex.sensor_timestamp))
        data.append(
            {
                "sensor_id": ex.sensor_id,
                "sensor_energy_value": ex.sensor_energy_value,
                "sensor_timestamp": ex.sensor_timestamp,
            }
        )

        # Acknowledge successful processing of the message
        consumer.acknowledge(msg)
    except Exception:
        # Message failed to be processed
        print(
            "Could acknoledge the message. Sending negative acknowledge and closing consumer and client."
        )
        consumer.negative_acknowledge(msg)
        break

print("Closing consumer")
consumer.close()
print("Closing client")
client.close()
