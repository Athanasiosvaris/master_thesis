from ast import parse

import subprocess
from typing import Optional
import pulsar
from pulsar.schema import *
from dataPreparationFunc import dataPreparation
import pandas as pd
import os
import psycopg2
import argparse

RETRAIN_TIMESTAMPS = {
    "first_batch": ["00:00:00", "00:09:59"],
    "second_batch": ["00:10:00", "00:19:59"],
    "third_batch": ["00:20:00", "00:29:59"],
    "fourth_batch": ["00:30:00", "00:39:59"],
    "fifth_batch": ["00:40:00", "00:49:59"],
    "sixth_batch": ["00:50:00", "00:59:59"],
}


class Sensor(Record):
    __namespace__ = "sensor"

    sensor_energy_value = Double()
    sensor_id = Integer()
    sensor_timestamp = Long()
    message_creation_time = Long()


def connect_to_database():

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port=5432,
        )
        if conn:
            print("Database connection established")
            return conn
    except psycopg2.OperationalError as e:
        print("Unable to connect to database:\n")
        print(e)


def insert_data_to_db(
    con, Sorted_Dataframe: pd.DataFrame, table_name: str
) -> bool:

    cur = con.cursor()
    for _, row in Sorted_Dataframe.iterrows():
        cur.execute(
            f"""
                INSERT INTO {table_name}
                (sensor_timestamp, sensor_id, sensor_energy_value,message_delay)
                VALUES (%s, %s, %s, %s)
                """,
            (
                row["sensor_timestamp"],
                row["sensor_id"],
                row["sensor_energy_value"],
                row["message_delay"],
            ),
        )
    con.commit()
    cur.close()
    return True


def check_if_table_exists(conn, table_name: str):
    try:
        cur = conn.cursor()
        cur.execute(f"""SELECT to_regclass('public.{table_name}')""")
        exists = cur.fetchone()[0]
        if exists == table_name.lower():
            cur.execute(f"""DROP TABLE {table_name};""")
            conn.commit()
            print(f"Dropped table {table_name}")

        cur.execute(f"""CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            sensor_id Integer,
            sensor_timestamp timestamp,
            sensor_energy_value double precision,
            message_delay double precision);""")
        conn.commit()
        print(f"Table {table_name} created successfully\n")
    except psycopg2.OperationalError as e:
        print(e)


def check_retrain(
    SorteDf: pd.DataFrame,
    device_name: str,
    bucket_name: str,
    database_table: str,
) -> list[str]:
    # Implementation for triggering retraining
    result = []
    last_timestamp = str(SorteDf["sensor_timestamp"].iloc[-1])

    for value in RETRAIN_TIMESTAMPS.values():
        if value[1] in last_timestamp:
            print(
                f"Triggering retrain for window beetween {value[0]} and {value[1]}"
            )
            print("lasttimestamp is ", last_timestamp)
            result = [value[0], last_timestamp]
            # Here I should call the retrain.py script to retrain the model with the new data.
            retrain(device_name, bucket_name, database_table)
            break
    return result


def retrain(device_name: str, bucket_name: str, database_table: str):
    script_path = os.path.join(
        os.path.dirname(__file__), "train_model/retrain.py"
    )
    cmd = [
        "python3",
        script_path,
        "--device_name",
        device_name,
        "--bucket_name",
        bucket_name,
        "--database_table",
        database_table,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"retrain.py failed:\n{result.stderr}")
    else:
        print(f"retrain.py completed successfully:\n{result.stdout}")


def prepare__retrain_result(result: list[str]):
    # It will return 2025-12-08-00-00-00, 2025-12-08-00-09-59
    date_prefix = str(result[1]).split(" ")[0]
    first_timestamp = (
        str(date_prefix + " " + result[0]).replace(" ", "-").replace(":", "-")
    )
    last_timestamp = str(result[1]).replace(" ", "-").replace(":", "-")
    model_path = f"{first_timestamp}-{last_timestamp}-model"
    print("Model path is: ", model_path)
    return model_path


def forecasting(
    device_name: str,
    bucket_name: str,
    retrain: bool,
    delete_forecasting_database: bool,
    model_path: Optional[str] = None,
):
    script_path = os.path.join(os.path.dirname(__file__), "Forecasting.py")
    cmd = [
        "python3",
        script_path,
        "--device_name",
        device_name,
        "--bucket_name",
        bucket_name,
    ]
    if retrain:
        cmd.append("--retrain")
    if delete_forecasting_database:
        cmd.append("--delete_forecasting_database")
    if model_path:
        cmd.append("--model_path")
        cmd.append(model_path)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Forecasting.py failed:\n{result.stderr}")
    else:
        print(f"Forecasting.py script logs\n{result.stdout}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Pulsar Consumer for Sensor Data"
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Name of the topic to subscribe to",
    )
    parser.add_argument(
        "--device_name",
        type=str,
        required=True,
        help="Name of the device to filter the data for",
    )
    args = parser.parse_args()
    topic = args.topic
    device_name = args.device_name

    client = pulsar.Client("pulsar://localhost:6650")
    consumer = client.subscribe(
        topic=topic,
        subscription_name="pythonSubscription",
        schema=AvroSchema(Sensor),
        initial_position=pulsar.InitialPosition.Latest,
    )
    print("Coordinator service started\n")

    data = []
    SortedDf = pd.DataFrame()
    conn = connect_to_database()
    database_table_name = device_name + "_actualvalues"
    check_if_table_exists(conn, database_table_name)
    delete_forecasting_database = True
    use_retrain = False

    while True:
        try:
            msg = consumer.receive(5000)

        except pulsar.Timeout:
            print("No new messages received yet.Trying again...")
            if data:
                SortedDf = dataPreparation(data)
                insert_data_to_db(conn, SortedDf, database_table_name)
                print("\nActual data inserted to database")
                # Check if we need to trigger retraining
                results = check_retrain(
                    SortedDf,
                    device_name,
                    "missingtimestamp",
                    database_table_name,
                )
                if results or use_retrain:
                    # Retrain is triggered
                    if results:
                        model_path = prepare__retrain_result(results)
                    print("Triggering forecasting with retrained model")
                    forecasting(
                        device_name=device_name,
                        bucket_name="missingtimestamp",
                        retrain=True,
                        delete_forecasting_database=False,
                        model_path=model_path,
                    )
                    use_retrain = True
                    data.clear()
                    continue
                else:
                    print("No retrain triggered")
                # if results: ->Retrain is triggered
                # Forecasting.py should be called with the new data and the new model to make the predictions and then insert the data to the database.

                print("Triggering forecasting\n")
                forecasting(
                    device_name=device_name,
                    bucket_name="missingtimestamp",
                    retrain=False,
                    delete_forecasting_database=delete_forecasting_database,
                )
                delete_forecasting_database = False
                data.clear()
            continue

        try:
            ex = msg.value()
            data.append(
                {
                    "sensor_id": ex.sensor_id,
                    "sensor_energy_value": ex.sensor_energy_value,
                    "sensor_timestamp": ex.sensor_timestamp,
                    "message_creation_time": ex.message_creation_time,
                }
            )

            # Acknowledge successful processing of the message
            consumer.acknowledge(msg)
        except Exception as e:
            # Message failed to be processed
            print(f"Could not acknowledge message: {e}")
            consumer.negative_acknowledge(msg)
            break

    print("Closing consumer")
    consumer.close()
    print("Closing client")
    client.close()
