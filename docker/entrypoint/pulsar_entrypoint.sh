#!/bin/bash

echo "-- Wait for public key and token to be ready"
until [[ -f "/public_key/public.key" && -f "/token/super_user" ]] ; do sleep 1; done
echo "-- Public key and token is ready -- Start Pulsar"
_term() { 
  echo "SIGTERM" 
  bin/pulsar-daemon stop standalone
  exit 0
}
trap _term SIGTERM

export PULSAR_EXTRA_OPTS=-Dlog4j2.formatMsgNoLookups=true
export BOOKIE_EXTRA_OPTS=-Dlog4j2.formatMsgNoLookups=true
bin/pulsar-daemon start standalone
bash functions_create.sh
until false; do sleep 1; done
