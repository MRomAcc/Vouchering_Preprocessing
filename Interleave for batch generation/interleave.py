import pandas as pd
from pathlib import Path

# --- CONFIG ---
script_path = Path(__file__).parent
input_folder = script_path / "input"
output_folder = script_path / "output"

# Search for the first file in the input folder
input_files = list(input_folder.glob("*.csv"))
if not input_files:
    raise FileNotFoundError(f"No CSV files found in the input folder: {input_folder}")
input_file = input_files[0]

output_file = output_folder / "output.csv"
# --------------

# Read CSV
df = pd.read_csv(input_file)

# Get unique offer names in the order they appear
offers = df["offer_name"].unique().tolist()

# Split into groups
groups = [df[df["offer_name"] == offer].reset_index(drop=True) for offer in offers]

# Ensure all groups have the same length
lengths = [len(g) for g in groups]
if len(set(lengths)) != 1:
    raise ValueError(f"Offer groups have different lengths: {dict(zip(offers, lengths))}")

# Interleave rows
interleaved_parts = []
for i in range(lengths[0]):  # row index within each group
    for g in groups:
        interleaved_parts.append(g.iloc[i])

# Combine into DataFrame
interleaved_df = pd.DataFrame(interleaved_parts)

# Save
output_folder.mkdir(parents=True, exist_ok=True)
interleaved_df.to_csv(output_file, index=False)

print(f"Interleaved file saved as: {output_file}")
