# Extracted from: https://github.com/ibm-functions/runtime-python/tree/master/python3

FROM python:3.6-slim-jessie

ENV FLASK_PROXY_PORT 8080

RUN apt-get update && apt-get install -y \
        gcc \
        libc-dev \
        libxslt-dev \
        libxml2-dev \
        libffi-dev \
        libssl-dev \
        zip \
        unzip \
        vim \
        && rm -rf /var/lib/apt/lists/*

RUN apt-cache search linux-headers-generic

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip setuptools six && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /actionProxy
ADD https://raw.githubusercontent.com/apache/incubator-openwhisk-runtime-docker/dockerskeleton%401.0.0/core/actionProxy/actionproxy.py /actionProxy/actionproxy.py

RUN mkdir -p /pythonAction
ADD https://raw.githubusercontent.com/apache/incubator-openwhisk-runtime-python/3%401.0.0/core/pythonAction/pythonrunner.py /pythonAction/pythonrunner.py

CMD ["/bin/bash", "-c", "cd /pythonAction && python -u pythonrunner.py"]