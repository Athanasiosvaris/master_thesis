import pulsar
from pulsar.schema import *
from dataPreparationFunc import dataPreparation
import pandas as pd
import os
import psycopg2


OUTPUT_FILE = "sorted_data.csv"
TEMP_FILE = "sorted_data.tmp"


class Sensor(Record):
    __namespace__ = "sensor"

    sensor_energy_value = Double()
    sensor_id = Integer()
    sensor_timestamp = Long()


def connect_to_database():

    try:
        conn = psycopg2.connect(
            "dbname= 'postgres' user='postgres' password='postgres' port=5432 "
        )
        if conn:
            print("Database connection establiished")
            return conn
    except psycopg2.OperationalError as e:
        print("Unable to connect to database:\n")
        print(e)


def insert_data_to_db(con, Sorted_Dataframe: pd.DataFrame):

    cur = con.cursor()
    for _, row in Sorted_Dataframe.iterrows():
        cur.execute(
            """
                INSERT INTO ActualValues
                (sensor_timestamp, sensor_id, sensor_energy_value)
                VALUES (%s, %s, %s)
                """,
            (row["sensor_timestamp"], row["sensor_id"], row["sensor_energy_value"]),
        )
    con.commit()
    cur.close()


client = pulsar.Client("pulsar://localhost:6650")
consumer = client.subscribe(
    topic="modelConsumeTopic",
    subscription_name="pythonSubscription",
    schema=AvroSchema(Sensor),
)
print("Python Consumer started")

data = []
SortedDf = pd.DataFrame()
conn = connect_to_database()

while True:
    try:
        msg = consumer.receive(5000)
        if data.__len__() == 60:
            print("Current data...")
            SortedDf = dataPreparation(data)
            print(SortedDf)
            SortedDf.to_csv(TEMP_FILE, index=False)
            os.replace(TEMP_FILE, OUTPUT_FILE)
            insert_data_to_db(conn, SortedDf)
            data.clear()
    except pulsar.Timeout:
        print("No new messages received yet.Trying again.....")
        continue

    try:
        ex = msg.value()
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
