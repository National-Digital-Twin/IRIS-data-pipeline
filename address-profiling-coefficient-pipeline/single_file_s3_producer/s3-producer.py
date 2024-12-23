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

from maplib.sinks import KafkaSink
from maplib import AutomaticAdapter, Record, RecordUtils
from maplib.config import Configurator
from maplib.logging import CoreLoggerFactory
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
broker = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
target_topic = config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
name = config.get("PRODUCER_NAME", required=True, 
                    description="Specifies the name of the producer")
source_name = config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")
bucket = config.get("S3_BUCKET", required=True, 
                    description="Specifies the source that the data has originated from")
filename = config.get("S3_FILENAME", required=True, 
                    description="Specifies the source that the data has originated from")

dsl = config.get("DEFAULT_SECURITY_LABEL", required=True, 
                    description="Specifies the source that the data has originated from")

default_security_label = string_to_label(dsl)

logger = CoreLoggerFactory.get_logger(__name__, broker=broker)
logger.logger.addHandler(StreamHandler())

s3 = boto3.client('s3')

def fetch_file(bucket, file):
    obj = s3.get_object(Bucket=bucket, Key=file)
    text_content = obj['Body'].read().decode('utf-8')
    file_received = io.StringIO(text_content)
    reader = csv.DictReader(file_received)
    return reader

def generate_records() -> Iterable[Record]:
    logger.info("Processing... " + filename)
    reader = fetch_file(bucket, filename)
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
                "Data-Source": source_name,
                "Data-Producer": name,
                "Security-Label": security_labels,
            }
        ),
        None,
        dumps(data),
    )
    logger.debug(record)
    return record

logger.info("Fetching bucket")


sink = KafkaSink(target_topic, broker)
adapter = AutomaticAdapter(
    target=sink, 
    adapter_function=generate_records, 
    name=name, 
    source_name=source_name
)
logger.info("Adapter created")
adapter.run()
logger.info("Adapter finished")

