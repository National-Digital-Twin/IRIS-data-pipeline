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
from telicent_lib.sources import KafkaSource
from telicent_lib.config import Configurator
from telicent_lib.logging import CoreLoggerFactory
from telicent_lib import Mapper, Record, RecordUtils
from typing import Union, List
from json import loads
from mapping_function import map_func
from dotenv import load_dotenv

# run adapter.py, then mapper.py, then mapper-2.py and finally, this file

# Mapper Configuration
load_dotenv()
config = Configurator()
BROKER = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
SASL_USERNAME = config.get("SASL_USERNAME", required=True,
                    description="The username for the SASL authentication.")
SASL_PASSWORD = config.get("SASL_PASSWORD", required=True,
                    description="The password for the SASL authentication.")
SOURCE_TOPIC = config.get("SOURCE_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper ingests from.")
TARGET_TOPIC = config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
SOURCE_TOPIC_GROUP_ID = config.get("SOURCE_TOPIC_GROUP_ID", required=False,
                    description="The group id for the topic to consume", default=0)
DEBUG = config.get("DEBUG", required=False, default=False, converter=bool, required_type=bool)

kafka_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "group.id": [SOURCE_TOPIC_GROUP_ID],
}

kafka_producer_config = {
    "bootstrap.servers": BROKER,
    "security.protocol": "SASL_PLAINTEXT",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": SASL_USERNAME,
    "sasl.password": SASL_PASSWORD,
    "allow.auto.create.topics": True,
}

logger = CoreLoggerFactory.get_logger(
    "{source}-to-{target}-mapper".format(source=SOURCE_TOPIC, target=TARGET_TOPIC),
    kafka_config=kafka_producer_config,
    topic="logging",
)
# Function each record on the source topic is passed to.
def mapping_function(record: Record) ->  Union[Record, List[Record], None]:

    # Add mapping logic here
    # Try to keep it small and performant
    data = loads(record.value)
    
    mapped = map_func(data)

    return RecordUtils.add_header(Record(record.headers, record.key, mapped, None), "Content-Type", "application/n-triples")


source = KafkaSource(topic=SOURCE_TOPIC, kafka_config=kafka_config)
target = KafkaSink(topic=TARGET_TOPIC, kafka_config=kafka_producer_config)
mapper = Mapper(source, target, mapping_function, name=SOURCE_TOPIC + " to " + TARGET_TOPIC + " Mapper", has_reporter=False, reporting_batch_size=500, has_error_handler=False)
mapper.run()
