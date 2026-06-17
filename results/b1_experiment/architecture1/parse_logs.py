#!/usr/bin/env python3
"""Parse architecture1 run logs into one CSV per run.

Each log contains repeated pairs of tables:
  - "Actual values fetched from database":
      <row idx> sensor_id sensor_energy_value sensor_timestamp message_delay
  - "Forecasted values:":
      <row idx> sensor_id sensor_energy_value_prediction sensor_timestamp

This writes, per run, the actual-value columns then a blank separator column
then the forecast columns, row-aligned by position within each block.
"""
import csv
import glob
import os
import re
import sys

RUN_RE = re.compile(r"architecture\d+_(\w+)_run_logs\.log$")

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


HEADER = [
    "block", "id", "sensor_id", "sensor_energy_value", "sensor_timestamp", "message_delay",
    "",
    "block", "id", "sensor_id", "sensor_energy_value_prediction", "sensor_timestamp",
]


def main():
    # Directory to scan (defaults to this script's dir); accepts e.g. ../architecture2
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    base = os.path.abspath(base)
    logs = sorted(glob.glob(os.path.join(base, "architecture*_*_run_logs.log")))
    if not logs:
        print(f"No run logs found in {base}")
        return
    # "architecture1" -> "A", "architecture2" -> "B", etc.
    arch_num = int(re.search(r"architecture(\d+)_", os.path.basename(logs[0])).group(1))
    arch_label = chr(ord("A") + arch_num - 1)
    for log in logs:
        run = RUN_RE.search(os.path.basename(log)).group(1)
        out_path = os.path.join(base, f"architecture{arch_label}_{run}_run.csv")
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
