FROM python:3.12

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/ndt_retrofit_buildings_extensions.ttl .
COPY ../src/retrofit_ontology_producer.py .

CMD ["python", "./retrofit_ontology_producer.py"]