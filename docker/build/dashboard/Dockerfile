FROM python:3.9.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --compile --no-cache-dir
WORKDIR /workspace/
