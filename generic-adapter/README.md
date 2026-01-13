# README

A generic adapter is a tool that allows a user to ingest records from a source and stream them
to a target Kafka topic. Currently the generic adapter has three modes of operation:

1. The first one is where the source is a file in CSV format without any integration with AWS S3 and where the source file is bundled with the image.
2. The second one is where the source is a file in CSV format with AWS S3 integration which expects the user to have either a local S3 service or a remote one with the correct permissions for access.
3. The third one is where the source is data already in a Kafka topic. This mode of operation ensures all data in a source Kafka topic is transferred to a target Kafka topic.

## Pre-requisites

- Bring up the required services like Kafka, Secure agent graph and minio using the command `make developer-resources-up MINIO_ROOT_USER=<your-minio-root-user> MINIO_ROOT_PASSWORD=<your-minio-root-password>` while in the main directory.
- If you want to run the local version of the adapter please ensure the source file is present in the infrastructure directory before building the image.

## Build the image

- While in this directory:
  - Run the command `docker build -t <image-tag> -f infrastructure/Dockerfile .` to build the image to bundle the image with the source file.
  - Run the command `docker build -t <image-tag> -f infrastructure/Dockerfile.s3 .` to build the image to use an s3 source.
  - Run the command `docker build -t <image-tag> -f infrastructure/Dockerfile.kafka .` to build the image for a Kafka topic source. You can also use the supplied Makefile to build and run the Kafka adapter.

## Running locally

- Run the image built in the previous step using the following command `docker run --rm -d [-e <env-vars>...| --env-file <path-to-your-env-file] <image-name> .`
- The environment variables required by this image are as follows
  - AWS_ACCESS_KEY_ID: This is your AWS access key id (required for local s3 run)
  - AWS_SECRET_ACCESS_KEY: This is your AWS secret access key (required for local s3 run)
  - AWS_REGION: The AWS region for your account and s3 resources (required for local s3 run)
  - S3_ENDPOINT: This is the endpoint where your s3 bucket is hosted (required for local s3 run)
  - S3_BUCKET_NAME: This is the s3 bucket where your source file is located
  - S3_FILENAME: This is the name of your source file (required for local s3 run)
  - FILENAME: This is the name of your source file (required for the local run)
  - BOOTSTRAP_SERVERS: This is a list of endpoints where to access your Kafka instance (required)
  - SASL_USERNAME: This is the SASL username for you Kafka instance (required)
  - SASL_PASSWORD: This is the SASL password for the user of your Kafka instance (required)
  - TARGET_TOPIC: This is the name of the topic in Kafka where the messages will be adapted (required)
  - SOURCE_NAME: The name of the source that is being adapted (required)
  - PRODUCER_NAME: The name of the adapter instance that is going to adapt the source file to the target topic (required)

You can run the Kafka-to-Kafka adapter broadly in two ways: to move data within the same Kafka cluster or between Kafka clusters. For the first, you need these variables defined as a minimum:
  - SOURCE_BOOTSTRAP_SERVERS
  - SOURCE_KAFKA_SECURITY_PROTOCOL (optional, defaults to "SASL_PLAINTEXT")
  - SOURCE_KAFKA_SASL_MECHANISM (optional, defaults to "PLAIN")
  - SOURCE_SASL_USERNAME
  - SOURCE_SASL_PASSWORD

If you'd like to move data between Kafka clusters, then you also need environment variables which allow the adapter to connect to that cluster:
  - TARGET_BOOTSTRAP_SERVERS
  - TARGET_KAFKA_SECURITY_PROTOCOL (optional, defaults to "SASL_PLAINTEXT")
  - TARGET_KAFKA_SASL_MECHANISM (optional, defaults to "PLAIN")
  - TARGET_SASL_USERNAME
  - TARGET_SASL_PASSWORD

Regardless of the above, you also need to tell the Kafka adapter what data you'd like to move and where (in terms of Kafka topics). You can do that by either mounting a topic_mappings.json file to the container or by passing in an TOPIC_MAPPINGS_JSON env variable at runtime. The JSON must be in this format:
`
  {
  "topic_mappings": [
    {"source_topic":"", "target_topic":""},
    {"source_topic":"", "target_topic":""}
  ]
}
`

If you'd like to run the Kafka adapter locally and need a second Kafka and ZooKeeper instance to test the movement of data between clusters, then you can do this easily by running `docker compose up -d` from the generic-adapter/infrastructure directory. Server details for the "kafka-b" instance are in generic-adapter/infrastructure/kafka-b/server.properties file.

### EXAMPLE using Kafka adapter within same cluster

To use the adapter within the same cluster, set SOURCE_ variables only in your .env as so:
`
SOURCE_BOOTSTRAP_SERVERS=172.30.95.127:9092
SOURCE_SASL_USERNAME=user1
SOURCE_SASL_PASSWORD=root
`

In this example, this is the topic mappings JSON we will use (stored locally in config/topic_mappings-single-cluster.json):
`
{
  "topic_mappings": [
    {"source_topic":"address-profiling-test-2026-01-06-154543-epc-assessment-mapped", "target_topic":"knowledge2-geo-test"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-floor-mapped", "target_topic":"knowledge2-geo-test"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-heating-mapped", "target_topic":"heating-v2"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-roof-mapped", "target_topic":"knowledge2-geo-test"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-structure-unit-mapped", "target_topic":"knowledge2-geo-test"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-wall-mapped", "target_topic":"knowledge2-geo-test"},
    {"source_topic":"address-profiling-test-2026-01-06-154543-window-mapped", "target_topic":"knowledge2-geo-test"}
  ]
}
`

We can now build the image using
`
make docker-build-kafka-adapter IMAGE_TAG="kafka-adapter:latest"
`

This creates an image called kafka-adapter:latest. We can then run the image as a container with:

`
make docker-run-kafka-adapter TOPIC_MAPPINGS_FILENAME="topic_mappings-single-cluster.json" IMAGE_TAG=kafka-adapter:latest
`

This will trigger the movement of data from the source topics to the target topics defined in the JSON and within the same Kafka cluster as defined in the .env file.

