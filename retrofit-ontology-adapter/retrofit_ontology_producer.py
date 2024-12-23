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
from telicent_lib import Record, Adapter
from telicent_lib.records import RecordUtils
from telicent_lib.config import Configurator
from typing import Iterable
from dotenv import load_dotenv
from typing import Union, List

load_dotenv()
# Mapper Configuration
config = Configurator()
broker = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
target_topic= config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
name = config.get("PRODUCER_NAME", required=True, 
                    description="Specifies the name of the producer")
source_name=config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")
debug = config.get("DEBUG", required=False, default=False, converter=bool, required_type=bool)

def generate_records() -> Iterable[Record]:
    return Record(RecordUtils.to_headers(
        {
            "Content-Type": "text/turtle",
            "Data-Source": source_name,
            "Data-Producer": name,
            "Security-Label": default_security_label
        }),
        None, 
        ttl_file.encode('utf-8')
    )


def process_source(adapter) -> Union[Record, List[Record], None]:
    adapter.send(generate_records())

if __name__ == "__main__":
    # Set security label
    default_security_label = "*"
    # Loop through all files
   
    # Load ttl file
    with open("ndt_retrofit_buildings_extensions.ttl", "r") as file:
        ttl_file = file.read()

        # Instantiate Sink for different topics 
        sink_ttl = KafkaSink(target_topic, broker)
        adapter = Adapter(sink_ttl, name=name, source_name=source_name)
        
        adapter.run()
        process_source(adapter)
        adapter.finished()