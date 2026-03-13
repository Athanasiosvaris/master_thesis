"""
Generate device2-device5 batch datasets replicating:
  data/batch_data/batch_values_input.csv

Properties preserved:
  - Same 3 columns: sensor_timestamp, sensor_id, sensor_energy_value
  - 2400 records each (original 300-record pattern tiled 8×, timestamps 00:00:00 → 00:39:59)
  - Timestamps in strict ascending order, NO gaps
  - Similar energy_value distribution; each device has a slight scale/noise variation
"""

import csv
import random
from datetime import datetime, timedelta

SEED    = 42
TARGET  = 2400   # records per device

INPUT  = '/home/thanos/master_thesis_monorepo/apache-pulsar/data/batch_data/batch_values_input.csv'
OUTPUT = '/home/thanos/master_thesis_monorepo/apache-pulsar/data/batch_data'

# (scale_factor, noise_std)
DEVICE_PROFILES = {
    2: (0.89,  7.0),   # slightly lower
    3: (1.05, 11.0),   # slightly higher, noisier
    4: (0.96,  5.5),   # close to original, low noise
    5: (1.11, 14.0),   # highest, noisiest
}

# Read original energy values only (300 records)
base_energies = []
with open(INPUT, newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        base_energies.append(float(row[2]))

n_base = len(base_energies)
# Tile to reach TARGET records
tiled_energies = (base_energies * ((TARGET // n_base) + 1))[:TARGET]

# Generate continuous timestamps starting at 2025-12-08 00:00:00, 1 s apart
start = datetime(2025, 12, 8, 0, 0, 0)
timestamps = [(start + timedelta(seconds=i)).strftime('%Y-%m-%d %H:%M:%S')
              for i in range(TARGET)]

print(f"Base pattern: {n_base} records  →  tiling to {TARGET} records")
print(f"Timestamp range: {timestamps[0]} → {timestamps[-1]}")

for device_id, (scale, noise) in DEVICE_PROFILES.items():
    rng = random.Random(SEED + device_id)
    out_path = f'{OUTPUT}/device_{device_id}_batch_data_2025-12-08.csv'

    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sensor_timestamp', 'sensor_id', 'sensor_energy_value'])
        for ts_str, orig_energy in zip(timestamps, tiled_energies):
            new_energy = max(50.0, orig_energy * scale + rng.gauss(0, noise))
            writer.writerow([ts_str, device_id, round(new_energy, 1)])

    values = []
    with open(out_path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            values.append(float(row[2]))

    print(f"device_{device_id}: {len(values)} records | "
          f"min={min(values):.1f}  max={max(values):.1f}  "
          f"mean={sum(values)/len(values):.1f}  →  {out_path}")

print("\nDone.")
