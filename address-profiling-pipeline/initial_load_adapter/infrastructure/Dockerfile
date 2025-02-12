FROM python:3.12

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/address_profiling_2024-12-13_115731.csv .
COPY ../src/producer.py .

CMD ["python", "./producer.py"]