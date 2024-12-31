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

from telicent_lib.sinks import KafkaSink
from telicent_lib import AutomaticAdapter, Record, RecordUtils
from telicent_lib.config import Configurator
from telicent_lib.logging import CoreLoggerFactory
from logging import StreamHandler
import boto3
from json import dumps
import io 
import csv
from typing import Iterable
from dotenv import load_dotenv
from label_mapper import string_to_label

# Mapper Configuration
load_dotenv()
config = Configurator()
BROKER = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
SASL_USERNAME = config.get("SASL_USERNAME", required=True,
                    description="The username for the SASL authentication.")
SASL_PASSWORD = config.get("SASL_PASSWORD", required=True,
                    description="The password for the SASL authentication.")
TARGET_TOPIC = config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
PRODUCER_NAME = config.get("PRODUCER_NAME", required=True, 
                    description="Specifies the name of the producer")
SOURCE_NAME = config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")
S3_BUCKET = config.get("S3_BUCKET", required=True, 
                    description="Specifies the source that the data has originated from")
S3_FILENAME = config.get("S3_FILENAME", required=True, 
                    description="Specifies the source that the data has originated from")

DEFAULT_SUECRITY_LABEL = config.get("DEFAULT_SECURITY_LABEL", required=True, 
                    description="Specifies the source that the data has originated from")

default_security_label = string_to_label(DEFAULT_SUECRITY_LABEL)

kafka_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanisms": "SCRAM-SHA-256",
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
}

logger = CoreLoggerFactory.get_logger(__name__, kafka_config=kafka_config)
logger.logger.addHandler(StreamHandler())

s3 = boto3.client('s3')

def fetch_file(bucket, file):
    obj = s3.get_object(Bucket=bucket, Key=file)
    text_content = obj['Body'].read().decode('utf-8')
    file_received = io.StringIO(text_content)
    reader = csv.DictReader(file_received)
    return reader

def generate_records() -> Iterable[Record]:
    logger.info("Processing... " + S3_FILENAME)
    reader = fetch_file(S3_BUCKET, S3_FILENAME)
    i = 0
    for row in reader:
       
        yield create_record(row, default_security_label)
        i += 1
        logger.info(f"Record {i} Uploaded")

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

logger.info("Fetching bucket")


sink = KafkaSink(TARGET_TOPIC, kafka_config=kafka_config)
adapter = AutomaticAdapter(
    target=sink, 
    adapter_function=generate_records, 
    name=PRODUCER_NAME, 
    source_name=SOURCE_NAME
)
logger.info("Adapter created")
adapter.run()
logger.info("Adapter finished")

