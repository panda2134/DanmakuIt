#!/bin/bash
if [ -f "/private_key/private.key" ]; then
    echo "use exist private key."
else
    echo "create key pair."
    python keys_create.py
fi
gunicorn -b 0.0.0.0:8000 -w 2 -k aiohttp.GunicornUVLoopWebWorker app:app