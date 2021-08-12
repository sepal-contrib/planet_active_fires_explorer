from pathlib import Path

base_dir = Path('~', 'module_results').expanduser()
root_dir = base_dir/'sepafe'

data_dir = root_dir/'data'
HISTORIC_DIR = root_dir/'historical'
ALERTS_DIR = root_dir/'alerts'

base_dir.mkdir(exist_ok=True)
root_dir.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)
HISTORIC_DIR.mkdir(parents=True, exist_ok=True)
ALERTS_DIR.mkdir(parents=True, exist_ok=True)