import json
from pathlib import Path


def load_state(state_file_path):
    """
    Loads the state from the JSON file.
    
    Args:
        state_file_path: Path to the state file
        
    Returns:
        Dictionary containing the state, or empty dict if file doesn't exist
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
    
    Args:
        state_file_path: Path to the state file
        state: Dictionary containing the state to save
    """
    state_file = Path(state_file_path)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
