#!/bin/bash

pip install ./dashboard -i https://pypi.tuna.tsinghua.edu.cn/simple --compile --no-cache-dir

_term() { 
  echo "SIGTERM"
  kill -15 %1
  kill -15 %2
  exit 0
}
trap _term SIGTERM
/entrypoint/wait_`uname -m`
if [[ $? -ne 0 ]]; then
	exit 1
fi
echo "Redis is up!"
arq dashboard.worker.WorkerSettings &
python dashboard/main.py &
wait
