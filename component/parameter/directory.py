from pathlib import Path

base_dir = Path('~', 'module_results').expanduser()
root_dir = base_dir/'Planet_fire_explorer'
data_dir = root_dir/'data'
HISTORIC_DIR = root_dir/'historical'

base_dir.mkdir(exist_ok=True)
root_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)
HISTORIC_DIR.mkdir(parents=True, exist_ok=True)