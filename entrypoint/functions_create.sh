#!/bin/bash
sleep 30
bin/pulsar-admin functions create \
  --py ./tagger.py \
  --classname tagger.TaggingFunction \
  --tenant public \
  --namespace default \
  --name tagger \
  --custom-serde-inputs '{"raw":"tagger.BytesIdentity","state":"tagger.BytesIdentity"}'