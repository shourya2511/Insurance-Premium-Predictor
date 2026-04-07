from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

# --- Models ---

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='id of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='name of the patient')]
    city: Annotated[str, Field(..., description='city where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='height of the patient in metres')]
    weight: Annotated[float, Field(..., gt=0, description='weight of the patient in kgs')]

    @computed_field
    @property # Required for computed_field in Pydantic v2
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property # Required for computed_field in Pydantic v2
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "underweight"
        elif self.bmi < 25: # Standard healthy range is up to 25
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    # Fixed typo: 'feild' -> 'field' and 'gender' Literal options
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)
    gender: Optional[Literal['male', 'female', 'others']] = None
    height: Optional[float] = Field(default=None, gt=0)
    weight: Optional[float] = Field(default=None, gt=0)

# --- Helper Functions ---

def load_data():
    try:
        with open('patients.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} # Return empty dict if file doesn't exist

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)

# --- Routes ---

@app.get("/")
def hello():
    return {'message': 'Patient Management System API'}

@app.get('/view')
def view():
    return load_data()

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in DB', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'),
    order: str = Query('asc', description='sort in ascending or descending order')
):
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field. Select from {valid_fields}')
    
    data = load_data()
    sort_order = (order == 'desc')

    # Use .get(sort_by, 0) to handle missing fields gracefully
    sorted_list = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    return sorted_list

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    # 1. Get existing data and update with new values
    current_patient_dict = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)
    current_patient_dict.update(update_data)

    # 2. Re-validate through Patient model to trigger @computed_field updates
    # We add the ID back in because the Patient model expects it
    current_patient_dict['id'] = patient_id
    updated_obj = Patient(**current_patient_dict)

    # 3. Save the full object back to the JSON (including new BMI/Verdict)
    data[patient_id] = updated_obj.model_dump()
    save_data(data)

    return {"message": "Patient updated successfully", "patient": data[patient_id]}

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]
    save_data(data)
    return {'message': 'Patient deleted'}