FROM python:3.13-slim

# Install git and cleanup to reduce image size
RUN apt-get update && \
    apt-get --no-install-recommends install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r adapteruser && useradd -r -g adapteruser adapteruser

WORKDIR /app

COPY ../requirements.txt .

RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY ../../utils .
COPY ../src/s3-directory-adapter.py .

USER adapteruser

CMD ["python", "./s3-directory-adapter.py"]