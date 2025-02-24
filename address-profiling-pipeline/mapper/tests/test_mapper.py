import pytest
from mapping_function import map_func 
import json

def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().split("\\n")

def load_json(file_path):
    """Reads a JSON file and returns its contents as a dictionary."""
    with open(file_path, "r") as file:
        return json.load(file)
    
def test_map_func():
    input = load_json('tests/input.json')
    expected_output = load_file("tests/output.txt")
    mapped_result = map_func(input).strip()
    result_array = mapped_result.split("\n")
    assert set(result_array) == set(expected_output)

if __name__ == "__main__":
    pytest.main()