# SPDX-License-Identifier: Apache-2.0

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

# This file is unmodified from its original version developed by Telicent Ltd.,
# and is now included as part of a repository maintained by the National Digital Twin Programme.
# All support, maintenance and further development of this code is now the responsibility
# of the National Digital Twin Programme.

from telicent_lib.sinks import KafkaSink

from telicent_lib import Record, RecordUtils, AutomaticAdapter
from telicent_lib.config import Configurator

from telicent_lib.access import SecurityLabelBuilder, EDHSecurityLabelsV2
from json import dumps
from typing import Iterable
import csv
from dotenv import load_dotenv


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
SOURCE_NAME=config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")
FILENAME=config.get("FILENAME", required=True,
                    description="The path along with the filename of the csv file to stream data from.")


# Define our adapter function, this is just a Python generator function that 
# generates the Record instance to be written out to the DataSink

kafka_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanism": "PLAIN",
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}


permitted_nationalities=['GBR', 'NZL']
default_security_label = SecurityLabelBuilder().add_multiple(EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.value, *permitted_nationalities).build()


def create_record(data, security_labels):
    return Record(RecordUtils.to_headers({ 
        "Content-Type": "application/json",
        "Data-Source": SOURCE_NAME, 
        "Data-Producer": PRODUCER_NAME, 
        "Security-Label": security_labels
    }), None, dumps(data))

def generate_records() -> Iterable[Record]:
    with open(FILENAME, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            yield create_record(row, default_security_label)

# Create a sink and the adapter
sink = KafkaSink(TARGET_TOPIC, kafka_config=kafka_config)
adapter = AutomaticAdapter(target=sink, adapter_function=generate_records, 
                           name=PRODUCER_NAME, source_name=SOURCE_NAME, has_reporter=False, has_error_handler=False)

# Call run() to run the action
adapter.run()
