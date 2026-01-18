import datetime
import subprocess
import sys
from pathlib import Path


def create_archive(files_to_archive, source_dir, destination_dir, seven_zip_exec, password, volume_size):
    """
    Creates a tar.gz archive with the given files.
    
    Args:
        files_to_archive: List of Path objects to include in the archive
        source_dir: Source directory path (for reference)
        destination_dir: Directory where the archive will be created
        seven_zip_exec: Path to the tar executable (repurposed argument)
        password: Password for the archive (Ignored for tar)
        volume_size: Volume size for splitting the archive (Ignored for tar)
        
    Returns:
        bool: True if archive creation was successful, False otherwise
        
    Raises:
        SystemExit: If tar executable is not found
    """
    source_path_obj = Path(source_dir)
    archive_name = f"{source_path_obj.name}.tar.gz"
    archive_path = Path(destination_dir) / archive_name

    # Ensure destination directory exists
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a temporary file list
    # tar -T expects file paths. relative paths are safer if we change cwd, but we can stick to absolute.
    # However, tar might complain about leading '/'. standard tar removes it.
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    file_list_path = Path(f"file_list_{timestamp}.txt")
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for file_path in files_to_archive:
            f.write(str(file_path) + '\n')

    command = [
        seven_zip_exec,
        '-czf',
        str(archive_path),
        '-T',
        str(file_list_path)
    ]

    print(f"Running tar command: {' '.join(command)}")
    if password and password != "YOUR_SECRET_PASSWORD":
        print("Warning: Password protection is not supported with tar.gz in this implementation.")
    
    try:
        # Check if volume splitting is requested
        if volume_size:
            # Parse volume size
            size_str = str(volume_size).lower().strip()
            suffix = size_str[-1]
            if suffix.isdigit():
                 bytes_size = int(size_str)
            else:
                value = int(size_str[:-1])
                if suffix == 'k':
                    bytes_size = value * 1024
                elif suffix == 'm':
                    bytes_size = value * 1024 * 1024
                elif suffix == 'g':
                    bytes_size = value * 1024 * 1024 * 1024
                else:
                    print(f"Warning: Unknown volume size suffix '{suffix}'. Ignoring volume splitting.")
                    bytes_size = 0
            
            if bytes_size > 0:
                print(f"Volume splitting enabled. Size: {bytes_size} bytes.")
                # Use shell pipeline for splitting
                # tar -cz -T list | split -b size - archive_prefix.
                # Note: split prefix should include the full path base
                
                # Archive name is like "source.tar.gz"
                # Split files will be "source.tar.gz.aa", "source.tar.gz.ab", etc.
                split_prefix = str(archive_path) + "."
                
                # We need to use Shell=True for piping, or manually connect streams.
                # Manual formatting of the command string for logging
                tar_cmd_str = f"{seven_zip_exec} -cz -T {file_list_path}"
                split_cmd_str = f"split -b {bytes_size} - {split_prefix}"
                full_cmd_str = f"{tar_cmd_str} | {split_cmd_str}"
                print(f"Running split command: {full_cmd_str}")

                # Using shell=True involves security risks if inputs are untrusted.
                # Here inputs come from config and are relatively trusted paths.
                # Alternative: Use subprocess.Popen to pipe.
                
                # Popen approach (safer):
                p1 = subprocess.Popen([seven_zip_exec, '-cz', '-T', str(file_list_path)], stdout=subprocess.PIPE)
                p2 = subprocess.Popen(['split', '-d', '-b', str(bytes_size), '-', split_prefix], stdin=p1.stdout)
                p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
                output = p2.communicate()
                
                if p2.returncode == 0:
                    print("Compression and splitting successful.")
                    file_list_path.unlink()
                    return True
                else:
                     raise subprocess.CalledProcessError(p2.returncode, "split")

        # Fallback to normal non-split archive if no volume size or parsing failed
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print("Compression successful.")
        print(result.stdout)
        file_list_path.unlink()  # Clean up the temporary file list
        return True
    except subprocess.CalledProcessError as e:
        print("Error during compression.")
        # e.cmd might be None if raised manually
        print(f"Command: {e.cmd}") 
        print(f"Return Code: {e.returncode}")
        # stdout/stderr might be on the process object if using Popen/communicate logic differently,
        # but here 'e' comes mostly from the fallback run or manual raise.
        if hasattr(e, 'stdout'): print(f"Output: {e.stdout}")
        if hasattr(e, 'stderr'): print(f"Error Output: {e.stderr}")
        if file_list_path.exists():
             file_list_path.unlink()
        return False
    except FileNotFoundError:
        print(f"Error: Executable not found at '{seven_zip_exec}'. Please check your config.ini.")
        sys.exit(1)
