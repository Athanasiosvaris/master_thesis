import __main__
from ast import parse

import numpy as np
from numpy.random import f
import pandas as pd
import tensorflow as tf
import joblib
import os
import psycopg2
import boto3
from botocore.client import Config
import argparse

pd.options.mode.chained_assignment = None
tf.random.set_seed(0)


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


def insert_data_to_db(con, forecasted_values_df: pd.DataFrame, database_table_name: str) :
    try:
        cur = con.cursor()
        for _, row in forecasted_values_df.iterrows():
            cur.execute(
                f"""
                     INSERT INTO {database_table_name}
                     (sensor_timestamp, sensor_id, sensor_energy_value_prediction)
                     VALUES (%s, %s, %s)
                    """,
                (
                    row["sensor_timestamp"],
                    row["sensor_id"],
                    row["sensor_energy_value_prediction"],
                ),
            )
        con.commit()
        cur.close()
    except psycopg2.OperationalError as e:
        print("Unable to insert data into database\n")
        print(e)
        return False

def check_if_table_exists(conn, database_table_name: str ):
    try:
        cur = conn.cursor()
        cur.execute(f"""SELECT to_regclass('public.{database_table_name}')""")
        exists = cur.fetchone()[0]
        if exists == database_table_name.lower():
            cur.execute(f"""DROP TABLE {database_table_name};""")
            conn.commit()
            print(f"Dropped table {database_table_name}")

        cur.execute(
            f"""CREATE TABLE {database_table_name} (
            id SERIAL PRIMARY KEY,
            sensor_id Integer,
            sensor_timestamp timestamp,
            sensor_energy_value_prediction double precision);"""
        )
        conn.commit()
        print(f"Table {database_table_name} created successfully")
    except psycopg2.OperationalError as e:
        print(e)

def boto3_client():
    # Create a boto3 client for s3
    s3_client = boto3.client(
        's3',
        endpoint_url="http://localhost:9002",
        aws_access_key_id='rustfsadmin',
        aws_secret_access_key='rustfsadmin',
        config=Config(signature_version='s3v4'))
    return s3_client

def fetch_model_and_scaler_from_s3(s3_client,device_name:str, bucket_name: str, model_path: str, retrain: bool):
    
    #s3.download_file('amzn-s3-demo-bucket', 'OBJECT_NAME', 'FILE_NAME')
    #OBJECT_NAME is the name of the file in the bucket, FILE_NAME is the name you want to save it as locally
    #Naming in rustfs: bucket_name/deviceX/timestamp/deviceX.keras or bucket_name/deviceX/initial/deviceX.keras
    if retrain:
        name = device_name+"/initial/"+device_name+".keras" # =>deviceX/initial/deviceX.keras
        scaler_name = device_name + "/" + "initial" + "/scaler.save"
    else:
        name = device_name+"/"+model_path+"/"+device_name+".keras"
        scaler_name = device_name + "/" + model_path + "/scaler.save"
    while True:
        try:
            s3_client.download_file(bucket_name, name, f"./{device_name}.keras")
            s3_client.download_file(bucket_name, scaler_name, f"./scaler.save")
            #If this downlo    ad files I want to retry
            model = tf.keras.models.load_model(f"./{device_name}.keras")
            scaler = joblib.load(f"./scaler.save")
            if model and scaler:
                print("Successfully downloaded model and scaler from S3")
            return model, scaler
        except Exception as e:
            print("Unable to download model and scaler from S3\n")
            print("Retrying...\n")


def fetch_actual_values_from_db(conn,database_table_name_actual_values:str):
    cur = conn.cursor()
    query = f"select sensor_id,sensor_energy_value,sensor_timestamp from {database_table_name_actual_values} order by sensor_timestamp desc limit 60;"
    cur.execute(query)  
    rows  = cur.fetchall()
    rows = rows[::-1]  #reverse the order of the list
    return rows

def dataset_preparation(rows: list):

    df = pd.DataFrame(rows, columns=['sensor_id', 'sensor_energy_value', 'sensor_timestamp'])
    #values = df["sensor_energy_value"].values.astype("float32")
    #dataset = values.reshape(-1, 1)
    
    return df

def forecasting(model,scaler, conn,bucket_name: str,database_table_name: str,database_table_name_actual_values: str):
        actual_values_df = dataset_preparation(fetch_actual_values_from_db(conn, database_table_name_actual_values))
        print("Actual values fetched from database")
        print(actual_values_df)
  
        forecasted_values_df = actual_values_df[["sensor_timestamp", "sensor_id"]]
        forecasted_values_df["sensor_timestamp"] = pd.to_datetime(
            forecasted_values_df["sensor_timestamp"]
        )
        forecasted_values_df["sensor_timestamp"] = forecasted_values_df[
            "sensor_timestamp"
        ] + pd.Timedelta(minutes=1)

        #id_values = actual_values_df["sensor_id"].values
        #timestamp_values = actual_values_df["sensor_timestamp"].values
        sensor_energy_value = actual_values_df["sensor_energy_value"].values

        # Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose.
        # It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.
        sensor_energy_value_reshaped = sensor_energy_value.reshape(-1, 1)
        #final_results = []

        # Normalization
        scaler = joblib.load("scaler.save")
        sensor_energy_value_scaled = scaler.transform(sensor_energy_value_reshaped)

        # generate the input and output sequences
        n_lookback = 60  # length of input sequences (lookback period)
        n_forecast = 60  # length of output sequences (forecast period)

        # Initial sliding window
        buffer = sensor_energy_value_scaled[-n_lookback:, 0]
        input_seq = buffer.reshape(1, n_lookback, 1)

        # Recursive multi-step forecast
        predictions_scaled = []

        for _ in range(n_forecast):
            next_scaled = model.predict(input_seq, verbose=0)[0, 0]
            predictions_scaled.append(next_scaled)

            # roll window
            input_seq[:, :-1, 0] = input_seq[:, 1:, 0]
            input_seq[:, -1, 0] = next_scaled

        # Inverse scale
        predictions = scaler.inverse_transform(
            np.array(predictions_scaled).reshape(-1, 1)
        ).flatten()

        # Add the predictions into the ForecastedDF
        forecasted_values_df = forecasted_values_df.assign(
            sensor_energy_value_prediction=predictions
        )
        print("Forecasted values:")
        print(forecasted_values_df)

        # Send into db
        if bucket_name == "missingtimestamps":
            insert_data_to_db( conn,forecasted_values_df,database_table_name)
            print("Forecasted values inserted into database")
            print("Exiting forecasting script")
        else:
            #It will be the batched so data
            insert_data_to_db(conn,forecasted_values_df,database_table_name)
            


#ToDo:
# - Make it be called from pulsarConsumer.py -> Read actual values from the database, make the predictions and then insert the forecasted values into the database.
# - Fetch model; and scaler from rustfs 

# args (bucket name, model name in rustfs, database table name to insert parameters)


if __name__ == "__main__":
    
        #Add arguments for bucket name, model name in rustfs and database table name to insert parameters   
        parser = argparse.ArgumentParser(description="Forecasting script for sensor data")
        parser.add_argument("--bucket_name", type=str, required=True,choices=["batch", "missingtimestamp"] ,help="Name of the S3 bucket to fetch the model and scaler from")
        parser.add_argument("--device_name", type=str, required=True, help="Name of the device to filter the data for")
        parser.add_argument("--model_path", type=str, required=False, help="Name of the model to fetch from S3 (without file extension)")
        parser.add_argument("--retrain", type=bool, required=True, help="Whether am forecasting for retrained model or for initial model")
        args = parser.parse_args()   
        
        database_table_name = args.device_name + "_forecastedvalues"
        database_table_name_actual_values = args.device_name + "_actualvalues"
        conn = connect_to_database()
        check_if_table_exists(conn, database_table_name)
        s3_client = boto3_client()
        model, scaler = fetch_model_and_scaler_from_s3(s3_client, args.device_name, args.bucket_name, args.model_path, args.retrain)
        forecasting(model, scaler, conn, args.bucket_name,database_table_name, database_table_name_actual_values)
