import os
import json

# Define the base path of the project
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_FOLDER_NAME = "flask_app"  # Modify this variable to change the app folder name

# Define folder paths relative to the project root
folders = [
    f"{APP_FOLDER_NAME}/templates",
    f"{APP_FOLDER_NAME}/static",
    f"{APP_FOLDER_NAME}/static/images",
    f"{APP_FOLDER_NAME}/migrations",
]

# Ensure the necessary folders exist
for folder in folders:
    os.makedirs(os.path.join(PROJECT_ROOT, folder), exist_ok=True)

# Read the file contents from the saved JSON
with open(os.path.join(PROJECT_ROOT, "files_content.json"), 'r', encoding='utf-8') as json_file:
    files = json.load(json_file)

# Create files with the specified content and correct encoding (UTF-8)
for file_path, content in files.items():
    # Create the full file path relative to the project root
    full_file_path = os.path.join(PROJECT_ROOT, file_path)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {full_file_path}")

print("Deployment complete! Now run flask db init, migrate, and upgrade.")