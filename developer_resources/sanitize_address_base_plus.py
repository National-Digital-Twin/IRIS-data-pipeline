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


CHUNK_SIZE = 100000

input_file_1, input_file_2, output_filename = parse_args(sys.argv[1:])

# Initialize empty DataFrame for results
result_df = pd.DataFrame()

# Get total row counts for progress tracking
df1_total = sum(1 for _ in open(input_file_1)) - 1
df2_total = sum(1 for _ in open(input_file_2)) - 1

# Process both files in chunks simultaneously
df1_chunks = pd.read_csv(input_file_1, chunksize=CHUNK_SIZE, sep="|")

processed_rows = 0
for chunk1 in df1_chunks:
    chunk1 = chunk1.drop_duplicates(subset=["UPRN"])

    current_chunk_uprns = set(chunk1["UPRN"])

    df2_chunks = pd.read_csv(input_file_2, chunksize=CHUNK_SIZE, sep="|")

    seen_uprns = set()

    for chunk2 in df2_chunks:
        chunk2 = chunk2.drop_duplicates(subset=["UPRN"])

        seen_uprns.update(chunk2["UPRN"])

        del chunk2

    non_matches = chunk1[~chunk1["UPRN"].isin(seen_uprns)]

    # Accumulate results efficiently
    if result_df.empty:
        result_df = non_matches
    else:
        result_df = pd.concat([result_df, non_matches], ignore_index=True)

    del chunk1, current_chunk_uprns, seen_uprns, non_matches

    # Update progress
    processed_rows += CHUNK_SIZE
    print(f"Processed {processed_rows:,}/{df2_total:,} rows from second file", end="\r")

# Save to CSV (in real usage, uncomment this line)
result_df.to_csv(f"{output_filename}-sanitized.csv", index=False, sep="|")
