import pandas as pd

# Function that receives an UNSORTED list of dictionaries like the following :
# data = [
#    {"sensor_id": 1, "sensor_energy_value": 695.3, "sensor_timestamp": 1765152003},
#    {"sensor_id": 1, "sensor_energy_value": 693.7, "sensor_timestamp": 1765152004},
#     .....
# ]
# and returns a sorted (based on timestamp) dataframe. Also, if a record misses from the
# initial list is beeing added to the dataframe.
# In the end the function returns a 60-records dataframe (1 record/per second)


def dataPreparation(data):
    SortedData = sorted(data, key=lambda d: d["sensor_timestamp"])
    df = pd.DataFrame(SortedData)
    # print("Sorted Data")
    # print(df)
    sensor_id = df["sensor_id"].iloc[0]

    # Converting epoch timestamp (it was in seconds) into data time {1765152003 =>2025-12-08 00:00:03}
    df["sensor_timestamp"] = pd.to_datetime(df["sensor_timestamp"], unit="s")
    df = df.set_index("sensor_timestamp")

    # Determine the minute (floor to minute)
    minute_start = df.index.min().floor("min")

    # Build full minute index: 00 → 59
    full_index = pd.date_range(start=minute_start, periods=60, freq="1s")
    df = df.reindex(full_index)
    df["sensor_id"] = sensor_id
    df = df.assign(
        sensor_energy_value=df.sensor_energy_value.fillna(df.sensor_energy_value.mean())
    )
    # print(df)
    df = df.reset_index()
    df = df.rename(columns={"index": "sensor_timestamp"})
    # print("Final Data")
    # print(df)
    return df
