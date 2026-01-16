import configparser
import json
import sys
from pathlib import Path

def load_config(config_path='config.ini'):
    """
    Loads the configuration from the specified INI file.
    """
    config = configparser.ConfigParser()
    if not config.read(config_path):
        print(f"Error: Configuration file not found at '{config_path}'")
        sys.exit(1)
    return config

def load_state(state_file_path):
    """
    Loads the state from the JSON file.
    Returns an empty dictionary if the file doesn't exist.
    """
    state_file = Path(state_file_path)
    if not state_file.exists():
        return {}
    with open(state_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: State file at '{state_file_path}' is corrupted. Starting from a fresh state.")
            return {}

def save_state(state_file_path, state):
    """
    Saves the state to the JSON file.
    """
    state_file = Path(state_file_path)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def scan_for_new_and_modified_files(source_dir, processed_files):
    """
    Scans the source directory and returns a list of new or modified files.
    """
    to_process = []
    source_path = Path(source_dir)
    
    if not source_path.is_dir():
        print(f"Error: Source directory '{source_dir}' not found or is not a directory.")
        sys.exit(1)

    for file_path in source_path.rglob('*'):
        if file_path.is_file():
            relative_path_str = str(file_path.relative_to(source_path))
            current_mtime = file_path.stat().st_mtime

            if relative_path_str not in processed_files or processed_files[relative_path_str] < current_mtime:
                to_process.append(file_path)
    
    return to_process

def create_archive(files_to_archive, source_dir, destination_dir, seven_zip_exec, password, volume_size):
    """
    Creates a 7z archive with the given files.
    """
    import subprocess
    import datetime

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"archive_{timestamp}.7z"
    archive_path = Path(destination_dir) / archive_name

    # Ensure destination directory exists
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a temporary file list
    file_list_path = Path(f"file_list_{timestamp}.txt")
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for file_path in files_to_archive:
            f.write(str(file_path) + '\n')

    command = [
        seven_zip_exec,
        'a',  # Add to archive
        str(archive_path),
        f"-p{password}",  # Set password
        f"-v{volume_size}",  # Set volume size
        f"@{file_list_path}"  # Read file list from file
    ]

    print(f"Running 7z command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("7z compression successful.")
        print(result.stdout)
        file_list_path.unlink() # Clean up the temporary file list
        return True
    except subprocess.CalledProcessError as e:
        print("Error during 7z compression.")
        print(f"Command: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error Output: {e.stderr}")
        file_list_path.unlink() # Clean up the temporary file list
        return False
    except FileNotFoundError:
        print(f"Error: 7z executable not found at '{seven_zip_exec}'. Please check your config.ini.")
        sys.exit(1)


def main():
    """
    Main function for the archiver.
    """
    config = load_config()
    print("Configuration loaded successfully.")

    # Get config values
    source_dir = config.get('Paths', 'source_dir')
    destination_dir = config.get('Paths', 'destination_dir')
    seven_zip_exec = config.get('Paths', '7z_executable')
    password = config.get('Archive', 'password')
    volume_size = config.get('Archive', 'volume_size')
    state_file_path = config.get('State', 'file')

    print(f"Source directory: {source_dir}")
    print(f"Destination directory: {destination_dir}")

    # Load state
    processed_files = load_state(state_file_path)
    print(f"Loaded state for {len(processed_files)} files.")

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
        print("Archive created successfully. Updating state file.")
        # Update state for successfully archived files
        for file_path in files_to_archive:
            relative_path_str = str(file_path.relative_to(Path(source_dir)))
            processed_files[relative_path_str] = file_path.stat().st_mtime
        
        save_state(state_file_path, processed_files)
        print("State file updated.")
    else:
        print("Archive creation failed. State file will not be updated.")
        sys.exit(1)
    
if __name__ == "__main__":
    main()
