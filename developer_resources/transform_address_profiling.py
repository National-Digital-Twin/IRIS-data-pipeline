import sys
import uuid
from pathlib import Path

import pandas as pd


def parse_args(args):
    input_file_1 = args[0]
    input_file_2 = args[1]
    path = Path(input_file_1)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    output_filename = path.stem
    path = Path(input_file_2)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    return [input_file_1, input_file_2, output_filename]


input_file_1, input_file_2, output_filename = parse_args(sys.argv[1:])

df1 = pd.read_csv(input_file_1, low_memory=False)
df2 = pd.read_csv(input_file_2, sep="|")

merged_df = pd.merge(
    df1, df2[["UPRN"]], on="UPRN", how="inner"  # Only keep UPRN from second file
)

# Create first CSV with required fields and UUID
csv1_data = merged_df[["UPRN", "SAPBand", "LodgementDate"]].copy()
csv1_data.columns = ["uprn", "epc_rating", "lodgement_date"]

# Add UUID column and move it to front
csv1_data.insert(0, "id", [str(uuid.uuid4()) for _ in range(len(csv1_data))])

# Replace any INVALID! values for epc_rating with ''
csv1_data = csv1_data.replace("INVALID!", "")

# Save first CSV with pipe separator
csv1_data.to_csv(f"{output_filename}_epc_transformed.csv", sep="|", index=False)

# Create second CSV with remaining fields
csv2_data = merged_df[
    [
        "PropertyType",
        "BuiltForm",
        "MainFuelType",
        "MultipleGlazingType",
        "WallConstruction",
        "WallInsulationType",
        "RoofConstruction",
        "RoofInsulationLocation",
        "RoofInsulationThickness",
        "FloorConstruction",
        "FloorInsulation",
    ]
].copy()

# Rename columns according to requirements
csv2_data.columns = [
    "type",
    "built_form",
    "fuel_type",
    "window_glazing",
    "wall_construction",
    "wall_insulation",
    "roof_construction",
    "roof_insulation",
    "roof_insulation_thickness",
    "floor_construction",
    "floor_insulation",
]

# Add id field from first CSV and move it to front
csv2_data.insert(0, "epc_assessment_id", csv1_data["id"])

# Save second CSV with pipe separator
csv2_data.to_csv(
    f"{output_filename}_structure_unit_transformed.csv", sep="|", index=False
)
