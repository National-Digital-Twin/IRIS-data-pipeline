# SPDX-License-Identifier: Apache-2.0
# Originally developed by Telicent Ltd.; subsequently adapted, enhanced, and maintained by the National Digital Twin Programme.

#
# Copyright (C) Telicent Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#  Modifications made by the National Digital Twin Programme (NDTP)
#  © Crown Copyright 2025. This work has been developed by the National Digital Twin Programme
#  and is legally attributed to the Department for Business and Trade (UK) as the governing entity.

import csv
from json import dumps
from typing import Iterable

import boto3
from dotenv import load_dotenv
from telicent_lib import AutomaticAdapter, Record, RecordUtils
from telicent_lib.access import EDHSecurityLabelsV2, SecurityLabelBuilder
from telicent_lib.config import Configurator
from telicent_lib.sinks import KafkaSink

load_dotenv()
config = Configurator()
BROKER = config.get(
    "BOOTSTRAP_SERVERS",
    required=True,
    description="Specifies the Kafka Bootstrap Servers to connect to.",
)
KAFKA_SECURITY_PROTOCOL = config.get(
    "KAFKA_SECURITY_PROTOCOL",
    required=False,
    default="SASL_PLAINTEXT",
)
KAFKA_SASL_MECHANISM = config.get(
    "KAFKA_SASL_MECHANISM",
    required=False,
    default="PLAIN",
)
SASL_USERNAME = config.get(
    "SASL_USERNAME",
    required=True,
    description="The username for the SASL authentication.",
)
SASL_PASSWORD = config.get(
    "SASL_PASSWORD",
    required=True,
    description="The password for the SASL authentication.",
)
TARGET_TOPIC = config.get(
    "TARGET_TOPIC",
    required=True,
    description="Specifies the Kafka topic the mapper pushes its output to",
)
PRODUCER_NAME = config.get(
    "PRODUCER_NAME", required=True, description="Specifies the name of the producer"
)
SOURCE_NAME = config.get(
    "SOURCE_NAME",
    required=True,
    description="Specifies the source that the data has originated from",
)
AWS_REGION = config.get(
    "AWS_REGION", required=True, description="The region where the s3 bucket exists"
)
S3_ENDPOINT = config.get(
    "S3_ENDPOINT",
    required=False,
    description="The s3 endpoint for local development and testing.",
)
S3_BUCKET_NAME = config.get(
    "S3_BUCKET_NAME",
    required=False,
    description="The s3 bucket where the object to adapt exists.",
)
S3_FILENAME = config.get(
    "S3_FILENAME",
    required=True,
    description="The object key of the file to adapt to kafka.",
)
AWS_ACCESS_KEY_ID = config.get(
    "AWS_ACCESS_KEY_ID",
    required=False,
    description="The aws access key id for local development and testing.",
)
AWS_SECRET_ACCESS_KEY = config.get(
    "AWS_SECRET_ACCESS_KEY",
    required=False,
    description="The aws secret access key for local development and testing.",
)

FIELD_SIZE_LIMIT = 1000000

permitted_nationalities = ["GBR", "NZL"]
default_security_label = (
    SecurityLabelBuilder()
    .add_multiple(
        EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.value, *permitted_nationalities
    )
    .build()
)

# Define our adapter function, this is just a Python generator function that
# generates the Record instance to be written out to the DataSink

kafka_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}

csv.field_size_limit(FIELD_SIZE_LIMIT)


def create_record(data, security_labels):
    return Record(
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


def generate_records() -> Iterable[Record]:
    if S3_ENDPOINT and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    else:
        s3_client = boto3.client("s3", region_name=AWS_REGION)
    obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILENAME)
    obj_body = obj["Body"].read().decode("utf-8").splitlines()
    rows = csv.DictReader(obj_body)

    for row in rows:
        yield create_record(row, default_security_label)


# Create a sink and the adapter
sink = KafkaSink(TARGET_TOPIC, kafka_config=kafka_config)

adapter = AutomaticAdapter(
    target=sink,
    adapter_function=generate_records,
    name=PRODUCER_NAME,
    source_name=SOURCE_NAME,
    has_reporter=False,
    has_error_handler=False,
)

# Call run() to run the action
adapter.run()
