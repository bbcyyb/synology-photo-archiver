# Synology Photo Archiver

A Python script to automatically find new and modified photos in a directory, package them into encrypted, split 7z archives, and move them to a destination directory. This script is designed to be run as a scheduled task on a Synology NAS.

## Features

- **Idempotent**: The script keeps track of processed files and will only archive new or modified files.
- **Configurable**: All paths, the archive password, and volume sizes can be set in a configuration file.
- **Secure**: Creates password-protected 7z archives.
- **Split Archives**: Splits large archives into smaller volumes for easier management.

## Prerequisites

1.  **Python 3**: Your Synology NAS must have Python 3 installed. You can install it from the Package Center.
2.  **7-Zip**: The `7z` command-line tool must be installed. You may need to install it via the Synology community package source or by other means.

## Setup

1.  **Copy Files**: Copy the `synology-photo-archiver` directory to a location on your Synology NAS (e.g., `/volume1/scripts/`).
2.  **Create `config.ini`**:
    -   Navigate to the `synology-photo-archiver` directory.
    -   Make a copy of `config.ini.template` and name it `config.ini`.
    -   Edit `config.ini` with your desired settings:
        ```ini
        [Paths]
        ; The directory where your original photos are stored.
        source_dir = /volume1/photo
        
        ; The directory where the 7z archives will be saved.
        destination_dir = /volume1/backups/photo_archives
        
        ; The full path to the 7z executable. Find it using 'which 7z' or 'find / -name 7z'.
        7z_executable = /usr/local/bin/7z

        [Archive]
        ; The password for your encrypted archives. Use a strong password.
        password = YOUR_SECRET_PASSWORD
        
        ; The size for each split volume (e.g., 1g = 1 GB, 500m = 500 MB).
        volume_size = 1g

        [State]
        ; The file to store the state of processed files.
        ; It's recommended to place this inside the script directory.
        file = /volume1/scripts/synology-photo-archiver/processed_files.json
        ```
3.  **Permissions**: Ensure the user running the script has read access to the `source_dir` and read/write access to the `destination_dir` and the script's directory (for the state file).

## Running the Script Manually

You can run the script manually to test your configuration.

1.  Open an SSH session to your Synology NAS.
2.  Navigate to the script's directory:
    ```bash
    cd /volume1/scripts/synology-photo-archiver
    ```
3.  Run the script:
    ```bash
    python3 archiver.py
    ```
    The script will print its progress to the console.

## Scheduling with Synology Task Scheduler

To run the script automatically, use the Task Scheduler in the Synology Control Panel.

1.  Go to **Control Panel > Task Scheduler**.
2.  Click **Create > Scheduled Task > User-defined script**.
3.  **General Tab**:
    -   **Task**: Give your task a name (e.g., "Photo Archiver").
    -   **User**: Select the user who should run the script (e.g., `root` or an admin user).
4.  **Schedule Tab**:
    -   Set the schedule for how often you want the script to run (e.g., daily at 2:00 AM).
5.  **Task Settings Tab**:
    -   Under **User-defined script**, enter the following command, making sure to adjust the path to your script:
        ```bash
        cd /volume1/scripts/synology-photo-archiver && python3 archiver.py
        ```
    -   It is recommended to also set up output results to a log file for easier debugging. You can do this by checking "Send run details by email" or by redirecting the output in your script command:
        ```bash
        cd /volume1/scripts/synology-photo-archiver && python3 archiver.py >> /volume1/scripts/synology-photo-archiver/archiver.log 2>&1
        ```
6.  Click **OK** to save the task. You can run it manually from the Task Scheduler to test it.
