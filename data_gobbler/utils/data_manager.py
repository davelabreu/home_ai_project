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
    def ensure_project_path(project_id: str) -> Path:
        """Ensures the directory for a specific project exists."""
        project_path = DATA_ROOT / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    @staticmethod
    def list_files(project_id: str):
        """Returns a list of CSV files for a project, sorted by newest first."""
        path = DATA_ROOT / project_id
        if not path.exists():
            return []
        
        files = [f.name for f in path.glob("*.csv")]
        # Sort by filename which includes our YYYY-MM-DD format
        return sorted(files, reverse=True)

    @staticmethod
    def save_dataframe(df: pd.DataFrame, project_id: str, prefix: str = "ingest"):
        """Saves a DataFrame to the project silo with a readable timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{prefix}_{timestamp}.csv"
        
        project_path = DataManager.ensure_project_path(project_id)
        save_path = project_path / filename
        
        df.to_csv(save_path, index=False)
        return filename

    @staticmethod
    def load_dataframe(project_id: str, filename: str) -> pd.DataFrame:
        """Reads a CSV file from a project silo into a pandas DataFrame."""
        file_path = DATA_ROOT / project_id / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        return pd.read_csv(file_path)

    @staticmethod
    def get_latest_dataframe(project_id: str):
        """Helper to get the most recently ingested data for a project."""
        files = DataManager.list_files(project_id)
        if not files:
            return None, None
        
        latest_file = files[0]
        return DataManager.load_dataframe(project_id, latest_file), latest_file
