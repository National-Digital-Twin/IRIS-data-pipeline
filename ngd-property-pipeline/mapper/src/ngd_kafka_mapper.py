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

import ast
from generic_mapper.src.generic_kafka_mapper import GenericKafkaMapper
import ies_tool.ies_tool as ies_tool
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = True  # output to local file if True

class NgdKafkaMapper(GenericKafkaMapper):
    
    data_ns = "http://ndtp.co.uk/data#"
    ies_ns = "http://informationexchangestandard.org/ont/ies#"
    
    ies = ies_tool.IESTool(data_ns)
    
    def get_uprn(self, record: dict):
        uprn_reference = ast.literal_eval(record["uprnreference"])
        #TODO: a building can contain multiple UPRNs, so we need to ensure we create a mapping for each one
        return uprn_reference[0]["uprn"]

    def map_record(self, record: dict) -> str:
        """
        Creates the graph and orchestrates its mappings.
        
        Args:
            record (dict): A record representing a building.
            
        Returns:
            str: The RDF graph serialized into triples.
        """
        self.ies.clear_graph()
        # first our namespaces
        self.ies.graph.namespace_manager.bind("data", self.data_ns)
        self.ies.graph.namespace_manager.bind("ies", self.ies_ns)

        if DEBUG_MODE:
            self.ies.graph.serialize(destination=f"{self.get_uprn(record)}_os_ngd.ttl", format="turtle")
            return
        
        record = self.ies.graph.serialize(format="turtle")
        return record
    
if __name__ == "__main__":
    mapper = NgdKafkaMapper()
    mapper.run_mapper()