#!/usr/bin/env bash
# Train initial models for devices 6..20 and upload to rustfs.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$SCRIPT_DIR/../model"
DATA_DIR="$SCRIPT_DIR/../apache-pulsar/data/missingtimestamp"
LOG="$SCRIPT_DIR/../logs/train_new_devices.log"
mkdir -p "$SCRIPT_DIR/../logs"

START_DEV=${START_DEV:-6}
END_DEV=${END_DEV:-20}

# Activate the model venv (provides tensorflow / keras / boto3)
# shellcheck disable=SC1091
source "$MODEL_DIR/.venv/bin/activate"

# Scratch dir for the per-model artifacts (scaler.save + deviceN.keras).
WORK_DIR="$MODEL_DIR/_train_scratch"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "===========================================================" | tee -a "$LOG"
echo "Initial training run started at $(date -u +%FT%TZ)"          | tee -a "$LOG"
echo "Devices: $START_DEV..$END_DEV"                               | tee -a "$LOG"
echo "Working dir: $WORK_DIR"                                       | tee -a "$LOG"
echo "===========================================================" | tee -a "$LOG"

for n in $(seq "$START_DEV" "$END_DEV"); do
    CSV="$DATA_DIR/device_${n}_in_order_data_2025-12-08.csv"
    if [ ! -f "$CSV" ]; then
        echo "ERROR: missing $CSV" | tee -a "$LOG"
        continue
    fi

    echo ""                                                          | tee -a "$LOG"
    echo "----- device${n} ($(date -u +%FT%TZ)) -----"               | tee -a "$LOG"
    echo "csv = $CSV"                                                | tee -a "$LOG"

    python3 -u "$MODEL_DIR/train_model/initial_train.py" \
        --csv_file "$CSV" \
        --model_name "device${n}" \
        --bucket_name missingtimestamp \
        >> "$LOG" 2>&1 \
        && echo "device${n}: OK ($(date -u +%FT%TZ))"  | tee -a "$LOG" \
        || echo "device${n}: FAILED ($(date -u +%FT%TZ)) -- see $LOG" | tee -a "$LOG"
done

echo ""                                                              | tee -a "$LOG"
echo "All done at $(date -u +%FT%TZ)"                                | tee -a "$LOG"
echo "===========================================================" | tee -a "$LOG"
