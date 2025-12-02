# README

A generic adapter is a tool that allows a user to ingest records from a source file in CSV format and stream them
to a target Kafka topic. Currently the generic adapter has two modes of operation, one is without any integration with AWS S3 using the source file bundled with the image. The other is with AWS S3 integration which expects the user to have either a local S3 service or a remote one with the correct permissions for access.

## Pre-requisites

- Bring up the required services like Kafka, Secure agent graph and minio using the command `make developer-resources-up MINIO_ROOT_USER=<your-minio-root-user> MINIO_ROOT_PASSWORD=<your-minio-root-password>` while in the main directory.
- If you want to run the local version of the adapter please ensure the source file is present in the infrastructure directory before building the image.

## Build the image

- While in this directory:
  - Run the command `docker build -t <image-tag> -f infrastructure/Dockerfile .` to build the image for a local run. This will bundle the image with the source file.
  - Run the command `docker build -t <image-tag> -f infrastructure/Dockerfile.s3 .` to build the image for a local run but with an s3 source

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
