#!/bin/sh
set -xeu

# If "-e uid={custom/local user id}" flag is not set for "docker run" command, use 9999 as default
CURR_UID=${CURRENT_UID:-9999}

# Notify user about the UID selected
echo "Current UID : $CURR_UID"

# Create user  with selected UID
useradd --shell /bin/bash -u "$CURR_UID" -o -c "" -m "$NAME"

# Set "HOME" ENV variable for user's home directory
export HOME=/home/"$NAME"

chown -R "$NAME": /opt/"$NAME"/data

# Execute process
exec /usr/local/bin/gosu "$NAME" "$@"
