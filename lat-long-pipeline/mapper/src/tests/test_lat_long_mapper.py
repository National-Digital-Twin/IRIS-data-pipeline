import json
import os

import pytest
from mapping_function import map_func
from rdflib import Graph
from rdflib.compare import graph_diff, to_isomorphic


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


def test_map_func():
    input_data = load_json("assets/input.json")
    expected_graph = Graph().parse(
        "src/tests/assets/output.txt",
        format="turtle",
        publicID="",
    )
    mapped_result = map_func(input_data).strip()
    actual_graph = Graph().parse(data=mapped_result, format="turtle")
    check_equivalent_graphs(expected_graph, actual_graph)


if __name__ == "__main__":
    pytest.main()
