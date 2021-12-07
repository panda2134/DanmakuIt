#!/bin/bash

pip install ./dashboard -i https://pypi.tuna.tsinghua.edu.cn/simple --compile --no-cache-dir

set -m

_term() { 
  echo "SIGTERM"
  killall python
  exit 0
}
trap _term SIGTERM

arq dashboard.worker.WorkerSettings &
python dashboard/main.py
wait