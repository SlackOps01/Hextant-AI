from app.domains.llm_models.service import LanguageModelService
from fastapi import APIRouter, status, Depends
from app.domains.llm_models.schemas import LanguageModelCreate, LanguageModelResponse, LanguageModelUpdate
from app.domains.users.security import require_admin
from app.core.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/llm-models",   
    tags=["LLM Models"]
)


@router.post("/", response_model=LanguageModelResponse, status_code=status.HTTP_201_CREATED)
def add_language_model(language_model: LanguageModelCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return LanguageModelService.add_language_model(db, language_model)

@router.get("/", response_model=list[LanguageModelResponse], status_code=status.HTTP_200_OK)
def list_language_models(db: Session = Depends(get_db)):
    return LanguageModelService.list_language_models(db)

@router.patch("/{model_id}", response_model=LanguageModelResponse, status_code=status.HTTP_202_ACCEPTED)
def update_language_model(model_id: str, language_model: LanguageModelUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    return LanguageModelService.update_language_model(db, model_id, language_model)

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_language_model(model_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    LanguageModelService.delete_language_model(db, model_id)
    return