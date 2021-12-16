#!/bin/bash

if [ -f "/private_key/private.key" ]; then
    echo "use exist private key."
else
    echo "create key pair."
    python keys_create.py
fi
/entrypoint/wait_`uname -m`
if [[ $? -ne 0 ]];
	exit 1
fi
echo "Redis is up!"
exec python app.py
