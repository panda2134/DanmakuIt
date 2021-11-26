#!/bin/bash
if [ -f "/private_key/private.key" ]; then
    echo "use exist private key."
else
    echo "create key pair."
    python keys_create.py
fi
python app.py