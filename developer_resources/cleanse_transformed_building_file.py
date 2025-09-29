import sys
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

CHUNK_SIZE = 100000

result_df = pd.DataFrame()

# Read the first CSV file (with | delimiter)
df1 = pd.read_csv(input_file_1, sep="|", low_memory=False)

df_2_total = sum(1 for _ in open(input_file_2)) - 1

# Read the second CSV file (with , delimiter)
df2_chunks = pd.read_csv(input_file_2, sep=",", low_memory=False, chunksize=CHUNK_SIZE)

for df2_chunk in df2_chunks:

    # Filter df1 for domestic certificates
    domestic_df = df2_chunk[df2_chunk["CertificateType"] == "domestic"]

    # Merge the filtered dataframe with df2 on UPRN
    merged_df = pd.merge(
        domestic_df[["UPRN"]],
        df1,
        on="UPRN",
        how="inner",
    )

    result_df = pd.concat([result_df, merged_df], ignore_index=True)

    del df2_chunk, domestic_df, merged_df

# Save the result to a new CSV file
result_df.to_csv(f"cleansed-{output_filename}.csv", index=False, sep="|")
