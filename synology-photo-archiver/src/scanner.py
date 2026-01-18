import sys
from pathlib import Path


def scan_for_new_and_modified_files(source_dir, processed_files):
    """
    Scans the source directory and returns a list of new or modified files.
    
    Args:
        source_dir: Path to the source directory to scan
        processed_files: Dictionary mapping relative file paths to their last processed mtime
        
    Returns:
        List of Path objects for files that are new or have been modified
        
    Raises:
        SystemExit: If source directory is not found or is not a directory
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
