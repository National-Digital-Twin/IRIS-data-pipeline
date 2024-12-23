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

from telicent_lib import Record, RecordUtils, AutomaticAdapter
from telicent_lib.config import Configurator

from telicent_lib.access import SecurityLabelBuilder, EDHSecurityLabelsV2
from json import dumps
from typing import Iterable
import csv
from dotenv import load_dotenv


load_dotenv()
config = Configurator()
broker = config.get("BOOTSTRAP_SERVERS", required=True,
                    description="Specifies the Kafka Bootstrap Servers to connect to.")
target_topic = config.get("TARGET_TOPIC", required=True,
                    description="Specifies the Kafka topic the mapper pushes its output to")
name = config.get("PRODUCER_NAME", required=True, 
                    description="Specifies the name of the producer")
source_name=config.get("SOURCE_NAME", required=True, 
                    description="Specifies the source that the data has originated from")


# Define our adapter function, this is just a Python generator function that 
# generates the Record instance to be written out to the DataSink
file_name = "./uprn_lat_lon.csv"


permitted_nationalities=['GBR', 'NZL']
default_security_label = SecurityLabelBuilder().add_multiple(EDHSecurityLabelsV2.PERMITTED_NATIONALITIES.value, *permitted_nationalities).build()


def create_record(data, security_labels):
    return Record(RecordUtils.to_headers({ 
        "Content-Type": "application/json",
        "Data-Source": source_name, 
        "Data-Producer": name, 
        "Security-Label": security_labels
    }), None, dumps(data))

def generate_records() -> Iterable[Record]:
    i=0

    with open(file_name, 'r', encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            i += 1
            yield create_record(row, default_security_label)

# Create a sink and the adapter
sink = KafkaSink(target_topic, broker)
adapter = AutomaticAdapter(target=sink, adapter_function=generate_records, 
                           name=name, source_name=source_name)

# Call run() to run the action
adapter.run()
