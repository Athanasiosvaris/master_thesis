import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os
import psycopg2

pd.options.mode.chained_assignment = None
tf.random.set_seed(0)

CSV_FILE = "sorted_data.csv"
CSV_FILE_60_BATCHES = "60_batch_values.csv"


def connect_to_database():

    try:
        conn = psycopg2.connect(
            "dbname= 'postgres' user='postgres' password='postgres' port=5432 "
        )
        if conn:
            print("Database connection established")
            return conn
    except psycopg2.OperationalError as e:
        print("Unable to connect to database:\n")
        print(e)


def insert_data_to_db(con, forecasted_values_df: pd.DataFrame, table_name: str) -> bool:
    try:
        cur = con.cursor()
        for _, row in forecasted_values_df.iterrows():
            cur.execute(
                f"""
                     INSERT INTO {table_name}
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
        return True
    except psycopg2.OperationalError as e:
        print("Unable to insert data into database\n")
        print(e)
        return False


conn = connect_to_database()
print("Waiting for CSV...")

while True:
    if not os.path.exists(CSV_FILE) or not os.path.exists(CSV_FILE_60_BATCHES):
        continue

    if os.path.exists(CSV_FILE):
        help = "CSV_FILE"
        actual_values_df = pd.read_csv(CSV_FILE)
    else:
        help = "CSV_FILE_60_BATCHES"
        actual_values_df = pd.read_csv(CSV_FILE_60_BATCHES)

    print("CSV received")

    forecasted_values_df = actual_values_df[["sensor_timestamp", "sensor_id"]]
    forecasted_values_df["sensor_timestamp"] = pd.to_datetime(
        forecasted_values_df["sensor_timestamp"]
    )
    print(forecasted_values_df.dtypes)
    forecasted_values_df["sensor_timestamp"] = forecasted_values_df[
        "sensor_timestamp"
    ] + pd.Timedelta(minutes=1)

    model = tf.keras.models.load_model("lstm_initial_model_600.keras")

    id_values = actual_values_df["sensor_id"].values
    timestamp_values = actual_values_df["sensor_timestamp"].values
    sensor_energy_value = actual_values_df["sensor_energy_value"].values

    # Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose.
    # It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.
    sensor_energy_value_reshaped = sensor_energy_value.reshape(-1, 1)
    final_results = []

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
    print(forecasted_values_df)

    # Send into db

    if help == "CSV_FILE":
        if insert_data_to_db(
            conn,
            forecasted_values_df,
            "ForecastedValues",
        ):
            os.remove(CSV_FILE)
            print("CSV_FILE deleted")
    else:
        if insert_data_to_db(
            conn,
            forecasted_values_df,
            "ForecastedValuesBatched",
        ):
            os.remove(CSV_FILE_60_BATCHES)
            print("CSV_FILE_60_BATCHES deleted")
