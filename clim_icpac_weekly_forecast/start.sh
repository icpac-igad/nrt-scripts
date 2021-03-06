#!/bin/sh

set -xeu

# Change the NAME variable with the name of script
NAME=$(basename "$(pwd)")

LOG=${LOG:-udp://localhost}

REMOTE_WEEKLY_DATA_DIR=${REMOTE_WEEKLY_DATA_DIR:-}
LOCAL_WEEKLY_DATA_IN_DIR=${LOCAL_WEEKLY_DATA_IN_DIR:-}

# volume where processed data is saved
LOCAL_WEEKLY_DATA_OUT_VOL=${LOCAL_WEEKLY_DATA_OUT_VOL:-}

# build docker image
docker build -t "$NAME" --build-arg NAME="$NAME" .

# run container. Make sure all the volumes are correctly set
docker run -v "$LOCAL_WEEKLY_DATA_IN_DIR":/opt/"$NAME"/input -v "$LOCAL_WEEKLY_DATA_OUT_VOL":/opt/"$NAME"/data \
  --log-driver=syslog --log-opt syslog-address="$LOG" --log-opt tag="$NAME" -e CURRENT_UID="$CURRENT_UID" \
  --env-file .env --rm "$NAME" python main.py
