import pandas as pd
from pathlib import Path

# Paths
base_folder = Path("Extract unique voucher codes")

# Find all *.csv files
output_files = list(base_folder.glob("*.csv"))

if not output_files:
    print("No processed output files found.")
else:
    print(f"Found {len(output_files)} output files.")

    codes = set()

    for f in output_files:
        try:
            df = pd.read_csv(f, dtype=str, usecols=["promotion_code"])
        except Exception as e:
            print(f"  Skipped {f.name}: {e}")
            continue

        new_codes = df["promotion_code"].dropna().str.strip().unique().tolist()
        codes.update(new_codes)
        print(f"  Collected {len(new_codes)} codes from {f.name}")

    # Save to CSV
    codes_df = pd.DataFrame(sorted(codes), columns=["code"])
    output_file = base_folder / "unique_voucher_codes.csv"
    codes_df.to_csv(output_file, index=False)

    print(f"\nSaved {len(codes_df)} unique codes to {output_file}")
