from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.prediction import UserInput
from app.services.prediction_service import predict_premium_category

router = APIRouter()


@router.post("/predict")
def predict_premium(data: UserInput):
    try:
        prediction = predict_premium_category(data)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction model could not be loaded. "
                f"Original error: {exc}. "
                "Please install the scikit-learn version used to train the model."
            ),
        ) from exc

    return JSONResponse(status_code=200, content={"predicted_category": prediction})
