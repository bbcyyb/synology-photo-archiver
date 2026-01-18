import sys
from pathlib import Path

from .config import load_config
from .scanner import scan_for_new_and_modified_files
from .compression import create_archive


def main():
    """
    Main function for the archiver.
    Orchestrates configuration loading, file scanning, archiving, and state management.
    """
    config = load_config()
    print("Configuration loaded successfully.")

    # Get config values
    source_dir = config.get('Paths', 'source_dir')
    destination_dir = config.get('Paths', 'destination_dir')
    seven_zip_exec = config.get('Paths', '7z_executable')
    password = config.get('Archive', 'password')
    volume_size = config.get('Archive', 'volume_size')
    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {destination_dir}")

    processed_files = {}  # Always start with an empty state

    # Scan for new and modified files
    files_to_archive = scan_for_new_and_modified_files(source_dir, processed_files)
    
    if not files_to_archive:
        print("No new or modified files to archive.")
        sys.exit(0)
    
    print(f"Found {len(files_to_archive)} new or modified files to archive.")

    # Create archive
    success = create_archive(
        files_to_archive,
        source_dir,
        destination_dir,
        seven_zip_exec,
        password,
        volume_size
    )

    if success:
        print("Archive created successfully.")
    else:
        print("Archive creation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
