import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from config.settings import RAW_DATA_DIR, CSV_FILES


class BronzeExtractor:
    # extraction brute des CSV dans le dossier raw

    def __init__(self, data_dir: Path = RAW_DATA_DIR):
        self.data_dir = data_dir

    def extract(self, dataset_name: str, nrows: Optional[int] = None) -> pd.DataFrame:
        # charge un CSV par nom de dataset
        file_name = CSV_FILES.get(dataset_name)
        if not file_name:
            raise ValueError(f"Dataset inconnu: {dataset_name}")

        file_path = self.data_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {file_path}")

        return pd.read_csv(file_path, encoding='utf-8', low_memory=False, nrows=nrows)

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        # charge tous les CSV configurés dans settings
        return {name: self.extract(name) for name in CSV_FILES.keys()}