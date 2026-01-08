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

import logging
from json import loads
from typing import List, Union

from dotenv import load_dotenv
from mapping_function import map_func
from telicent_lib import Record, RecordUtils
from telicent_lib.config import Configurator

from custom_mappers.one_off_mapper import OneOffMapper

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
SOURCE_TOPIC = config.get(
    "SOURCE_TOPIC",
    required=True,
    description="Specifies the Kafka topic the mapper ingests from.",
)
SOURCE_TOPIC_GROUP_ID = config.get(
    "SOURCE_TOPIC_GROUP_ID",
    required=True,
    description="Specifies the Kafka topic group id the mapper ingests from.",
)
TARGET_TOPIC = config.get(
    "TARGET_TOPIC",
    required=True,
    description="Specifies the Kafka topic the mapper pushes its output to",
)
DEBUG = config.get(
    "DEBUG", required=False, default=False, converter=bool, required_type=bool
)
LOG_LEVEL = config.get(
    "LOG_LEVEL",
    required=False,
    description="Logging level for the mapper",
    default="INFO",
)

kafka_consumer_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "group.id": [SOURCE_TOPIC_GROUP_ID],
}

kafka_producer_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}

# set log level for external libraries
logging.getLogger("ies_tool.ies_tool").setLevel(LOG_LEVEL)
logging.getLogger("telicent_lib").setLevel(LOG_LEVEL)
logging.getLogger("telicent_lib.config").setLevel(LOG_LEVEL)


# Function each record on the source topic is passed to.
def unwrap_and_map(record: Record) -> Union[Record, List[Record], None]:
    data = loads(record.value)

    mapped = map_func(data)
    if mapped is None:
        return mapped
    return RecordUtils.add_header(
        Record(record.headers, record.key, mapped, None),
        "Content-Type",
        "text/turtle",
    )


mapper = OneOffMapper(
    BROKER,
    SASL_USERNAME,
    SASL_PASSWORD,
    SOURCE_TOPIC,
    TARGET_TOPIC,
    kafka_consumer_config,
    kafka_producer_config,
    unwrap_and_map,
)

mapper.run()
