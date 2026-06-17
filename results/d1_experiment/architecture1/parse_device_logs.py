#!/usr/bin/env python3
"""Parse d1_experiment architecture1 per-device coordinator logs into CSVs.

Each watermark config (0sec/5sec/10sec) holds one log per device:
  coordinator_service_device<N>.log

Each log has repeated "Actual values fetched from database" tables with columns:
  <row idx> sensor_id sensor_energy_value sensor_timestamp message_delay computed_value

This writes one CSV per device log (next to the log) with those actual values.
Forecasted values are ignored.
"""
import csv
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

WATERMARK_DIRS = ["0sec_watermark", "5sec_watermark", "10sec_watermark"]
DEVICE_RE = re.compile(r"coordinator_service_(device\d+)\.log$")

# Actual row: idx sensor_id energy "YYYY-MM-DD HH:MM:SS" delay computed_value
ACTUAL_RE = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+([-\d.]+)\s+"
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+([-\d.]+)\s+(\S+)\s*$"
)
ACTUAL_MARKER = "Actual values fetched from database"

HEADER = [
    "block", "id", "sensor_id", "sensor_energy_value",
    "sensor_timestamp", "message_delay", "computed_value",
]


def parse_log(path):
    """Yield CSV row dicts for every actual-values data line."""
    block = -1
    in_table = False
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if ACTUAL_MARKER in line:
                block += 1
                in_table = True
                continue
            if not in_table:
                continue
            m = ACTUAL_RE.match(line)
            if m:
                idx, sid, energy, ts, delay, computed = m.groups()
                yield {
                    "block": block,
                    "id": int(idx),
                    "sensor_id": int(sid),
                    "sensor_energy_value": float(energy),
                    "sensor_timestamp": ts,
                    "message_delay": float(delay),
                    "computed_value": computed,
                }
            elif line.strip() and "sensor_id" not in line:
                in_table = False  # table ended (forecast header / blank / other)


def main():
    for wm in WATERMARK_DIRS:
        wdir = os.path.join(HERE, wm)
        logs = sorted(glob.glob(os.path.join(wdir, "coordinator_service_device*.log")))
        for log in logs:
            device = DEVICE_RE.search(os.path.basename(log)).group(1)
            out_path = os.path.join(wdir, f"{device}_{wm}.csv")
            n = 0
            with open(out_path, "w", newline="") as out:
                writer = csv.DictWriter(out, fieldnames=HEADER)
                writer.writeheader()
                for row in parse_log(log):
                    writer.writerow(row)
                    n += 1
            print(f"{wm}/{os.path.basename(log)} -> {os.path.basename(out_path)}: {n} rows")


if __name__ == "__main__":
    main()
