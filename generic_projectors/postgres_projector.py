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

from abc import ABC, abstractmethod
from ia_map_lib.sources import KafkaSource
from ia_map_lib.config import Configurator
from ia_map_lib.logging import LoggerFactory
from ia_map_lib import Projector, Record, RecordUtils
from typing import Union, List
import logging
from json import loads
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


load_dotenv()
config = Configurator()
BROKER = config.get(
    "BOOTSTRAP_SERVERS",
    required=True,
    description="Specifies the Kafka Bootstrap Servers to connect to.",
)
SASL_USERNAME = config.get(
    "SASL_USERNAME", required=False,
    description="The username for the SASL authentication."
)
SASL_PASSWORD = config.get(
    "SASL_PASSWORD", required=False,
    description="The password for the SASL authentication."
)
SOURCE_TOPIC = config.get(
    "SOURCE_TOPIC",
    required=True,
    description="Specifies the Kafka topic the projector ingests from.",
)
SOURCE_TOPIC_GROUP_ID = config.get(
    "SOURCE_TOPIC_GROUP_ID",
    required=True,
    description="Specifies the Kafka topic group id the projector ingests from.",
)
DEBUG = config.get(
    "DEBUG", required=False, default=False, converter=bool, required_type=bool
)

class GenericPostgresProjector(ABC):
    kafka_config = {
        "bootstrap.servers": BROKER,
        "security.protocol": "PLAINTEXT",
        "allow.auto.create.topics": True,
        "group.id": [SOURCE_TOPIC_GROUP_ID],
    }
    
    if (SASL_USERNAME and SASL_PASSWORD):
        kafka_config["security.protocol"] = "SASL_PLAINTEXT"
        kafka_config["sasl.mechanism"] = "PLAIN"
        kafka_config["sasl.username"] = SASL_USERNAME
        kafka_config["sasl.password"] = SASL_PASSWORD

    logger = LoggerFactory.get_logger(
        "{source}-to-database-projector".format(source=SOURCE_TOPIC),
        kafka_config,
        level = logging.DEBUG,
        topic="logging",
    )
    
    
    def __init__(self, db_url=None):
        self.db_url = db_url
        self.SessionLocal = None
        if db_url:
            self.engine = create_engine(db_url, echo=False, future=True)


    def execute_sql(self, query, params=None):
        """Utility for executing raw SQL (Core style)"""
        if not self.engine:
            raise RuntimeError("Database not configured for this job")
        with self.engine.begin() as conn:
            return conn.execute(text(query), params or {})


    def handle_record_mapping(self, record: Record) -> Union[Record, List[Record], None]:
        self.logger.debug("Beginning processing of record")
        data = loads(record.value)

        mapped = self.project_record(data)
        self.logger.debug("Record has completed processing")
        return RecordUtils.add_header(
            Record(record.headers, record.key, mapped, None),
            "Content-Type",
            "text/turtle",
        )
        
    
    @abstractmethod
    def project_record(self, record: any):
        """Projector-specific logic"""
        pass


    def run_projector(self):
        source = KafkaSource(
            topic=SOURCE_TOPIC, kafka_config=self.kafka_config
        )
        mapper = Projector(
            source,
            self.handle_record_mapping,
            target_store="postgres",
            name=SOURCE_TOPIC + " to database projector",
            has_reporter=False,
            reporting_batch_size=500,
            has_error_handler=False
        )
        self.logger.info("Projector instantiated")
        mapper.run()
