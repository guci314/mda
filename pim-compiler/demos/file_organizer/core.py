import os
import shutil
from collections import defaultdict

def organize_files(source_dir, destination_dir, dry_run=False):
    """
    Organizes files from the source directory into subdirectories within the destination directory
    based on their file extensions.

    Args:
        source_dir (str): The path to the source directory.
        destination_dir (str): The path to the destination directory.
        dry_run (bool): If True, simulate the organization process without actual file operations.
    """
    print(f"Starting file organization from '{source_dir}' to '{destination_dir}' (Dry Run: {dry_run})")

    files_to_organize = defaultdict(list)

    # Group files by extension
    for filename in os.listdir(source_dir):
        source_path = os.path.join(source_dir, filename)
        if os.path.isfile(source_path):
            _, extension = os.path.splitext(filename)
            extension = extension.lower().lstrip('.') # Remove leading dot and convert to lowercase
            if not extension: # Handle files without extensions
                extension = "no_extension"
            files_to_organize[extension].append(filename)

    if not files_to_organize:
        print("No files found to organize.")
        return

    for extension, files in files_to_organize.items():
        target_subdir = os.path.join(destination_dir, extension)
        if not dry_run:
            os.makedirs(target_subdir, exist_ok=True)
            print(f"Created directory: {target_subdir}")
        else:
            print(f"Would create directory: {target_subdir}")

        for filename in files:
            source_path = os.path.join(source_dir, filename)
            destination_path = os.path.join(target_subdir, filename)

            if not dry_run:
                try:
                    shutil.move(source_path, destination_path)
                    print(f"Moved: '{filename}' to '{target_subdir}'")
                except Exception as e:
                    print(f"Error moving '{filename}': {e}")
            else:
                print(f"Would move: '{filename}' to '{target_subdir}'")

    print("File organization process completed.")