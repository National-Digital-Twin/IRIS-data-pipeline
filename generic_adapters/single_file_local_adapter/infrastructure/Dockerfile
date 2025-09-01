FROM python:3.12

ARG SOURCE_FILE
# Create a non-root user and group
RUN groupadd -r adapteruser && useradd -r -g adapteruser adapteruser

WORKDIR /app

COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN --mount=type=secret,id=pat_token \
    export GITHUB_ACCESS_TOKEN=$(cat /run/secrets/pat_token) && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY ${SOURCE_FILE} .
COPY src/producer.py .

USER adapteruser

CMD ["python", "./producer.py"]
