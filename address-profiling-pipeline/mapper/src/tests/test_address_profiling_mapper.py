import json
import os

import pytest
from ies_tool.ies_tool import IESTool
from mapping_functions.mapping_function_factory import get_mapping_function
from namespaces import data_ns
from rdflib import Graph
from rdflib.compare import graph_diff, to_isomorphic


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


def __test_mapping_function(output_file_suffix: str, mapper_sub_type: str):
    input_data = load_json("assets/inputs.json")
    for record in input_data:
        file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                f"assets/output_{record.get('UPRN')}_{output_file_suffix}.txt",
            )
        )
        try:
            expected_graph = Graph().parse(
                file_path,
                format="turtle",
                publicID="",
            )
            ies = IESTool(data_ns)
            mapped_result = get_mapping_function(mapper_sub_type)(record, ies).strip()
            actual_graph = Graph().parse(data=mapped_result, format="turtle")
            check_equivalent_graphs(expected_graph, actual_graph)
        except FileNotFoundError:
            mapped_result = get_mapping_function(mapper_sub_type)(record, ies)
            assert mapped_result is None


def test_structure_unit_mapping_function():
    __test_mapping_function("structure_unit", "STRUCTURE_UNIT")


def test_epc_assessment_mapping_function():
    __test_mapping_function("epc_assessment", "EPC_ASSESSMENT")


def test_floor_mapping_function():
    __test_mapping_function("floor", "FLOOR")


def test_roof_mapping_function():
    __test_mapping_function("roof", "ROOF")


def test_wall_mapping_function():
    __test_mapping_function("wall", "WALL")


def test_window_mapping_function():
    __test_mapping_function("window", "WINDOW")


def test_heating_mapping_function():
    __test_mapping_function("heating", "HEATING")


if __name__ == "__main__":
    pytest.main()
