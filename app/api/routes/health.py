from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def hello():
    return {"message": "Patient Management System API"}
