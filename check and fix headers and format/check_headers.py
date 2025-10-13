import os
import pandas as pd
import numpy as np
from difflib import get_close_matches
from colorama import Fore, Style, init

from dateutil.parser import parse

# Initialize colorama
init(autoreset=True)

# Paths
folder_path = r"check and fix headers and format"
output_folder = os.path.join(folder_path, "check_headers_output")
FORCE_DATE_ORDER = 'monthfirst'  # Options: 'dayfirst', 'monthfirst', None
os.makedirs(output_folder, exist_ok=True)

# Intended schema and order
INTENDED_HEADERS = [
    "promotion_code",
    "product_sku",
    "product_ean",
    "redemption_date",
    "quantity",
    "sales_value",
    "currency"
]

# Columns to treat as text
TEXT_COLUMNS = ["promotion_code", "product_sku", "product_ean", "currency"]
NUMERIC_COLUMNS = ["quantity", "sales_value"]

# Placeholders to treat as missing
NA_VALUES = ["N/A", "NA", "NaN", "null", ""]

def normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "_")

def match_headers(headers):
    """Match headers to intended schema using exact match, fuzzy match, or date rule."""
    fixed = []
    used_matches = set()
    for h in headers:
        norm_h = normalize(h)

        # Any column mentioning 'date' → redemption_date
        if "date" in norm_h:
            print(f"{Fore.YELLOW}⚠ Interpreting header '{h}' as 'redemption_date'{Style.RESET_ALL}")
            fixed.append("redemption_date")
            used_matches.add("redemption_date")
            continue

        # Exact match
        if norm_h in [normalize(i) for i in INTENDED_HEADERS]:
            match = [i for i in INTENDED_HEADERS if normalize(i) == norm_h][0]
            fixed.append(match)
            used_matches.add(match)
        else:
            # Fuzzy match
            candidates = get_close_matches(norm_h, [normalize(i) for i in INTENDED_HEADERS], n=1, cutoff=0.6)
            if candidates:
                match = [i for i in INTENDED_HEADERS if normalize(i) == candidates[0]][0]
                print(f"{Fore.YELLOW}⚠ Corrected header '{h}' → '{match}'{Style.RESET_ALL}")
                fixed.append(match)
                used_matches.add(match)
            else:
                print(f"{Fore.RED}❌ Could not match header '{h}' to intended schema{Style.RESET_ALL}")
                fixed.append(h)
    return fixed

def reorder_and_fix_dataframe(df):
    """Reorder dataframe columns and insert missing ones with NaN."""
    reordered = pd.DataFrame()
    for col in INTENDED_HEADERS:
        if col in df.columns:
            reordered[col] = df[col]
        else:
            print(f"{Fore.RED}❌ Missing column '{col}' → inserting empty column.{Style.RESET_ALL}")
            reordered[col] = np.nan  # proper NaN for missing
    # Append extra columns at the end
    extras = [c for c in df.columns if c not in INTENDED_HEADERS]
    if extras:
        print(f"{Fore.MAGENTA}ℹ Extra columns preserved at the end: {extras}{Style.RESET_ALL}")
        for col in extras:
            reordered[col] = df[col]
    return reordered

def parse_dates_column(series, col_name):
    """Parse a date column into ISO yyyy-mm-dd, inferring day/month order."""
    if series.isna().all():
        return series
    parsed_dayfirst = pd.to_datetime(series, errors="coerce", dayfirst=True, infer_datetime_format=True)
    parsed_monthfirst = pd.to_datetime(series, errors="coerce", dayfirst=False, infer_datetime_format=True)
    dayfirst_valid = parsed_dayfirst.notna().sum()
    monthfirst_valid = parsed_monthfirst.notna().sum()
    if dayfirst_valid > monthfirst_valid:
        parsed = parsed_dayfirst
        print(f"{Fore.GREEN}✅ Parsed '{col_name}' as DMY (day-first){Style.RESET_ALL}")
    elif monthfirst_valid > dayfirst_valid:
        parsed = parsed_monthfirst
        print(f"{Fore.GREEN}✅ Parsed '{col_name}' as MDY (month-first){Style.RESET_ALL}")
    else:
        # If equal, use FORCE_DATE_ORDER if set
        if FORCE_DATE_ORDER == 'dayfirst':
            parsed = parsed_dayfirst
            print(f"{Fore.YELLOW}⚠ Forced '{col_name}' as DMY (day-first) due to FORCE_DATE_ORDER{Style.RESET_ALL}")
        elif FORCE_DATE_ORDER == 'monthfirst':
            parsed = parsed_monthfirst
            print(f"{Fore.YELLOW}⚠ Forced '{col_name}' as MDY (month-first) due to FORCE_DATE_ORDER{Style.RESET_ALL}")
        else:
            parsed = parsed_dayfirst
            print(f"{Fore.YELLOW}⚠ Equal valid dates for DMY/MDY, defaulting to day-first for '{col_name}'{Style.RESET_ALL}")
    return parsed.dt.strftime("%Y-%m-%d")

def drop_empty_rows(df, text_cols, numeric_cols):
    """Drop rows completely empty or containing only placeholders."""
    is_empty = pd.Series(True, index=df.index)
    for col in text_cols:
        if col in df.columns:
            is_empty &= df[col].replace(NA_VALUES + ['<NA>'], pd.NA).isna()
    for col in numeric_cols:
        if col in df.columns:
            is_empty &= df[col].isna() | (df[col] == 0)
    before = len(df)
    df = df[~is_empty]
    removed = before - len(df)
    if removed > 0:
        print(f"{Fore.YELLOW}⚠ Removed {removed} fully empty rows{Style.RESET_ALL}")
    return df

def main():
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".csv"):
            continue
        file_path = os.path.join(folder_path, filename)
        print(f"\n📂 Processing {filename}")

        # Load CSV with placeholders treated as NaN
        df = pd.read_csv(file_path, dtype=str, na_values=NA_VALUES, keep_default_na=True)

        # Match headers
        df.columns = match_headers(list(df.columns))

        # Reorder and insert missing columns
        corrected_df = reorder_and_fix_dataframe(df)

        # Force text columns
        for col in TEXT_COLUMNS:
            if col in corrected_df.columns:
                corrected_df[col] = corrected_df[col].astype(str).replace("nan", pd.NA)

        # Force numeric columns
        for col in NUMERIC_COLUMNS:
            if col in corrected_df.columns:
                corrected_df[col] = pd.to_numeric(corrected_df[col], errors="coerce")
                # Convert to integer type if possible
                if col == "quantity":
                    # Convert floats to int safely, preserving NaN
                    corrected_df[col] = corrected_df[col].apply(lambda x: int(x) if pd.notna(x) else pd.NA)

        # Parse date columns
        for col in corrected_df.columns:
            if "date" in col.lower():
                corrected_df[col] = parse_dates_column(corrected_df[col], col)

        # Drop fully empty rows
        corrected_df = drop_empty_rows(corrected_df, TEXT_COLUMNS, NUMERIC_COLUMNS)

        # Save corrected CSV
        new_path = os.path.join(output_folder, f"corrected_{filename}")
        corrected_df.to_csv(new_path, index=False)
        print(f"{Fore.CYAN}💾 Corrected file saved as {new_path}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
