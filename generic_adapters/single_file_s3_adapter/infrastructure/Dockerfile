FROM python:3.12

# Create a non-root user and group
RUN groupadd -r adapteruser && useradd -r -g adapteruser adapteruser

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/label_mapper.py .
COPY ../src/s3-producer.py .

USER adapteruser

CMD ["python", "./s3-producer.py"]