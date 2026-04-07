import pickle

from app.core.paths import MODEL_PATH

_prediction_model = None
_model_load_error = None


def get_prediction_model():
    global _prediction_model, _model_load_error

    if _prediction_model is not None:
        return _prediction_model

    if _model_load_error is not None:
        raise RuntimeError(_model_load_error)

    try:
        with MODEL_PATH.open("rb") as model_file:
            _prediction_model = pickle.load(model_file)
        return _prediction_model
    except Exception as exc:
        _model_load_error = str(exc)
        raise RuntimeError(_model_load_error) from exc


def warm_up_prediction_model() -> None:
    try:
        get_prediction_model()
    except RuntimeError:
        pass
