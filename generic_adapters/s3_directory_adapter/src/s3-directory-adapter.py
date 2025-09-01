# SPDX-License-Identifier: Apache-2.0
# © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
# and is legally attributed to the Department for Business and Trade (UK) as the governing entity.
 
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from botocore.exceptions import ClientError

from ia_map_lib.sinks import KafkaSink
from ia_map_lib import AutomaticAdapter, Record, RecordUtils
from ia_map_lib.config import Configurator
from ia_map_lib.logging import LoggerFactory

from logging import StreamHandler
import boto3
from json import dumps
import io 
import csv
from typing import Iterable
from dotenv import load_dotenv
from utils.label_mapper import string_to_label

# Mapper Configuration
load_dotenv()
config = Configurator()
BROKER = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
SASL_USERNAME = config.get("SASL_USERNAME", required=False,
                    description="The username for the SASL authentication.")
SASL_PASSWORD = config.get("SASL_PASSWORD", required=False,
                    description="The password for the SASL authentication.")
TARGET_TOPIC = config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
PRODUCER_NAME = config.get("PRODUCER_NAME", required=True, 
                    description="Specifies the name of the producer")
SOURCE_NAME = config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")
S3_BUCKET = config.get("S3_BUCKET", required=True, 
                    description="Specifies the S3 bucket that the data should be fetched from")
S3_BUCKET_EXPECTED_OWNER = config.get("S3_BUCKET", required=True, 
                    description="Specifies the expected owner of the S3 bucket")
S3_DIRECTORY = config.get("S3_DIRECTORY", required=True, 
                    description="Specifies the S3 directory that holds the files")
PENDING_TAG = {"Key": "status", "Value": "pending"}
PROCESSED_TAG = {"Key": "status", "Value": "processed"}

DEFAULT_SECURITY_LABEL = config.get("DEFAULT_SECURITY_LABEL", required=True, 
                    description="Specifies the default security label for the data")


default_security_label = string_to_label(DEFAULT_SECURITY_LABEL)

kafka_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": "PLAINTEXT",
    "allow.auto.create.topics": True,
}

if (SASL_USERNAME and SASL_PASSWORD):
    kafka_config["security.protocol"] = "SASL_PLAINTEXT"
    kafka_config["sasl.mechanism"] = "PLAIN"
    kafka_config["sasl.username"] = SASL_USERNAME
    kafka_config["sasl.password"] = SASL_PASSWORD

logger = LoggerFactory.get_logger(__name__, kafka_config=kafka_config)
logger.logger.addHandler(StreamHandler())

s3 = boto3.client('s3')

def get_unprocessed_files():
    """List files in S3 that don't have pending/processed tags."""
    paginator = s3.get_paginator("list_objects_v2")
    new_files = []

    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_DIRECTORY):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):  # skip directories
                continue

            # Check object tags to see if already pending or processed
            try:
                tags = s3.get_object_tagging(Bucket=S3_BUCKET, Key=key, ExpectedBucketOwner=S3_BUCKET_EXPECTED_OWNER)
                tagset = {t["Key"]: t["Value"] for t in tags.get("TagSet", [])}
                if tagset.get("status") in ("pending", "processed"):
                    continue
            except ClientError as e:
                logger.warning(f"Could not get tags for {key}: {e}")

            new_files.append(key)

    return new_files


def claim_file(key):
    """Mark file as pending so no other job picks it up."""
    try:
        s3.put_object_tagging(
            Bucket=S3_BUCKET,
            Key=key,
            Tagging={"TagSet": [PENDING_TAG]},
            ExpectedBucketOwner=S3_BUCKET_EXPECTED_OWNER,
        )
        logger.info(f"Claimed file {key} as pending.")
        return True
    except ClientError as e:
        logger.error(f"Failed to claim {key}: {e}")
        return False


def get_next_file_key():
    files = get_unprocessed_files()

    if not files or len(files) == 0:
        logger.info("No new files found.")
        return
    else:
        return files[0] # only ever take the first file
    

def fetch_file(bucket, file_key):
    if claim_file(file_key):
        obj = s3.get_object(Bucket=bucket, Key=file_key, ExpectedBucketOwner=S3_BUCKET_EXPECTED_OWNER)
        stream = io.TextIOWrapper(obj['Body'], encoding='utf-8')
        return csv.DictReader(stream)


def mark_file_processed(file_key):
    """Tag the file as processed and optionally move it."""
    try:
        s3.put_object_tagging(
            Bucket=S3_BUCKET,
            Key=file_key,
            Tagging={"TagSet": [PROCESSED_TAG]},
            ExpectedBucketOwner=S3_BUCKET_EXPECTED_OWNER,
        )
    except ClientError as e:
        logger.error(f"Failed to mark {file_key} as processed: {e}")


def generate_records() -> Iterable[Record]:
    logger.info("Processing a file in... " + S3_DIRECTORY)
    file_key = get_next_file_key()
    if file_key:
        reader = fetch_file(S3_BUCKET, file_key)
        i = 0
        for row in reader:
            yield create_record(row, default_security_label)
            i += 1
            logger.info(f"Record {i} Uploaded")
        
        mark_file_processed(file_key)


def create_record(data, security_labels):
    record =  Record(
        RecordUtils.to_headers(
            {
                "Content-Type": "application/json",
                "Data-Source": SOURCE_NAME,
                "Data-Producer": PRODUCER_NAME,
                "Security-Label": security_labels,
            }
        ),
        None,
        dumps(data),
    )
    logger.debug(record)
    return record


sink = KafkaSink(TARGET_TOPIC, kafka_config=kafka_config, debug=True)
adapter = AutomaticAdapter(
    target=sink, 
    adapter_function=generate_records, 
    name=PRODUCER_NAME, 
    has_error_handler=False,
    has_reporter=False,
    has_data_catalog=False
)
logger.info("Adapter created")
adapter.run()
logger.info("Adapter finished")

