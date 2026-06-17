#!/usr/bin/env python3
"""Parse a1 scaling-experiment architecture1 per-device coordinator logs into CSVs.

logs1/ holds one coordinator log per device: coordinator_service_device<N>.log
Each log has repeated pairs of tables:
  - "Actual values fetched from database":
      <row idx> sensor_id sensor_energy_value sensor_timestamp message_delay
  - "Forecasted values:":
      <row idx> sensor_id sensor_energy_value_prediction sensor_timestamp

Writes one CSV per device: actual columns, a blank separator column, then the
forecast columns, row-aligned by position within each block.
"""
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(HERE, "logs1")
DEVICE_RE = re.compile(r"coordinator_service_(device\d+)\.log$")

# Actual row: idx sensor_id energy "YYYY-MM-DD HH:MM:SS" delay
ACTUAL_RE = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+([-\d.]+)\s+"
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+([-\d.]+)\s*$"
)
# Forecast row: idx sensor_id prediction "YYYY-MM-DD HH:MM:SS"
FORECAST_RE = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+([-\d.]+)\s+"
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*$"
)

ACTUAL_MARKER = "Actual values fetched from database"
FORECAST_MARKER = "Forecasted values:"

HEADER = [
    "block", "id", "sensor_id", "sensor_energy_value", "sensor_timestamp", "message_delay",
    "",
    "block", "id", "sensor_id", "sensor_energy_value_prediction", "sensor_timestamp",
]


def parse_log(path):
    """Return a list of blocks; each block is (actual_rows, forecast_rows)."""
    blocks = []
    actual, forecast = None, None
    mode = None  # None | "actual" | "forecast"

    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if ACTUAL_MARKER in line:
                actual, forecast = [], []
                blocks.append((actual, forecast))
                mode = "actual"
                continue
            if FORECAST_MARKER in line:
                mode = "forecast"
                continue
            if mode == "actual":
                m = ACTUAL_RE.match(line)
                if m:
                    idx, sid, energy, ts, delay = m.groups()
                    actual.append((int(idx), int(sid), float(energy), ts, float(delay)))
                elif line.strip() and "sensor_id" not in line:
                    mode = None
            elif mode == "forecast":
                m = FORECAST_RE.match(line)
                if m:
                    idx, sid, pred, ts = m.groups()
                    forecast.append((int(idx), int(sid), float(pred), ts))
                elif line.strip() and "sensor_id" not in line:
                    mode = None
    return blocks


def main():
    logs = sorted(
        glob.glob(os.path.join(LOGS_DIR, "coordinator_service_device*.log")),
        key=lambda p: int(re.search(r"device(\d+)", p).group(1)),
    )
    for log in logs:
        device = DEVICE_RE.search(os.path.basename(log)).group(1)
        out_path = os.path.join(LOGS_DIR, f"{device}.csv")
        blocks = parse_log(log)
        n = 0
        with open(out_path, "w", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(HEADER)
            for b, (actual, forecast) in enumerate(blocks):
                for i in range(max(len(actual), len(forecast))):
                    if i < len(actual):
                        idx, sid, energy, ts, delay = actual[i]
                        left = [b, idx, sid, energy, ts, delay]
                    else:
                        left = ["", "", "", "", "", ""]
                    if i < len(forecast):
                        idx, sid, pred, ts = forecast[i]
                        right = [b, idx, sid, pred, ts]
                    else:
                        right = ["", "", "", "", ""]
                    writer.writerow(left + [""] + right)
                    n += 1
        print(f"{os.path.basename(log)} -> {os.path.basename(out_path)}: "
              f"{len(blocks)} blocks, {n} rows")


if __name__ == "__main__":
    main()
