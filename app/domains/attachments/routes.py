from fastapi import APIRouter, Depends, status, File, UploadFile
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db
from app.core.oauth2 import TokenData
from app.domains.attachments.service import AttachmentService
from app.domains.attachments.schemas import AttachmentResponse, PresignedUrlResponse
from typing import List

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
def upload_attachment(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AttachmentService.upload_file(
        db=db,
        file=file,
        user_id=current_user.id,
    )


@router.get("/{attachment_id}/download", response_model=PresignedUrlResponse)
def get_download_url(
    attachment_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = AttachmentService.generate_download_url(
        db=db,
        attachment_id=attachment_id,
        user_id=current_user.id,
    )
    return PresignedUrlResponse(url=url)

@router.get("/", response_model=List[AttachmentResponse])
def list_attachments(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    return AttachmentService.list_attachments(
        db=db,
        user_id=current_user.id,
    )