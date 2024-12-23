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
from telicent_lib.sources import KafkaSource, KafkaResetPosition
from telicent_lib.config import Configurator
from telicent_lib.logging import CoreLoggerFactory
from telicent_lib import Mapper, Record, RecordUtils
from typing import Union, List
from json import loads
from mapping_function import map_func
from dotenv import load_dotenv

load_dotenv()
config = Configurator()
broker = config.get(
    "BOOTSTRAP_SERVERS",
    required=True,
    description="Specifies the Kafka Bootstrap Servers to connect to.",
)
source_topic = config.get(
    "SOURCE_TOPIC",
    required=True,
    description="Specifies the Kafka topic the mapper ingests from.",
)
target_topic = config.get(
    "TARGET_TOPIC",
    required=True,
    description="Specifies the Kafka topic the mapper pushes its output to",
)
debug = config.get(
    "DEBUG", required=False, default=False, converter=bool, required_type=bool
)

logger = CoreLoggerFactory.get_logger(
    "{source}-to-{target}-mapper".format(source=source_topic, target=target_topic),
    broker=broker,
    topic="telicent-logging",
)


# Function each record on the source topic is passed to.
def mapping_function(record: Record) -> Union[Record, List[Record], None]:
    # Add mapping logic here
    # Try to keep it small and performant
    data = loads(record.value)

    mapped = map_func(data)
    if mapped is None:
        logger.warning(
            "{uprn}, {address} does not container a lat/lon lookup".format(
                uprn=data["UPRN"], address=data["Address"]
            ),
        )
        print(
            "{uprn}, {address} does not container a lat/lon lookup".format(
                uprn=data["UPRN"], address=data["Address"]
            )
        )
        return mapped
    return RecordUtils.add_header(
        Record(record.headers, record.key, mapped, None),
        "Content-Type",
        "text/turtle",
    )


source = KafkaSource(
    topic=source_topic, broker=broker, reset_position=KafkaResetPosition.BEGINNING
)
target = KafkaSink(topic=target_topic, broker=broker)
mapper = Mapper(
    source,
    target,
    mapping_function,
    name=source_topic + " to " + target_topic + " Mapper",
    has_reporter=False,
    reporting_batch_size=500,
)
mapper.run()
