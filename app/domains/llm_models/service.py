from fastapi import HTTPException, status
from app.domains.llm_models.models import LanguageModels
from app.domains.llm_models.schemas import LanguageModelCreate, LanguageModelResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


LanguageModelConflictException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Language model with this api_identifier already exists",
)


class LanguageModelService:
    @staticmethod
    def add_language_model(
        db: Session, language_model: LanguageModelCreate
    ) -> LanguageModelResponse:
        db_language_model = LanguageModels(**language_model.model_dump())
        db.add(db_language_model)
        try:
            db.commit()
            db.refresh(db_language_model)
        except IntegrityError:
            db.rollback()
            raise LanguageModelConflictException
        return LanguageModelResponse.model_validate(db_language_model)
