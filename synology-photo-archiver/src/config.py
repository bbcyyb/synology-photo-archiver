import configparser
import sys


def load_config(config_path='config.ini'):
    """
    Loads the configuration from the specified INI file.
    
    Args:
        config_path: Path to the configuration file (default: 'config.ini')
        
    Returns:
        ConfigParser object with loaded configuration
        
    Raises:
        SystemExit: If configuration file is not found
    """
    config = configparser.ConfigParser()
    if not config.read(config_path):
        print(f"Error: Configuration file not found at '{config_path}'")
        sys.exit(1)
    return config
