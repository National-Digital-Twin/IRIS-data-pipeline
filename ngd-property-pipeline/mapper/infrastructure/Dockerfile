FROM python:3.12

RUN apt-get update && \
    apt-get --no-install-recommends install -y git build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r mapperuser && useradd -r -g mapperuser mapperuser

WORKDIR /app

COPY src/mapper.py .
COPY src/mapping_function.py .
COPY custom_mappers ./custom_mappers

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER mapperuser

CMD ["python", "mapper.py"]
