import boto3
from mypy_boto3_s3 import S3Client
from fastapi import UploadFile


class AttachmentService:
    @staticmethod
    def upload_file(file: UploadFile):
        s3: S3Client = boto3.client("s3")
        s3.upload_file(file.file, "bucket", file.filename)
        