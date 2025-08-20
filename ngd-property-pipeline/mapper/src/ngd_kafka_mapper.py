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