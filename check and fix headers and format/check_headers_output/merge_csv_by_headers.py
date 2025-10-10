import os
import pandas as pd

# Get the directory where this script resides
base_dir = os.path.dirname(os.path.abspath(__file__))
merged_dir = os.path.join(base_dir, 'merged')
os.makedirs(merged_dir, exist_ok=True)

# Find all .csv files in base_dir and subfolders
csv_files = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith('.csv'):
            csv_files.append(os.path.join(root, file))

if not csv_files:
    print("No CSV files found.")
    exit(1)

# Read headers from all files
header_map = {}
for file in csv_files:
    try:
        df = pd.read_csv(file, nrows=0)
        header_tuple = tuple(df.columns)
        header_map.setdefault(header_tuple, []).append(file)
    except Exception as e:
        print(f"Skipping {file}: {e}")

# Merge files with matching headers
for headers, files in header_map.items():
    if len(files) < 2:
        continue  # Only merge if more than one file with same headers
    dfs = []
    for file in files:
        try:
            dfs.append(pd.read_csv(file))
        except Exception as e:
            print(f"Error reading {file}: {e}")
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        out_name = f"merged_{'_'.join([str(h) for h in headers])}.csv"
        out_path = os.path.join(merged_dir, out_name)
        merged_df.to_csv(out_path, index=False)
        print(f"Merged {len(files)} files into {out_path}")
print("Merging complete.")
