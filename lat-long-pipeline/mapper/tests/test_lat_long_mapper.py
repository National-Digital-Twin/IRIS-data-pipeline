import pytest
import importlib
import mapping_function
importlib.reload(mapping_function)
from mapping_function import map_func
import json
import os
from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff

def load_file(file_name):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().split("\n")

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

@pytest.mark.lat_long_pipeline    
def test_map_func():
    input_data = load_json('input.json')
    expected_graph = Graph().parse(f"{os.getcwd()}/lat-long-pipeline/mapper/tests/output.txt", format="turtle", publicID="")    
    mapped_result = map_func(input_data).strip()
    actual_graph = Graph().parse(data=mapped_result, format="turtle")
    check_equivalent_graphs(expected_graph, actual_graph)

if __name__ == "__main__":
    pytest.main()