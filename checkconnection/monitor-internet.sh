#!/bin/bash

# URL per comprovar la connexió
CHECK_URL="http://www.google.com"
MAX_RETRIES=5
RETRY_DELAY=60
CHECK_DELAY=900

# Funció per comprovar la connexió
check_internet() {
  curl -s --head $CHECK_URL | head -n 1 | grep "200 OK" > /dev/null
  return $?
}

# Monitoritzar la connexió
while true; do
  retries=0
  while ! check_internet; do
    retries=$((retries + 1))
    echo "No hi ha connexió. Intent $retries/$MAX_RETRIES."
    if [ $retries -ge $MAX_RETRIES ]; then
      echo "Connexió perduda. Reiniciant el dispositiu..."
      /sbin/reboot
    fi
    sleep $RETRY_DELAY
  done
  echo "Connexió OK."
  sleep $CHECK_DELAY
done
