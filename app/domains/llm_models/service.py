from fastapi import HTTPException, status
from app.domains.llm_models.models import LanguageModels
from app.domains.llm_models.schemas import LanguageModelCreate, LanguageModelResponse, LanguageModelUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


LanguageModelConflictException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Language model with this api_identifier already exists",
)

LanguageModelNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Language model not found")

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
    
    @staticmethod
    def list_language_models(db: Session) -> list[LanguageModelResponse]:
        language_models = db.query(LanguageModels).all()
        return [LanguageModelResponse.model_validate(lm) for lm in language_models]

    
    @staticmethod
    def update_language_model(db: Session, model_id: str, language_model: LanguageModelUpdate) -> LanguageModelResponse:
        language_model_db = db.query(LanguageModels).filter(LanguageModels.id == model_id).first()
        if not language_model_db:
            raise LanguageModelNotFoundException

        update_data = language_model.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(language_model_db, key, value)
        db.commit()
        db.refresh(language_model_db)
        return LanguageModelResponse.model_validate(language_model_db)
        
    @staticmethod
    def delete_language_model(db: Session, model_id: str) -> None:
        language_model_db = db.query(LanguageModels).filter(LanguageModels.id == model_id).first()
        if not language_model_db:
            raise LanguageModelNotFoundException
        db.delete(language_model_db)
        db.commit()
        return 
        