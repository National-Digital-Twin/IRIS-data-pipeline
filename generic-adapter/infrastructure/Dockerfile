FROM python:3.12

ARG SOURCE_FILE
# Create a non-root user and group
RUN groupadd -r adapteruser && useradd -r -g adapteruser adapteruser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ${SOURCE_FILE} .
COPY src/s3_producer.py .

USER adapteruser

CMD ["python", "./s3_producer.py"]
