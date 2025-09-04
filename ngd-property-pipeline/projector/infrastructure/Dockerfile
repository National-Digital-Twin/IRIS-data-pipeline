FROM python:3.13-slim

# Create a non-root user and group
RUN apt-get update && \
    apt-get --no-install-recommends install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r projectoruser && useradd -r -g projectoruser projectoruser

WORKDIR /app

COPY ../src/ngd_postgres_projector.py .
COPY infrastructure/docker-context/generic_projectors/ ./generic_projectors


COPY ../requirements.txt .
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install -e ./generic_projectors

USER projectoruser

CMD ["python", "./ngd_postgres_projector.py"]