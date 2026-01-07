# Passthrough Mapper

A lightweight Kafka bridge that merges multiple source topics into target topics
within the same cluster. It is designed for deployment-time runs (batch), not
as a long-running service.

## What it does
- Consumes from a list of source topics (one group id per domain).
- Produces into target topics (many-to-one supported).
- Preserves provenance via `source_topic` header and a safe key rewrite.
- Ensures idempotency with respect to group offsets (idempotent per stable group ID).

## Config
Required Environment variables:
- `BOOTSTRAP_SERVERS` (e.g. `172.30.95.127:9092`)
- `SASL_USERNAME`, `SASL_PASSWORD`
- `KAFKA_SECURITY_PROTOCOL` (default `SASL_PLAINTEXT`)
- `KAFKA_SASL_MECHANISM` (default `PLAIN`)
- `AUTO_OFFSET_RESET` (default `earliest`)
- `IDLE_TIMEOUT_SECONDS` (default `0`)
- `TOPIC_MAPPINGS_FILEPATH` (path to JSON file inside container)
- `TOPIC_MAPPINGS_JSON` (optional, takes precedence over file)

## Topic mappings format
```json
{
  "topic_mappings": [
    {
      "source": "address-profiling-...-floor-mapped",
      "source_topic_group_id": "address-profiling-floor-mapped",
      "target": "knowledge2-geo-test"
    }
  ]
}
```

## Running with Docker
`docker build -t passthrough-mapper:latest -f infrastructure/Dockerfile .`
`docker run --env-file .env passthrough-mapper:latest`

## Airflow usage
Pass JSON via the Trigger DAG UI (Config field) and inject into the container:
`env = {"TOPIC_MAPPINGS_JSON": "{{ dag_run.conf | tojson }}"}`
`