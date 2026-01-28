import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os
import time
import psycopg2

pd.options.mode.chained_assignment = None
tf.random.set_seed(0)

CSV_FILE = "sorted_data.csv"

print("Waiting for CSV...")

while not os.path.exists(CSV_FILE):
    time.sleep(1)


SortdedDf = pd.read_csv(CSV_FILE)
print("CSV received")
print(SortdedDf)


os.remove(CSV_FILE)
print("CSV deleted")

print("I escaped the loop")
model = tf.keras.models.load_model("lstm_initial_model_600.keras")

id_values = SortdedDf["sensor_id"].values
timestamp_values = SortdedDf["sensor_timestamp"].values
sensor_energy_value = SortdedDf["sensor_energy_value"].values
# Reshaping in NumPy refers to modifying the dimensions of an existing array without changing its data. The reshape() function is used for this purpose. It reorganizes the elements into a new shape, which is useful in machine learning, matrix operations and data preparation.

sensor_energy_value_reshaped = sensor_energy_value.reshape(-1, 1)
final_results = []

# Normalization
scaler = joblib.load("scaler.save")
sensor_energy_value_scaled = scaler.transform(sensor_energy_value_reshaped)

# generate the input and output sequences
n_lookback = 60  # length of input sequences (lookback period)
n_forecast = 60  # length of output sequences (forecast period)


# -----------------------------
# INITIAL SLIDING WINDOW
# -----------------------------
buffer = sensor_energy_value_scaled[-n_lookback:, 0]

input_seq = buffer.reshape(1, n_lookback, 1)

# -----------------------------
# RECURSIVE MULTI-STEP FORECAST
# -----------------------------
predictions_scaled = []

for _ in range(n_forecast):
    next_scaled = model.predict(input_seq, verbose=0)[0, 0]
    predictions_scaled.append(next_scaled)

    # roll window
    input_seq[:, :-1, 0] = input_seq[:, 1:, 0]
    input_seq[:, -1, 0] = next_scaled

# -----------------------------
# INVERSE SCALE
# -----------------------------
predictions = scaler.inverse_transform(
    np.array(predictions_scaled).reshape(-1, 1)
).flatten()

print("Next 60 forecasted values:")
print(predictions)


# Send into db
conn = psycopg2.connect(
    "dbname= 'postgres' user='postgres' password='postgres' port=5432 "
)
cur = conn.cursor()
