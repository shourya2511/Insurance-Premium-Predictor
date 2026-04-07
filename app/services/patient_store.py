import json

from app.core.paths import PATIENTS_DATA_PATH


def load_data():
    try:
        with PATIENTS_DATA_PATH.open("r", encoding="utf-8") as patient_file:
            return json.load(patient_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data) -> None:
    with PATIENTS_DATA_PATH.open("w", encoding="utf-8") as patient_file:
        json.dump(data, patient_file, indent=4)
