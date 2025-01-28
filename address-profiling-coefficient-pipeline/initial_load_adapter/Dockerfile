FROM python:3.12

ARG FILENAME

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ${FILENAME} .
COPY ./producer.py .

CMD ["python", "./producer.py"]