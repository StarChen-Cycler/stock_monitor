import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Define the base path of the project folder
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_FOLDER_NAME = "flask_app"  # Modify this variable to change the app folder name

# Define the base path of the app folder
base_path = os.path.join(PROJECT_ROOT, APP_FOLDER_NAME)

# Path to the app_files.json that stores file paths
app_files_json = os.path.join(PROJECT_ROOT, "app_files.json")

# List of directories or files to exclude from tracking
EXCLUDED = [
    f"{APP_FOLDER_NAME}/migrations",
    f"{APP_FOLDER_NAME}/__pycache__",
    f"{APP_FOLDER_NAME}/site.db",
    f"{APP_FOLDER_NAME}/data_loader/__pycache__",
    f"{APP_FOLDER_NAME}/strategies/__pycache__",
    # os.path.join(APP_FOLDER_NAME, "migrations"),  # Exclude the migrations folder
    # os.path.join(APP_FOLDER_NAME, "__pycache__"), # Exclude Python cache files
    # os.path.join(APP_FOLDER_NAME, "site.db"),     # Exclude the SQLite database
]

# Function to read the app files from app_files.json
def read_app_files():
    if os.path.exists(app_files_json):
        with open(app_files_json, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    return []

# Function to write the updated file paths to app_files.json
def write_app_files(file_paths):
    with open(app_files_json, 'w', encoding='utf-8') as json_file:
        json.dump(file_paths, json_file, ensure_ascii=False, indent=4)
    print("Updated app_files.json")

# Function to check if a file or directory is excluded
def is_excluded(file_path):
    for exclusion in EXCLUDED:
        # Check if the file_path matches or starts with the exclusion path
        if file_path.startswith(exclusion):
            return True
    return False

# Function to recursively get all file paths in the app folder
def get_all_files_in_directory():
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        # Skip directories that are in the EXCLUDED list
        dirs[:] = [d for d in dirs if not any(d.startswith(exclusion) for exclusion in EXCLUDED)]
        for file in files:
            # Get the file path relative to the project root
            file_path = os.path.relpath(os.path.join(root, file), PROJECT_ROOT).replace(os.sep, '/')
            if not is_excluded(file_path):
                file_paths.append(file_path)
    return file_paths

# File system event handler for monitoring file changes
class WatcherHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self.handle_event(event)

    def on_created(self, event):
        self.handle_event(event)

    def on_deleted(self, event):
        self.handle_event(event)

    def on_moved(self, event):
        self.handle_event(event)

    def handle_event(self, event):
        print(f"Detected change: {event.src_path}")

        # Get the current list of file paths (excluding files in EXCLUDED list)
        file_paths = get_all_files_in_directory()

        # Write the updated list of file paths to app_files.json
        write_app_files(file_paths)

# Function to start the watchdog observer
def start_watching():
    # Set up event handler and observer
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, base_path, recursive=True)

    # Start the observer in a separate thread
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()