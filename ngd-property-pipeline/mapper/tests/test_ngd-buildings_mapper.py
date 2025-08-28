import pytest
import importlib
import ngd_kafka_mapper
importlib.reload(ngd_kafka_mapper)
from ngd_kafka_mapper import map_record
import json
import os
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff

def load_file(file_name):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.read().split("\n")
        return [line for line in lines if line]

def load_json(file_name):
    """Reads a JSON file and returns its contents as a dictionary."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    with open(file_path, "r") as file:
        return json.load(file)

def check_equivalent_graphs(expected_graph, actual_graph):
    i_expected_g = to_isomorphic(expected_graph)
    i_actual_g = to_isomorphic(actual_graph)
    graphs_equal = i_expected_g == i_actual_g
    
    if not graphs_equal:
        in_both, in_first, in_second = graph_diff(i_expected_g, i_actual_g)

        print("✅ Triples in both graphs:\n", in_both.serialize(format="nt"))
        print("❌ Missing in actual_graph:\n", in_first.serialize(format="nt"))
        print("🔺 Extra in actual_graph:\n", in_second.serialize(format="nt"))
    assert graphs_equal

@pytest.mark.ngd_property_pipeline     
def test_map_func():
    input_data = load_json('inputs.json')
    for record in input_data:
        expected_graph = Graph().parse(f"{os.getcwd()}/ngd-property-pipeline/mapper/tests/output_{record.get('osid')}.txt", format="turtle", publicID="")     
        mapped_result = map_record(record).strip()
        actual_graph = Graph().parse(data=mapped_result, format="turtle")
        check_equivalent_graphs(expected_graph, actual_graph)

if __name__ == "__main__":
    pytest.main()