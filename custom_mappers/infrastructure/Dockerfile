FROM python:3.12

# Create a non-root user and group
RUN groupadd -r bridgeuser && useradd -r -g bridgeuser bridgeuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/custom_mappers

USER bridgeuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "-m", "custom_mappers.bridge"]
