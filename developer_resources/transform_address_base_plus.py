import sys
from pathlib import Path

import pandas as pd


def parse_args(args):
    input_file = args[0]
    path = Path(input_file)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    return [input_file, path.stem]


input_file, output_filename = parse_args(sys.argv[1:])

# Read the CSV file
df = pd.read_csv(input_file)

# Select and rename columns
result_df = df[
    ["UPRN", "TOID", "Address", "PostcodeLocator", "Latitude", "Longitude"]
].copy()
result_df = result_df.rename(
    columns={"Address": "first_line_of_address", "PostcodeLocator": "post_code"}
)

# Create POINT column using WKT format
result_df["point"] = result_df.apply(
    lambda row: f"POINT({row['Longitude']} {row['Latitude']})", axis=1
)

# Drop original coordinate columns
result_df = result_df.drop(["Latitude", "Longitude"], axis=1)

# Write to output file
result_df.to_csv(f"{output_filename}_transformed.csv", index=False, sep="|")
