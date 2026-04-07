from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "model.pkl"
PATIENTS_DATA_PATH = BASE_DIR / "patients.json"
