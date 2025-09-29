import sys
from pathlib import Path

import pandas as pd


def parse_args(args):
    input_file_1 = args[0]
    input_file_2 = args[1]
    input_file_3 = args[2]
    path = Path(input_file_1)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    path = Path(input_file_2)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    output_filename_1 = path.stem
    path = Path(input_file_3)
    if not path.exists():
        print(f"The file {path.name} does not exist!")
        exit(1)
    output_filename_2 = path.stem
    return [
        input_file_1,
        input_file_2,
        input_file_3,
        output_filename_1,
        output_filename_2,
    ]


input_file_1, input_file_2, input_file_3, output_filename_1, output_filename_2 = (
    parse_args(sys.argv[1:])
)


# Read the first CSV file (with | delimiter)
df1 = pd.read_csv(input_file_1, sep="|", low_memory=False)

# Read the second CSV file (with , delimiter)
df2 = pd.read_csv(input_file_2, sep="|", low_memory=False)

# Read the second CSV file (with , delimiter)
df3 = pd.read_csv(input_file_3, sep="|", low_memory=False)

merged_df_1 = pd.merge(
    df1[["UPRN"]],
    df2,
    left_on="UPRN",
    right_on="uprn",
    how="inner",
)

# Merge the filtered dataframe with df2 on UPRN
merged_df_2 = pd.merge(
    merged_df_1[["id"]],
    df3,
    left_on="id",
    right_on="epc_assessment_id",
    how="inner",
)

merged_df_2["fuel_type"] = merged_df_2["fuel_type"].replace(
    {"DualFuel": "Other", "Biogas": "Other"}
)
merged_df_2["floor_construction"] = merged_df_2["floor_construction"].replace(
    {
        "Unknown": "",
        "NULL": "",
        "Other": "Floor",
        "Solid": "SolidFloor",
        "SuspendedTimber": "Suspended",
        "SuspendedNotTimber": "Suspended",
        "OtherPremisesBelow": "OtherPremisesBelowFloor",
        "AnotherDwellingBelow": "AnotherDwellingBelowFloor",
    }
)
merged_df_2["floor_insulation"] = merged_df_2["floor_insulation"].replace(
    {
        "NULL": "",
        "AsBuilt": "",
        "RetroFitted": "InsulatedFloor",
        "NoInsulation": "NoInsulationInFloor",
        "Insulated": "InsulatedFloor",
        "LimitedInsulation": "LimitedFloorInsulation",
    }
)
merged_df_2["roof_construction"] = merged_df_2["roof_construction"].replace(
    {
        "NULL": "",
        "Flat": "FlatRoof",
        "AnotherDwellingAbove": "AnotherDwellingAbove",
        "OtherPremisesAbove": "OtherPremisesAbove",
        "Pitched": "PitchedRoof",
        "PitchedNormalLoftAccess": "PitchedRoof",
        "PitchedNormalNoLoftAccess": "PitchedRoof",
        "PitchedThatched": "ThatchedRoof",
        "PitchedWithSlopingCeiling": "PitchedRoof",
        "ParkHomeRoof": "RoofConstruction",
        "Thatched": "ThatchedRoof",
        "RoofRooms": "RoofRooms",
        "Other": "RoofConstruction",
    }
)
merged_df_2["roof_insulation"] = merged_df_2["roof_insulation"].replace(
    {
        "NULL": "NoInsulationInRoof",
        "": "NoInsulationInRoof",
        "Rafters": "InsulatedAtRafters",
        "InsulatedAtRafters": "InsulatedAtRafters",
        "CeilingInsulated": "CeilingInsulated",
        "Unknown": "NoInsulationInRoof",
        "None": "NoInsulationInRoof",
        "FlatRoofInsulation": "FlatRoofInsulation",
        "NoInsulation": "NoInsulationInRoof",
        "NoInsulation(Assumed)": "NoInsulationAssumedInRoof ",
        "NoInsulationAssumed": "NoInsulationAssumedInRoof",
        "LoftInsulation(Assumed)": "AssumedLoftInsulation",
        "LoftInsulation": "LoftInsulation",
        "LimitedInsulationAssumed": "LimitedInsulationAssumed",
        "LimitedInsulation": "LimitedInsulation",
        "InsulatedAssumed": "InsulatedAssumed",
        "Other": "Insulated",
        "Insulated": "Insulated",
        "Thatched": "InsulatedWithThatched",
        "ThatchedWithAdditionalInsulation": "ThatchedWithAdditionalInsulation",
    }
)
merged_df_2["wall_construction"] = merged_df_2["wall_construction"].replace(
    {
        "NULL": "",
        "Other": "Wall",
        "CavityWall": "CavityWall",
        "Cob": "Cob",
        "GraniteOrWhinstone": "GraniteOrWhinstone",
        "ParkHomeWall": "ParkHomeWall",
        "Sandstone": "Sandstone",
        "SolidBrick": "SolidBrick",
        "SystemBuilt": "SystemBuilt",
        "TimberFrame": "TimberFrame",
    }
)
merged_df_2["wall_insulation"] = merged_df_2["wall_insulation"].replace(
    {
        "NULL": "NoInsulationInWall",
        "": "NoInsulationInWall",
        "AsBuilt": "InsulatedWall",
        "FilledCavity": "InsulatedWall",
        "FilledCavityAndInternalInsulation": "InternalInsulation",
        "FilledCavityAndExternalInsulation": "ExternalInsulation",
        "WithAdditionalInsulation": "InsulatedWall",
        "WithInternalInsulation": "InternalInsulation",
        "WithExternalInsulation": "ExternalInsulation",
        "Unknown": "WallInsulation",
    }
)

# Save the result to a new CSV file
merged_df_1[["id", "uprn", "epc_rating", "lodgement_date"]].to_csv(
    f"cleansed_{output_filename_1}.csv", index=False, sep="|"
)
merged_df_2[
    [
        "epc_assessment_id",
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
].to_csv(f"cleansed_{output_filename_2}.csv", index=False, sep="|")
