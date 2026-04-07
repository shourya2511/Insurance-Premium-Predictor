from app.main import app
from app.schemas.prediction import UserInput
from app.services.model_service import get_prediction_model as _get_prediction_model

model = _get_prediction_model()
