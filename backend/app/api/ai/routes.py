from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.ai.service import generate_text
from app.database.session import get_db


class AIRequest(BaseModel):
    prompt: str


class AIResponse(BaseModel):
    result: str

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/complete",
    response_model=AIResponse,
    status_code=status.HTTP_200_OK,
)
def complete_text(
    request: AIRequest,
    db: Session = Depends(get_db),
):
    try:
        result = generate_text(request.prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    return AIResponse(result=result)
