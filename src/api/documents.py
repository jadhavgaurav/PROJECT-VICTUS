"""
Document upload and management endpoints
"""

import os
import shutil
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Request, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..tools import update_vector_store, FAISS_INDEX_PATH
from ..utils.logging import get_logger
from ..auth.dependencies import get_optional_user
from .schemas import DocumentsResponse, DocumentItem, DocumentStatusResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user = Depends(get_optional_user)
):
    """Upload a document for RAG processing."""
    if not (file.filename and (file.filename.endswith(".pdf") or file.filename.endswith(".docx"))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a PDF or DOCX."
        )
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process in background
        background_tasks.add_task(update_vector_store, file_path)
        logger.info(f"File uploaded: {file.filename}")

        return {
            "status": "success",
            "filename": file.filename,
            "detail": "File received and is being processed in the background."
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file"
        )


@router.get("/documents", response_model=DocumentsResponse)
async def get_documents(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get list of all uploaded documents.
    """
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            return DocumentsResponse(documents=[], total=0, total_size=0)
        
        # Get all files in uploads directory
        files = []
        total_size = 0
        
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            
            # Only include PDF and DOCX files
            if not (filename.endswith(".pdf") or filename.endswith(".docx")):
                continue
            
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                total_size += file_size
                
                # Check if indexed (file exists in FAISS index)
                indexed = False
                if os.path.exists(FAISS_INDEX_PATH):
                    # Simple check: if FAISS index exists and has content, assume indexed
                    # In production, you might want a more sophisticated check
                    indexed = len(os.listdir(FAISS_INDEX_PATH)) > 0 if os.path.isdir(FAISS_INDEX_PATH) else False
                
                files.append(DocumentItem(
                    filename=filename,
                    size=file_size,
                    upload_date=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    status="ready" if indexed else "processing",
                    indexed=indexed
                ))
        
        # Sort by upload date (newest first)
        files.sort(key=lambda x: x.upload_date, reverse=True)
        
        return DocumentsResponse(
            documents=files,
            total=len(files),
            total_size=total_size
        )
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents"
        )


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Delete a document.
    """
    try:
        # Security: prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        upload_dir = "uploads"
        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file
        os.remove(file_path)
        logger.info(f"Deleted document: {filename}")
        
        # Note: The document will remain in FAISS index until re-indexing
        # In production, you might want to remove it from the index as well
        
        return {"status": "success", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )


@router.get("/documents/status", response_model=DocumentStatusResponse)
async def get_document_status(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get document processing status.
    """
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            return DocumentStatusResponse(total=0, indexed=0, processing=0, failed=0)
        
        total = 0
        indexed = 0
        processing = 0
        
        for filename in os.listdir(upload_dir):
            if filename.endswith(".pdf") or filename.endswith(".docx"):
                total += 1
                # Check if indexed
                if os.path.exists(FAISS_INDEX_PATH) and os.path.isdir(FAISS_INDEX_PATH):
                    if len(os.listdir(FAISS_INDEX_PATH)) > 0:
                        indexed += 1
                    else:
                        processing += 1
                else:
                    processing += 1
        
        return DocumentStatusResponse(
            total=total,
            indexed=indexed,
            processing=processing,
            failed=0  # We don't track failures currently
        )
    except Exception as e:
        logger.error(f"Error getting document status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving document status"
        )

