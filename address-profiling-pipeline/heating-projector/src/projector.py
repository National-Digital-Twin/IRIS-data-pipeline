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

from dotenv import load_dotenv
from projection_function import project_func
from telicent_lib.config import Configurator
from telicent_lib.records import Record

from custom_projectors.batched_one_off_projector import BatchedOneOffProjector

load_dotenv()
config = Configurator()

BOOTSTRAP_SERVERS = config.get(
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
    description="The group id for the topic to consume",
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

SAG_ENDPOINT = config.get(
    "SAG_ENDPOINT",
    required=True,
    description="The SAG endpoint to send the data through",
)

SAG_UPDATE_FREQUENCY = config.get(
    "SAG_UPDATE_FREQUENCY",
    required=False,
    description="The frequency with which to make calls to the update endpoint of the SAG",
    default=5000,
    converter=int,
    required_type=int,
)

HEATING_GRAPH_URI = config.get(
    "HEATING_GRAPH_URI",
    required=True,
    description="The URI of the named graph where the heating data must be projected",
)

kafka_consumer_config = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "group.id": [SOURCE_TOPIC_GROUP_ID],
}

kafka_producer_config = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": KAFKA_SECURITY_PROTOCOL,
    "sasl.mechanism": KAFKA_SASL_MECHANISM,
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}


def unwrap_and_project(records: [Record]) -> None:
    project_func(SAG_ENDPOINT, HEATING_GRAPH_URI, [record.value for record in records])


projector = BatchedOneOffProjector(
    SOURCE_TOPIC,
    kafka_consumer_config,
    kafka_producer_config,
    SAG_UPDATE_FREQUENCY,
    unwrap_and_project,
)

projector.run()
