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


def connect_to_database():

    try:
        conn = psycopg2.connect(
            dbname= "postgres", 
            user="postgres", 
            password="postgres",
            host="localhost",
            port=5432 
        )
        if conn:
            print("Database connection established")
            return conn
    except psycopg2.OperationalError as e:
        print("Unable to connect to database:\n")
        print(e)

def insert_data_to_db(con, Sorted_Dataframe: pd.DataFrame, table_name: str) -> bool:

    cur = con.cursor()
    for _, row in Sorted_Dataframe.iterrows():
        cur.execute(
            f"""
                INSERT INTO {table_name}
                (sensor_timestamp, sensor_id, sensor_energy_value)
                VALUES (%s, %s, %s)
                """,
            (row["sensor_timestamp"], row["sensor_id"], row["sensor_energy_value"]),
        )
    con.commit()
    cur.close()
    return True


def check_if_table_exists(conn, table_name: str ):
    try:
        cur = conn.cursor()
        cur.execute(f"""SELECT to_regclass('public.{table_name}')""")
        exists = cur.fetchone()[0]
        if exists == table_name.lower():
            cur.execute(f"""DROP TABLE {table_name};""")
            conn.commit()

        cur.execute(
            f"""CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            sensor_id Integer,
            sensor_timestamp timestamp,
            sensor_energy_value double precision);"""
        )
        conn.commit()
    except psycopg2.OperationalError as e:
        print(e)

def check_retrain(SorteDf: pd.DataFrame, device_name: str,bucket_name:str) -> list[str]:
    # Implementation for triggering retraining
    result = []
    last_timestamp = str(SorteDf['sensor_timestamp'].iloc[-1])
    
    for value in RETRAIN_TIMESTAMPS.values():
        if value[1] in last_timestamp:
            print(f"Triggering retrain for window beetween {value[0]} and {value[1]}")
            print("lasttimestamp is ", last_timestamp)
            result = [value[0], value[1]]
            #Here I should call the retrain.py script to retrain the model with the new data.
            #retrain.py(device_name, bucket_name,database_table)
            break
    return result

def prepare__retrain_result(result: list[str]):
    #It will return 2025-12-08-00-00-00, 2025-12-08-00-09-59
    if result:
        date_prefix = str(result[1]).split(" ")[0] 
        first_timestamp = str(date_prefix + " " + result[0]).replace(" ", "-").replace(":", "-")
        last_timestamp = str(result[1]).replace(" ", "-").replace(":", "-")
        return first_timestamp, last_timestamp
    else:
        return None, None

def forecasting(device_name: str, bucket_name: str,retrain: bool ,model_path: Optional[str] = None):
    script_path = os.path.join(os.path.dirname(__file__), "Forecasting.py")
    cmd = [
        "python3", script_path,
        "--device_name", device_name,
        "--bucket_name", bucket_name,
        "--retrain", str(retrain),
    ]
    if model_path:
        cmd += ["--model_path", model_path]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Forecasting.py failed:\n{result.stderr}")
    else:
        print(f"Forecasting.py completed successfully:\n{result.stdout}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Pulsar Consumer for Sensor Data")
    parser.add_argument("--topic", type=str, required=True, help="Name of the topic to subscribe to")
    parser.add_argument("--device_name", type=str, required=True, help="Name of the device to filter the data for")
    args = parser.parse_args()
    topic = args.topic
    device_name = args.device_name

    #topic = modelConsumeTopic
    client = pulsar.Client("pulsar://localhost:6650")
    consumer = client.subscribe(
        topic=topic,
        subscription_name="pythonSubscription",
        schema=AvroSchema(Sensor),
    )
    print("Python Consumer started")

    data = []
    SortedDf = pd.DataFrame()
    conn = connect_to_database()
    database_table_name = device_name + "_actualvalues"
    check_if_table_exists(conn,database_table_name)


    while True:
        try:
            msg = consumer.receive(5000)

        except pulsar.Timeout:
            print("No new messages received yet.Trying again...")
            if data:
                print("Current data...")
                SortedDf = dataPreparation(data)
                print(SortedDf)
                #Check if we need to trigger retraining
                #results = check_retrain(SortedDf, device_name, bucket_name)
                #if results: ->Retrain is triggered
                    #first_timestamp, last_timestamp = prepare__retrain_result(results)
                    #Forecasting.py should be called with the new data and the new model to make the predictions and then insert the data to the database.
                    #forecasting(model, scaler, conn, bucket_name, database_table_name)
                #Here I should call Forecasting.py to make the predictions and then insert the data to the database.
                #Forecasting.py should be called with the new data and the new model to make the predictions and then insert the data to the database.
                insert_data_to_db(conn, SortedDf, device_name)
                forecasting(device_name=device_name, bucket_name="missingtimestamp", retrain=False)
                data.clear()
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
