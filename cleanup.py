import os

# Get the directory where this script resides
base_dir = os.path.dirname(os.path.abspath(__file__))

# Traverse all subfolders and delete .csv files
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith('.csv'):
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
print("Cleanup complete.")
