import os
import pandas as pd

# Get current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Folder paths
input_source_folder = os.path.join(script_dir, 'Input source')
input_mask_folder = os.path.join(script_dir, 'Input mask')
output_folder = os.path.join(script_dir, 'Output folder')

# Find first CSV file in each folder
source_files = [f for f in os.listdir(input_source_folder) if f.lower().endswith('.csv')]
mask_files = [f for f in os.listdir(input_mask_folder) if f.lower().endswith('.csv')]

if not source_files:
    print(f"No CSV file found in {input_source_folder}")
    exit(1)
if not mask_files:
    print(f"No CSV file found in {input_mask_folder}")
    exit(1)

file1 = os.path.join(input_source_folder, source_files[0])
file2 = os.path.join(input_mask_folder, mask_files[0])

os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, 'matched_rows.csv')

# Load both files
try:
    df1 = pd.read_csv(file1, dtype=str)
    df2 = pd.read_csv(file2, dtype=str)
except Exception as e:
    print(f"Error loading files: {e}")
    exit(1)

# Ensure 'promotion_code' column exists
if 'promotion_code' not in df1.columns or 'promotion_code' not in df2.columns:
    print("Both files must contain a 'promotion_code' column.")
    exit(1)

# Prepare mapping from lower-case code in source to original code in mask
mask_map = {code.lower(): code for code in df2['promotion_code'].dropna()}

# Filter rows from first file where code matches any in second file (case-insensitive)
matched = df1[df1['promotion_code'].str.lower().isin(mask_map.keys())].copy()

# Replace promotion_code in output with the value from mask file
matched['promotion_code'] = matched['promotion_code'].str.lower().map(mask_map)

# Save result
matched.to_csv(output_file, index=False)
print(f"Matched rows saved to {output_file}")
