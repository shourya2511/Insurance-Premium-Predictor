from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json
import pandas as pd
import pickle

app = FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

model_load_error = None
prediction_model = None

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


class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the user')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the user')]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description='Height of the user')]
    income_lpa: Annotated[float, Field(..., gt=0, description='Annual salary of the user in lpa')]
    smoker: Annotated[bool, Field(..., description='Is user a smoker')]
    city: Annotated[str, Field(..., description='The city that the user belongs to')]
    occupation: Annotated[
        Literal['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job'],
        Field(..., description='Occupation of the user')
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        if self.smoker or self.bmi > 27:
            return "medium"
        return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        if self.age < 45:
            return "adult"
        if self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        if self.city in tier_2_cities:
            return 2
        return 3

# --- Helper Functions ---

def get_prediction_model():
    global prediction_model, model_load_error

    if prediction_model is not None:
        return prediction_model

    if model_load_error is not None:
        raise RuntimeError(model_load_error)

    try:
        with open('model.pkl', 'rb') as f:
            prediction_model = pickle.load(f)
        return prediction_model
    except Exception as exc:
        model_load_error = str(exc)
        raise RuntimeError(model_load_error) from exc


@app.on_event("startup")
def preload_prediction_model():
    try:
        get_prediction_model()
    except RuntimeError:
        # Keep the API process running so the frontend gets a clear JSON error
        # from /predict instead of a server that never comes up cleanly.
        pass

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

@app.post('/predict')
def predict_premium(data: UserInput):
    try:
        model = get_prediction_model()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction model could not be loaded. "
                f"Original error: {exc}. "
                "Please install the scikit-learn version used to train the model."
            ),
        ) from exc

    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])

    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={'predicted_category': prediction})

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
