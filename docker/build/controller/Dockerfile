FROM apachepulsar/pulsar:2.8.1
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --compile --no-cache-dir
WORKDIR /workspace/
