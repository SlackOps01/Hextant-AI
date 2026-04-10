from app.domains.artifacts.models import Artifact, ArtifactType
from mypy_boto3_s3 import S3Client
from sqlalchemy.orm import Session
import boto3
from uuid import uuid7
from app.core.config import CONFIG

class ArtifactNotFoundException(Exception):
    def __init__(self, artifact_id: str):
        self.artifact_id = artifact_id
        super().__init__(f"Artifact with ID {artifact_id} not found")



s3: S3Client = boto3.client(
    "s3",
    aws_access_key_id=CONFIG.S3_ACCESS_KEY_ID,
    aws_secret_access_key=CONFIG.S3_SECRET_ACCESS_KEY,
    endpoint_url=CONFIG.S3_ENDPOINT_URL,
)

class ArtifactService:
    @staticmethod
    def upload_artifact(db: Session, artifact_type: ArtifactType, content: bytes, user_id: str, message_id: str):
        s3_key = f"{user_id}/{uuid7()}_{artifact_type.value}"
        s3.put_object(Bucket=CONFIG.S3_BUCKET_NAME, Key=s3_key, Body=content)
        # 3. Create a default name for the AI-generated artifact
        default_name = f"Generated {artifact_type.value.capitalize()}"
        new_artifact = Artifact(
            s3_key=s3_key,
            type=artifact_type,     # Matches SQL: %(type)s
            owner_id=user_id,       # Matches SQL: %(owner_id)s
            name=default_name,      # <-- THE FIX: No longer null
            file_size_bytes=len(content), # Optional, but good since it's in your DB!
            message_id=message_id
        )
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)
        return new_artifact

    @staticmethod
    def generate_artifact_url(db: Session, artifact_id: str, user_id: str):
        artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            raise ArtifactNotFoundException(artifact_id)
        if artifact.owner_id != user_id:
            raise Exception("You do not have permission to access this artifact")

        return s3.generate_presigned_url("get_object", Params={"Bucket": CONFIG.S3_BUCKET_NAME, "Key": artifact.s3_key}, ExpiresIn=3600)
            
        
