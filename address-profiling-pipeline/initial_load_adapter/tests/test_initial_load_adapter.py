from unittest.mock import patch
import pytest
from producer import generate_records
import json
import os

def load_expected_output(file_name):
    """Reads the expected output file and returns a list of stripped lines."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

@pytest.mark.address_profiling_pipeline    
def test_generate_records():
    test_input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "input.csv"))

    with patch('producer.FILENAME', test_input_file):
        expected_output = load_expected_output("output.json")
        records = list(generate_records())

        actual_output = []
        for record in records:
            actual_output.extend(record.value.strip().split("\n"))

        assert set(actual_output) == set(expected_output)

if __name__ == "__main__":
    pytest.main()