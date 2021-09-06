#!/bin/sh

#Change the NAME variable with the name of your script
NAME=$(basename $(pwd))
LOG=${LOG:-udp://localhost}
HOST_DATA_VOL=${PM25_DATA_VOL:-}

docker build -t $NAME --build-arg NAME=$NAME .

if [ -z "$HOST_DATA_VOL" ]; then
  echo "Running container without host mounted volume. Data will not be persisted"
  docker run --log-driver=syslog --log-opt syslog-address=$LOG --log-opt tag=$NAME --env-file .env --rm $NAME python main.py
else
  docker run -v $HOST_DATA_VOL:/opt/$NAME/data -v $HOST_DATA_VOL:/opt/$NAME/data --log-driver=syslog --log-opt syslog-address=$LOG --log-opt tag=$NAME --env-file .env --rm $NAME python main.py
fi
