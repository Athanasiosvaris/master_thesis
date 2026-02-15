import pulsar
from pulsar.schema import *
import pandas as pd
import os
import psycopg2

batch = pd.DataFrame()
rows = []


class Sensor(Record):
    __namespace__ = "sensor"

    sensor_id = Integer()
    sensor_timestamp = Long()
    sensor_energy_value = Double()


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


def insert_data_to_db(con, batch: pd.DataFrame):

    cur = con.cursor()
    for _, row in batch.iterrows():
        cur.execute(
            """
                INSERT INTO ActualValuesBatched
                (sensor_id, sensor_timestamp, sensor_energy_value)
                VALUES (%s, %s, %s)
                """,
            (row["sensor_id"], row["sensor_timestamp"], row["sensor_energy_value"]),
        )
    con.commit()
    cur.close()


def create_consumer() -> pulsar.Consumer:
    client = pulsar.Client("pulsar://localhost:6650")
    consumer = client.subscribe(
        topic="model60BatchesConsumeTopicPython",
        subscription_name="pythonSubscription",
        schema=AvroSchema(Sensor),
    )
    print("Python Consumer started")
    return consumer


def read_messages(consumer: pulsar.Consumer, lines: list, conn: psycopg2.connect):
    while True:
        try:
            message = consumer.receive(5000)
            ex = message.value()
            rows.append(
                {
                    "sensor_id": ex.sensor_id,
                    "sensor_energy_value": ex.sensor_energy_value,
                    "sensor_timestamp": ex.sensor_timestamp,
                }
            )
            consumer.acknowledge(message)
            if len(rows) == 60:
                batch = pd.DataFrame(rows)
                print("Batch of 60 messages received")
                print(batch)
                insert_data_to_db(conn, batch)
                batch.to_csv("60_batch_values.csv", index=False)
                rows.clear()
        except pulsar.Timeout:
            print("No new messages received yet.Trying again...")


def main():
    conn = connect_to_database()
    consumer = create_consumer()
    read_messages(consumer, rows, conn)


if __name__ == "__main__":
    main()
