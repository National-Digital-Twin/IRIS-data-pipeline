FROM python:3.13-slim

RUN apt-get update && \
    apt-get --no-install-recommends install -y git build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r mapperuser && useradd -r -g mapperuser mapperuser

WORKDIR /app

COPY ../src/ngd_kafka_mapper.py .
COPY infrastructure/docker-context/generic_mappers/ ./generic_mappers

COPY ../requirements.txt .

RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    pip install -e ./generic_mappers

USER mapperuser

CMD ["python", "./ngd_kafka_mapper.py"]