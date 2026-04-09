from sqlalchemy.orm import Session
import boto3
from mypy_boto3_s3 import S3Client
from fastapi import UploadFile
from uuid import uuid7
from app.core.config import CONFIG
from app.domains.attachments.models import Attachments
from fastapi import HTTPException, status

class AttachmentNotFoundException(HTTPException):
    def __init__(self, attachment_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Attachment with id {attachment_id} not found")

class AttachmentPermissionsException(HTTPException):
    def __init__(self, attachment_id: str, user_id: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=f"User {user_id} is not authorized to access attachment {attachment_id}")


s3: S3Client = boto3.client("s3",
    endpoint_url=CONFIG.S3_ENDPOINT_URL,
    aws_access_key_id=CONFIG.S3_ACCESS_KEY_ID,
    aws_secret_access_key=CONFIG.S3_SECRET_ACCESS_KEY
)

class AttachmentService:
    @staticmethod
    def upload_file(file: UploadFile, db: Session, user_id: str):
        file_key = f"{user_id}/{uuid7()}_{file.filename}"
        s3.upload_fileobj(file.file, CONFIG.S3_BUCKET_NAME, file_key)

        new_attachment = Attachments(
            s3_key=file_key,
            file_name=file.filename,
            file_size_bytes=file.size,
            mime_type=file.content_type,
            user_id=user_id
        )
        db.add(new_attachment)
        db.commit()
        db.refresh(new_attachment)
        return new_attachment

    @staticmethod
    def generate_download_url(db: Session, attachment_id: str, user_id: str):
        attachment = db.query(Attachments).filter(Attachments.id == attachment_id).first()
        if not attachment:
            raise AttachmentNotFoundException(attachment_id)

        if attachment.user_id != user_id:
            raise AttachmentPermissionsException(attachment_id, user_id)

        s3_key = attachment.s3_key
        
        return s3.generate_presigned_url("get_object", Params={"Bucket": CONFIG.S3_BUCKET_NAME, "Key": s3_key}, ExpiresIn=3600)

    @staticmethod
    def list_attachments(db: Session, user_id: str):
        return db.query(Attachments).filter(Attachments.user_id == user_id).all()