#!/bin/bash
echo "-- Wait for public key and token to be ready"
until [[ -f "/public_key/public.key" && -f "/token/super_user" ]] ; do sleep 1; done
echo "-- Public key and token is ready -- Start Pulsar"
bash functions_create.sh &
bin/pulsar standalone