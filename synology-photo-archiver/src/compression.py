import datetime
import subprocess
import sys
from pathlib import Path


def create_archive(files_to_archive, source_dir, destination_dir, seven_zip_exec, password, volume_size):
    """
    Creates a 7z archive with the given files.
    
    Args:
        files_to_archive: List of Path objects to include in the archive
        source_dir: Source directory path (for reference)
        destination_dir: Directory where the archive will be created
        seven_zip_exec: Path to the 7z executable
        password: Password for the archive
        volume_size: Volume size for splitting the archive
        
    Returns:
        bool: True if archive creation was successful, False otherwise
        
    Raises:
        SystemExit: If 7z executable is not found
    """
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
        file_list_path.unlink()  # Clean up the temporary file list
        return True
    except subprocess.CalledProcessError as e:
        print("Error during 7z compression.")
        print(f"Command: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error Output: {e.stderr}")
        file_list_path.unlink()  # Clean up the temporary file list
        return False
    except FileNotFoundError:
        print(f"Error: 7z executable not found at '{seven_zip_exec}'. Please check your config.ini.")
        sys.exit(1)
