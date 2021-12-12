#!/bin/bash

echo "-- Wait for Pulsar service to be ready"
until curl http://localhost:8080/metrics > /dev/null 2>&1 ; do sleep 1; done
echo "-- Pulsar service is ready -- Create functions"
sleep 10
bin/pulsar-admin functions delete \
  --tenant public \
  --namespace default \
  --name tagger

bin/pulsar-admin functions create \
  --py ./tagger.py \
  --classname tagger.TaggingFunction \
  --tenant public \
  --namespace default \
  --name tagger \
  --custom-serde-inputs '{"raw":"tagger.BytesIdentity","state":"tagger.BytesIdentity"}'