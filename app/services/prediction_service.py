import pandas as pd

from app.schemas.prediction import UserInput
from app.services.model_service import get_prediction_model


def build_prediction_frame(data: UserInput) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "bmi": data.bmi,
                "age_group": data.age_group,
                "lifestyle_risk": data.lifestyle_risk,
                "city_tier": data.city_tier,
                "income_lpa": data.income_lpa,
                "occupation": data.occupation,
            }
        ]
    )


def predict_premium_category(data: UserInput):
    model = get_prediction_model()
    input_df = build_prediction_frame(data)
    return model.predict(input_df)[0]
