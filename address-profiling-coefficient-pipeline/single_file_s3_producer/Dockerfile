FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./label_mapper.py .
COPY ./s3-producer.py .

CMD ["python", "./s3-producer.py"]