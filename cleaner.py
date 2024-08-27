import os

# Path to the directory
directory_path = './data'

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    # Check if the file ends with .json
    if filename.endswith(".json"):
        file_path = os.path.join(directory_path, filename)
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
