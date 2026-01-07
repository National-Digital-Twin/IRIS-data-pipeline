FROM python:3.12

# Create a non-root user and group
RUN groupadd -r passthroughuser && useradd -r -g passthroughuser passthroughuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/passthrough_mapper

USER passthroughuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "-m", "passthrough_mapper.passthrough"]
