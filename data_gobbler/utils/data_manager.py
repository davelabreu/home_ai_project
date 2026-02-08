import os
import json
import pandas as pd
import datetime
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).parent.parent
PROJECTS_JSON = BASE_DIR / "projects.json"
DATA_ROOT = BASE_DIR / "projects"

class DataManager:
    """
    The Data Manager handles all filesystem and data ingestion logic.
    It ensures project silos are maintained and data is cleanly loaded.
    """
    
    @staticmethod
    def get_projects():
        """Loads and returns the project registry."""
        if not PROJECTS_JSON.exists():
            return {}
        with open(PROJECTS_JSON, "r") as f:
            return json.load(f)

    @staticmethod
    def list_subsystems(project_id: str):
        """Lists subdirectories (subsystems) in a project."""
        path = DATA_ROOT / project_id
        if not path.exists():
            return []
        return sorted([d.name for d in path.iterdir() if d.is_dir()])

    @staticmethod
    def list_tests(project_id: str, subsystem: str):
        """Lists subdirectories (tests) in a subsystem."""
        path = DATA_ROOT / project_id / subsystem
        if not path.exists():
            return []
        return sorted([d.name for d in path.iterdir() if d.is_dir()])

    @staticmethod
    def list_files(project_id: str, subsystem: str = None, test: str = None):
        """Returns a list of CSV files, supporting nested paths."""
        path = DATA_ROOT / project_id
        if subsystem:
            path = path / subsystem
        if test:
            path = path / test
            
        if not path.exists():
            return []
        
        files = [f.name for f in path.glob("*.csv")]
        return sorted(files, reverse=True)

    @staticmethod
    def ensure_path(project_id: str, subsystem: str = "general", test: str = "quick_dump") -> Path:
        """Ensures a nested directory path exists."""
        path = DATA_ROOT / project_id / subsystem / test
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def save_dataframe(df: pd.DataFrame, project_id: str, subsystem: str = "general", test: str = "quick_dump", prefix: str = "ingest"):
        """Saves a DataFrame to a nested project silo with a readable timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{prefix}_{timestamp}.csv"
        
        save_dir = DataManager.ensure_path(project_id, subsystem, test)
        save_path = save_dir / filename
        
        df.to_csv(save_path, index=False)
        return filename

    @staticmethod
    def load_dataframe(project_id: str, subsystem: str, test: str, filename: str) -> pd.DataFrame:
        """Reads a CSV file from a nested path into a pandas DataFrame."""
        file_path = DATA_ROOT / project_id / subsystem / test / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        return pd.read_csv(file_path)

    @staticmethod
    def get_latest_dataframe(project_id: str):
        """Helper to get the most recently ingested data for a project (Legacy support)."""
        files = DataManager.list_files(project_id)
        if not files:
            return None, None
        
        latest_file = files[0]
        # Legacy load (flat structure)
        file_path = DATA_ROOT / project_id / latest_file
        return pd.read_csv(file_path), latest_file
