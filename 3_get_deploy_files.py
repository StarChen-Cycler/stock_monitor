import os
import json

# Define the base path of the project
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
# APP_FOLDER_NAME = "flask_app"  # Modify this variable to change the app folder name

# Path to the app_files.json that stores file paths
app_files_json = os.path.join(PROJECT_ROOT, "app_files.json")

# Function to read the app files from app_files.json
def read_app_files():
    if os.path.exists(app_files_json):
        with open(app_files_json, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    return []

# Function to read the content of a file
def read_file_content(file_path):
    full_file_path = os.path.join(PROJECT_ROOT, file_path)
    with open(full_file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Dictionary to store file paths and their content
files_content = {}

# Read the file paths from app_files.json
file_paths = read_app_files()

# Traverse the file paths and read their content
for file_path in file_paths:
    full_file_path = os.path.join(PROJECT_ROOT, file_path)
    if os.path.exists(full_file_path):
        # Read the content of each file
        content = read_file_content(file_path)
        # Store the content in the dictionary with the file path as key
        files_content[file_path] = content
    else:
        print(f"File not found: {full_file_path}")

# Save the content of files to a JSON file
def save_files_to_json():
    with open(os.path.join(PROJECT_ROOT, "files_content.json"), 'w', encoding='utf-8') as json_file:
        json.dump(files_content, json_file, ensure_ascii=False, indent=4)
    print("Files content saved to files_content.json.")

# Run the function to save the files
if __name__ == '__main__':
    save_files_to_json()