from pathlib import Path
import pandas as pd
import yaml


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FOLDER = BASE_DIR / "dataset" / "ipl"
PROCESSED_FOLDER = BASE_DIR / "dataset" / "processed"

MATCHES_FILE = PROCESSED_FOLDER / "matches.parquet"
DELIVERIES_FILE = PROCESSED_FOLDER / "deliveries.parquet"


def load_ipl_data():

    """
    Load previously processed IPL match and delivery data.
    """

    if not MATCHES_FILE.exists():
        raise FileNotFoundError(
            "Matches Parquet file not found. "
            "Please run the main application first."
        )

    if not DELIVERIES_FILE.exists():
        raise FileNotFoundError(
            "Deliveries Parquet file not found. "
            "Please run the main application first."
        )

    matches = pd.read_parquet(MATCHES_FILE)

    deliveries = pd.read_parquet(DELIVERIES_FILE)

    return matches, deliveries


def get_dataset_info():

    """
    Return basic information about the IPL dataset.
    """

    yaml_files = list(DATA_FOLDER.glob("*.yaml"))

    yaml_files += list(DATA_FOLDER.glob("*.yml"))

    return {
        "total_yaml_files": len(yaml_files),
        "matches_file": MATCHES_FILE.exists(),
        "deliveries_file": DELIVERIES_FILE.exists()
    }


def load_single_match(file_name):

    """
    Read an individual IPL YAML match file.
    """

    file_path = DATA_FOLDER / file_name

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

    with open(file_path, "r", encoding="utf-8") as file:

        match_data = yaml.load(file, Loader=loader)

    return match_data