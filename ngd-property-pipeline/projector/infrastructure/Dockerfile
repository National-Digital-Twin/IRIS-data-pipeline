FROM python:3.13-slim

# Create a non-root user and group
RUN groupadd -r projectoruser && useradd -r -g projectoruser mapperuser

WORKDIR /app

COPY ../src/ngd_postgres_projector.py .
COPY ../../../generic_projectors .

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e /generic_projectors

USER projectoruser

CMD ["python", "./ngd_postgres_projector.py"]