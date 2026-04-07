from fastapi import APIRouter, HTTPException, Path, Query

from app.schemas.patient import Patient, PatientUpdate
from app.services.patient_store import load_data, save_data

router = APIRouter()


@router.get("/view")
def view():
    return load_data()


@router.get("/patient/{patient_id}")
def view_patient(
    patient_id: str = Path(..., description="ID of the patient in DB", examples=["P001"])
):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@router.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"),
    order: str = Query("asc", description="sort in ascending or descending order"),
):
    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid field. Select from {valid_fields}"
        )

    data = load_data()
    sort_order = order == "desc"
    return sorted(data.values(), key=lambda value: value.get(sort_by, 0), reverse=sort_order)


@router.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    current_patient_dict = data[patient_id]
    update_data = patient_update.model_dump(exclude_unset=True)
    current_patient_dict.update(update_data)
    current_patient_dict["id"] = patient_id

    updated_obj = Patient(**current_patient_dict)
    data[patient_id] = updated_obj.model_dump()
    save_data(data)

    return {"message": "Patient updated successfully", "patient": data[patient_id]}


@router.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    del data[patient_id]
    save_data(data)
    return {"message": "Patient deleted"}
