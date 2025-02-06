FROM python:3.12

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/label_mapper.py .
COPY ../src/s3-producer.py .

CMD ["python", "./s3-producer.py"]