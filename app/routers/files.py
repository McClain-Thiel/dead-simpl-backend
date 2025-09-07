import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from ..dependencies import DBSessionDependency, get_current_user
from ..db.models import User
from ..schemas.upload import Upload as UploadSchema, UploadCreate
from ..db import crud
from ..gcs import generate_signed_url, upload_file_to_gcs
from ..db.models import UploadTask

router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/generate-signed-url")
def get_signed_url_for_upload(
    user: User = Depends(get_current_user),
    task: UploadTask = Form(...), 
    filename: str = Form(...), 
    content_type: str = Form(...)
):
    """Get a signed URL to upload a file to GCS."""
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="GCS_BUCKET_NAME is not configured")
        
    file_id = str(uuid.uuid4())
    destination_blob_name = f"{user.id}/{task.value}/{file_id}/{filename}"
    
    signed_url = generate_signed_url(bucket_name, destination_blob_name, content_type)
    
    return {
        "signed_url": signed_url,
        "storage_url": f"gs://{bucket_name}/{destination_blob_name}"
    }

@router.post("/upload", response_model=UploadSchema)
async def upload_file(
    db: DBSessionDependency,
    user: User = Depends(get_current_user),
    task: UploadTask = Form(...), 
    file: UploadFile = File(...)
):
    """Upload a file and create an upload record."""
    file_id = str(uuid.uuid4())
    destination_blob_name = f"{user.id}/{task.value}/{file_id}/{file.filename}"
    
    # Save the file locally first
    with open(file.filename, "wb") as buffer:
        buffer.write(await file.read())
        
    storage_url = upload_file_to_gcs(file.filename, destination_blob_name)
    
    # Clean up local file
    os.remove(file.filename)
    
    upload_data = UploadCreate(
        task=task,
        storage_url=storage_url,
        filename=file.filename,
        size=file.size,
        content_type=file.content_type
    )
    
    return crud.create_upload(db=db, upload=upload_data, user_id=user.id)

@router.get("/", response_model=List[UploadSchema])
def read_uploads(db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Retrieve uploads for the current user."""
    return crud.get_uploads_by_user(db=db, user_id=user.id)

@router.delete("/{upload_id}", response_model=UploadSchema)
def delete_upload(upload_id: uuid.UUID, db: DBSessionDependency, user: User = Depends(get_current_user)):
    """Delete an upload."""
    db_upload = crud.delete_upload(db=db, upload_id=upload_id, user_id=user.id)
    if db_upload is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return db_upload 