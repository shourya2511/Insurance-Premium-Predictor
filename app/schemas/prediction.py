from typing import Annotated, Literal

from pydantic import BaseModel, Field, computed_field

from app.domain.cities import TIER_1_CITIES, TIER_2_CITIES


class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the user")]
    height: Annotated[
        float, Field(..., gt=0, lt=2.5, description="Height of the user")
    ]
    income_lpa: Annotated[
        float, Field(..., gt=0, description="Annual salary of the user in lpa")
    ]
    smoker: Annotated[bool, Field(..., description="Is user a smoker")]
    city: Annotated[
        str, Field(..., description="The city that the user belongs to")
    ]
    occupation: Annotated[
        Literal[
            "retired",
            "freelancer",
            "student",
            "government_job",
            "business_owner",
            "unemployed",
            "private_job",
        ],
        Field(..., description="Occupation of the user"),
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height**2)

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
        if self.city in TIER_1_CITIES:
            return 1
        if self.city in TIER_2_CITIES:
            return 2
        return 3
