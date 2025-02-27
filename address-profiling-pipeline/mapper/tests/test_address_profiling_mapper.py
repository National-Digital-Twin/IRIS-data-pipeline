import pytest
from mapping_function import map_func 
import json
import os

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

@pytest.mark.address_profiling_pipeline     
def test_map_func():
    input_data = load_json('input.json')
    expected_output = load_file("output.txt")
    mapped_result = map_func(input_data).strip()
    result_array = mapped_result.split("\n")
    assert set(result_array) == set(expected_output)

if __name__ == "__main__":
    pytest.main()