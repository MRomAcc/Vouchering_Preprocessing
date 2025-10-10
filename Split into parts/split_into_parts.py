import pandas as pd
import math

def split_csv(input_file, output_prefix, parts=2):
    # Read CSV
    df = pd.read_csv(input_file)

    # Calculate rows per split
    total_rows = len(df)
    rows_per_file = math.ceil(total_rows / parts)

    for i in range(parts):
        start_row = i * rows_per_file
        end_row = start_row + rows_per_file
        df_part = df.iloc[start_row:end_row]

        output_file = f"{output_prefix}_part{i+1}.csv"
        df_part.to_csv(output_file, index=False)
        print(f"Saved {output_file} with {len(df_part)} rows.")

if __name__ == "__main__":
    # Example usage
    split_csv("test.csv", "output")
