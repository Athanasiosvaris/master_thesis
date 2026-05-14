import pandas as pd
import time

# Function that receives an UNSORTED list of dictionaries like the following :
# data = [
#    {"sensor_id": 1, "sensor_energy_value": 695.3, "sensor_timestamp": 1765152003, "message_creation_time": 1765152003123},
#    {"sensor_id": 1, "sensor_energy_value": 693.7, "sensor_timestamp": 1765152004, "message_creation_time": 1765152004118},
#     .....
# ]
# sensor_timestamp is epoch seconds, message_creation_time is epoch milliseconds.
# Returns a sorted (based on timestamp) 60-record dataframe (1 record/sec). Missing
# seconds are reindexed in and their sensor_energy_value / message_delay are filled
# with the column mean. message_creation_time is converted into message_delay
# (current_time_ms - message_creation_time_ms).


def dataPreparation(data):
    SortedData = sorted(data, key=lambda d: d["sensor_timestamp"])
    df = pd.DataFrame(SortedData)
    sensor_id = df["sensor_id"].iloc[0]

    # Converting epoch timestamp (it was in seconds) into data time {1765152003 =>2025-12-08 00:00:03}
    df["sensor_timestamp"] = pd.to_datetime(df["sensor_timestamp"], unit="s")
    df = df.set_index("sensor_timestamp")
    df = df[~df.index.duplicated(keep="last")]

    epoch_time = int(time.time() * 1000)  # Current time in milliseconds
    df["message_creation_time"] = epoch_time - df["message_creation_time"]
    df = df.rename(columns={"message_creation_time": "message_delay"})
    # Determine the minute (floor to minute)
    minute_start = df.index.min().floor("min")

    # Build full minute index: 00 → 59
    full_index = pd.date_range(start=minute_start, periods=60, freq="1s")
    df = df.reindex(full_index)
    df["sensor_id"] = sensor_id
    df = df.assign(
        sensor_energy_value=df.sensor_energy_value.fillna(
            df.sensor_energy_value.mean()
        ),
        message_delay=df.message_delay.fillna(df.message_delay.mean()),
    )
    df = df.reset_index()
    df = df.rename(columns={"index": "sensor_timestamp"})
    return df
