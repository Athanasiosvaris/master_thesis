"""
Generate device2-device5 datasets following the same patterns as:
  device_1_data_manipulated_2025-12-08_2025-12-09.csv

Pattern analysis:
  - Data spans 2025-12-08 00:00:00 to 2025-12-09 23:59:59 (UTC)
  - Each minute has 5-15 randomly missing timestamps (gaps)
  - Rows are NOT written in chronological order: consecutive batches from
    multiple concurrent streams are interleaved, so the file contains
    sequential runs of timestamps that jump back and forth in time
  - Power values follow a distribution centred ~600-700W with occasional
    higher-load bursts; each device has a slightly different scale/noise
"""

import csv
import random
from datetime import datetime, timezone, timedelta

SEED = 42
random.seed(SEED)

BASE_DIR   = '/home/thanos/master_thesis_monorepo/apache-pulsar/data/missing_timestamp_data'
INPUT_FILE = f'{BASE_DIR}/device_1_data_manipulated_2025-12-08_2025-12-09.csv'

START_TS = datetime(2025, 12, 8,  0, 0, 0, tzinfo=timezone.utc)
END_TS   = datetime(2025, 12, 9, 23, 59, 59, tzinfo=timezone.utc)

# Device profiles: (scale_factor, noise_std)
DEVICE_PROFILES = {
    2: (0.87,  8.0),
    3: (1.06, 12.0),
    4: (0.94,  6.5),
    5: (1.13, 15.0),
}

# ---------------------------------------------------------------------------
# 1. Read original power values, keyed by second offset from START_TS
# ---------------------------------------------------------------------------
print("Reading device_1 power values...")
power_by_offset = {}
with open(INPUT_FILE, newline='') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        ts = datetime.fromisoformat(row[2].replace('+00', '+00:00'))
        offset = int((ts - START_TS).total_seconds())
        power_by_offset[offset] = float(row[1])

total_seconds = int((END_TS - START_TS).total_seconds()) + 1
print(f"  Loaded {len(power_by_offset)} power readings over {total_seconds} possible seconds")

# ---------------------------------------------------------------------------
# 2. Helper: given a minute's list of valid offsets, produce the interleaved
#    batch ordering that mimics device_1's concurrent-stream pattern
# ---------------------------------------------------------------------------
def interleave_batches(offsets):
    """
    Split `offsets` (already a sorted list of ints within one minute)
    into 2–4 randomly sized consecutive batches, then interleave them in
    the file in shuffled order so timestamps jump around — matching device_1.
    """
    if not offsets:
        return []

    n        = len(offsets)
    n_batches = random.randint(2, min(4, n))

    # Random split points, producing n_batches slices
    cuts = sorted(random.sample(range(1, n), min(n_batches - 1, n - 1)))
    cuts = [0] + cuts + [n]
    batches = [offsets[cuts[i]:cuts[i+1]] for i in range(len(cuts) - 1)]

    # Shuffle the order in which batches are written to the file.
    # Occasionally (30 % chance) defer some batches — write them later,
    # simulating a slow stream that catches up after many minutes.
    random.shuffle(batches)
    return batches          # list of lists; caller flattens in this shuffled order


# ---------------------------------------------------------------------------
# 3. Build the complete offset schedule per device:
#    - per minute: drop 5–15 random seconds
#    - collect into interleaved batches
# ---------------------------------------------------------------------------
def build_schedule(device_seed):
    """Return a list of offsets in the order they will be written to the file."""
    rng = random.Random(device_seed)

    minutes_total = total_seconds // 60 + 1

    # We'll accumulate deferred batches (the "slow stream" effect)
    deferred = []   # list of (target_minute_idx, [offsets])
    schedule = []   # final flat list of offsets in file-write order

    for m in range(minutes_total):
        base = m * 60

        # All second offsets that exist in device_1 for this minute
        candidate_offsets = [
            base + s for s in range(60)
            if (base + s) <= (total_seconds - 1) and (base + s) in power_by_offset
        ]

        if not candidate_offsets:
            continue

        # Drop 5–15 seconds (gaps)
        n_gaps = rng.randint(5, min(15, len(candidate_offsets) - 1))
        drop   = set(rng.sample(candidate_offsets, n_gaps))
        valid  = [o for o in candidate_offsets if o not in drop]

        if not valid:
            continue

        # Split into interleaved batches
        n       = len(valid)
        n_batch = rng.randint(2, min(4, n))
        cuts    = sorted(rng.sample(range(1, n), min(n_batch - 1, n - 1)))
        cuts    = [0] + cuts + [n]
        batches = [valid[cuts[i]:cuts[i+1]] for i in range(len(cuts) - 1)]
        rng.shuffle(batches)

        # Occasionally defer one batch to simulate a late-arriving stream
        # (30 % chance, but only if there are at least 2 batches)
        deferred_now = []
        if len(batches) >= 2 and rng.random() < 0.30:
            idx = rng.randrange(len(batches))
            deferred_now.append(batches.pop(idx))

        # Write any deferred batches from previous minutes that are now "due"
        still_deferred = []
        for (target, batch) in deferred:
            if m >= target:
                for b in batch:
                    schedule.extend(b)
            else:
                still_deferred.append((target, batch))
        deferred = still_deferred

        # Write current minute's batches
        for b in batches:
            schedule.extend(b)

        # Register new deferred (deliver 1–3 minutes later)
        for b in deferred_now:
            delay = rng.randint(1, 3)
            deferred.append((m + delay, [b]))

    # Flush remaining deferred at the end
    for (_, batch) in deferred:
        for b in batch:
            schedule.extend(b)

    return schedule


# ---------------------------------------------------------------------------
# 4. Write CSV files
# ---------------------------------------------------------------------------
for device_id, (scale, noise) in DEVICE_PROFILES.items():
    print(f"Generating device{device_id}  (scale={scale}, noise±{noise})...")
    rng_power = random.Random(SEED + device_id)

    schedule = build_schedule(device_seed=SEED * 10 + device_id)

    out_path = f'{BASE_DIR}/device_{device_id}_data_2025-12-08_2025-12-09.csv'
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'aprt_power', 'timestamp'])
        for offset in schedule:
            orig_power = power_by_offset[offset]
            new_power  = max(50.0, orig_power * scale + rng_power.gauss(0, noise))
            ts         = START_TS + timedelta(seconds=offset)
            ts_str     = ts.strftime('%Y-%m-%d %H:%M:%S+00')
            writer.writerow([device_id, round(new_power, 1), ts_str])

    # Quick stats
    gaps_per_min = []
    for m in range(total_seconds // 60 + 1):
        base = m * 60
        present = sum(1 for o in schedule if base <= o < base + 60)
        possible = sum(1 for s in range(60)
                       if (base + s) <= (total_seconds - 1)
                       and (base + s) in power_by_offset)
        if possible > 0:
            gaps_per_min.append(possible - present)

    avg_gap = sum(gaps_per_min) / len(gaps_per_min) if gaps_per_min else 0
    print(f"  Written {len(schedule):,} records  |  avg gaps/min={avg_gap:.1f}  "
          f"min={min(gaps_per_min)}  max={max(gaps_per_min)}  →  {out_path}")

print("\nDone.")
