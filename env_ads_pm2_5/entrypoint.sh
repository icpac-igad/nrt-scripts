#!/bin/bash
set -e

# If "-e uid={custom/local user id}" flag is not set for "docker run" command, use 9999 as default
CURRENT_UID=${CURRENT_UID:-9999}

# Notify user about the UID selected
echo "Current UID : $CURRENT_UID"

# Create user  with selected UID
useradd --shell /bin/bash -u "$CURRENT_UID" -o -c "" -m "$NAME"

# Set "HOME" ENV variable for user's home directory
export HOME=/home/"$NAME"

chown -R "$NAME": /opt/"$NAME"/data

# Execute process
exec /usr/local/bin/gosu "$NAME" "$@"
