from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, computed_field


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="id of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="name of the patient")]
    city: Annotated[str, Field(..., description="city where the patient is living")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of patient")]
    gender: Annotated[
        Literal["male", "female", "others"],
        Field(..., description="gender of the patient"),
    ]
    height: Annotated[
        float,
        Field(..., gt=0, description="height of the patient in metres"),
    ]
    weight: Annotated[
        float,
        Field(..., gt=0, description="weight of the patient in kgs"),
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "underweight"
        if self.bmi < 25:
            return "Normal"
        if self.bmi < 30:
            return "Overweight"
        return "Obese"


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)
    gender: Optional[Literal["male", "female", "others"]] = None
    height: Optional[float] = Field(default=None, gt=0)
    weight: Optional[float] = Field(default=None, gt=0)
