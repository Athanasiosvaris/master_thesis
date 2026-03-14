import os
import sys
from venv import create
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import joblib
import boto3
import psycopg2
from botocore.client import Config

"""
Reads database and brings latest 600 data
Trains the model 
Uploads based in Rustfs
Example usage: 
python3 initial_train.py --csv_file /home/thanos/master_thesis_monorepo/apache-pulsar/data/missing_timestamp_data/device_5_data_2025-12-08_2025-12-09.csv --bucket_name missingtimestamp  --model_name device5
"""

# CONFIG
ROW_LIMIT = 600
LOOK_BACK = 60
EPOCHS = 200
BATCH_SIZE = 32


np.random.seed(5)

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



def fetch_data_from_db(conn,table_name:str):
    cur = conn.cursor()
    query = f"select sensor_id,sensor_energy_value,sensor_timestamp from {table_name} order by sensor_timestamp desc limit 600;"
    cur.execute(query)  
    rows  = cur.fetchall()
    rows = rows[::-1]  #reverse the order of the list
    return rows


def dataset_preparation(rows: list):

    df = pd.DataFrame(rows, columns=['sensor_id', 'sensor_energy_value', 'sensor_timestamp'])
    df = df.iloc[:ROW_LIMIT]
    first_timestamp = str(df['sensor_timestamp'].iloc[0])
    first_timestamp = first_timestamp.replace(" ","-").replace(":","-")
    last_timestamp = str(df['sensor_timestamp'].iloc[-1])
    last_timestamp = last_timestamp.replace(" ","-").replace(":","-")
    values = df["sensor_energy_value"].values.astype("float32")
    dataset = values.reshape(-1, 1)

    return dataset, first_timestamp, last_timestamp

def boto3_client():
    # Create a boto3 client for s3
    s3_client = boto3.client(
        's3',
        endpoint_url="http://localhost:9002",
        aws_access_key_id='rustfsadmin',
        aws_secret_access_key='rustfsadmin',
        config=Config(signature_version='s3v4'))
    return s3_client
 

def create_dataset(dataset, look_back=1):
    # CREATE DATASET FOR LSTM
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        dataX.append(dataset[i : (i + look_back), 0])
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)



def create_model(dataset, model_name: str) -> None:
    # TRAIN / TEST SPLIT (50/50)
    train_size = int(len(dataset) * 0.5)
    train, test = dataset[:train_size], dataset[train_size:]
    # NORMALIZATION (IMPORTANT)
    scaler = MinMaxScaler(feature_range=(0, 1))
    train = scaler.fit_transform(train)  # fit ONLY on training data
    test = scaler.transform(test)
    joblib.dump(scaler, "scaler.save")  # save scaler
    # CREATE LSTM DATASETS
    trainX, trainY = create_dataset(train, LOOK_BACK)
    testX, testY = create_dataset(test, LOOK_BACK)
    trainX = trainX.reshape(trainX.shape[0], trainX.shape[1], 1)
    testX = testX.reshape(testX.shape[0], testX.shape[1], 1)
    # BUILD LSTM MODEL
    model = Sequential()
    model.add(LSTM(25, input_shape=(LOOK_BACK, 1)))
    model.add(Dropout(0.1))
    model.add(Dense(1))
    model.compile(loss="mse", optimizer="adam")
    # TRAIN MODEL
    model.fit(trainX, trainY, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)
    # SAVE MODEL
    model.save(f"./{model_name}")

def create_bucket_if_not_exists(s3_client, bucket_name: str) -> None:
  try:
      s3_client.create_bucket(Bucket=bucket_name)
      print(f'Bucket {bucket_name} created.')
  except s3_client.exceptions.BucketAlreadyOwnedByYou:
      print(f'Bucket {bucket_name} already exists.')

def upload_model_to_rustfs(model_name: str, s3_client, bucket_name: str, device_name: str, first_timestamp: str, last_timestamp: str) -> None:
    
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # This function would contain the logic to upload the model to rustfs.
    # For example, it could use an API client to send the model file to rustfs.
    
    print(f"Uploading {model_name} to bucket {bucket_name}...")
    s3_client.upload_file(f"./{model_name}", bucket_name, f"{device_name}/{first_timestamp}-{last_timestamp}-model/{model_name}")
    print(f"{model_name} uploaded to bucket {bucket_name}.")
    os.remove(f"./{model_name}")  # Clean up local file after upload

    print(f"Uploading scaler to bucket {bucket_name}...")
    s3_client.upload_file(f"./scaler.save", bucket_name, f"{device_name}/{first_timestamp}-{last_timestamp}-model/scaler.save")
    print(f"scaler.save uploaded to bucket {bucket_name}.")
    os.remove(f"./scaler.save")  # Clean up local file after upload
    
    return None

def parse_arguments():

    parser = argparse.ArgumentParser(description="Train LSTM model on sorted data.")
    parser.add_argument("--device_name", type=str, required=True, help="Name of the device for which to train the model.")
    parser.add_argument("--bucket_name", type=str, choices=["batch", "missingtimestamp"], required=True, help="Bucket name to upload the model to (batch or missingtimestamp).")
    parser.add_argument("--database_table", type=str, required=True, help="Name of the database table containing the actual values.")
    return parser.parse_args()

if __name__ == "__main__":
    
    args = parse_arguments()
    device_name = args.device_name
    bucket_name = args.bucket_name
    database_table = args.database_table
    
    model_name = device_name + ".keras"
    conn = connect_to_database()
    if conn:
        rows = fetch_data_from_db(conn, database_table)
        dataset, first_timestamp, last_timestamp = dataset_preparation(rows)
    print(f"Retraining model for device {device_name} with data from table {database_table} between timestamps {first_timestamp} and {last_timestamp}...")
    create_model(dataset, model_name)
    
    s3_client = boto3_client()
    print(f"Using bucket name: {bucket_name}")
    create_bucket_if_not_exists(s3_client, bucket_name)
    upload_model_to_rustfs(model_name, s3_client, bucket_name, device_name, first_timestamp, last_timestamp)
    
    sys.exit(0)