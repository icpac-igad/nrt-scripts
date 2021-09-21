#!/bin/sh

#Change the NAME variable with the name of your script
NAME=$(basename $(pwd))
LOG=${LOG:-udp://localhost}

WEEKLY_INPUT_DATA_VOL=${WEEKLY_INPUT_DATA_VOL:-}
HOST_DATA_VOL=${WEEKLY_OUTPUT_DATA_VOL:-}
SSH_VOLUME=${SSH_VOLUME:-}

docker build -t "$NAME" --build-arg NAME="$NAME" .

if [ -z "$HOST_DATA_VOL" ]; then
  echo "Running container without host mounted volume. Data will not be persisted"
  docker run --log-driver=syslog --log-opt syslog-address="$LOG" --log-opt tag="$NAME" --env-file .env --rm "$NAME" python main.py
else
  docker run -v "$HOST_DATA_VOL":/opt/"$NAME"/data -v "$WEEKLY_INPUT_DATA_VOL":/opt/"$NAME"/input \
    -v "$SSH_VOLUME":/home/"$NAME"/.ssh --log-driver=syslog --log-opt syslog-address="$LOG" --log-opt tag="$NAME" \
    --env-file .env --rm "$NAME" python main.py
fi
