FROM python:3.12

# Create a non-root user and group
RUN groupadd -r adapteruser && useradd -r -g adapteruser adapteruser

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../src/ndt_retrofit_buildings_extensions.ttl .
COPY ../src/retrofit_ontology_producer.py .

USER adapteruser

CMD ["python", "./retrofit_ontology_producer.py"]