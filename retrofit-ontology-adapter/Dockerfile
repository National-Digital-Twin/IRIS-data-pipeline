FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ndt_retrofit_buildings_extensions.ttl .
COPY ./retrofit_ontology_producer.py .

CMD ["python", "./retrofit_ontology_producer.py"]