from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.patients import router as patients_router
from app.api.routes.prediction import router as prediction_router
from app.services.model_service import warm_up_prediction_model


def create_app() -> FastAPI:
    application = FastAPI(title="Insurance and Patient API")
    application.include_router(health_router)
    application.include_router(prediction_router)
    application.include_router(patients_router)

    @application.on_event("startup")
    def preload_prediction_model():
        warm_up_prediction_model()

    return application


app = create_app()
