FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./uprn-lat-long.csv .
COPY ./producer.py .

CMD ["python", "./producer.py"]