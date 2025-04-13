
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from app.core.v_db import VectorDB
from app.schemas import Document, DocumentCreate, DocumentUpdate
from app.utils import get_db

router = APIRouter(
)


@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
        library_id: str = Path(..., description="The ID of the parent library"),
        document: DocumentCreate = ...,
        db: VectorDB = Depends(get_db)
):
    """
    Create a new document within a library
    """
    if not db.library_exists(library_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )

    doc_id = db.create_document(
        library_id=library_id,
        title=document.title,
        metadata=document.metadata or {}
    )
    return db.get_document(doc_id)


@router.get("/", response_model=List[Document])
async def list_documents(
        library_id: str = Path(..., description="The ID of the parent library"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: VectorDB = Depends(get_db)
):
    """
    List all documents in a library with pagination
    """
    if not db.library_exists(library_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )

    return db.get_documents_in_library(
        library_id=library_id,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=Document)
async def get_document(
        library_id: str = Path(..., description="The ID of the parent library"),
        document_id: str = Path(..., description="The ID of the document"),
        db: VectorDB = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document = db.get_document(document_id)
    if not document or document["library_id"] != library_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in specified library"
        )
    return document


@router.put("/{document_id}", response_model=Document)
async def update_document(
        library_id: str = Path(..., description="The ID of the parent library"),
        document_id: str = Path(..., description="The ID of the document"),
        document_update: DocumentUpdate = ...,
        db: VectorDB = Depends(get_db)
):
    """
    Update a document's metadata
    """
    if not db.document_exists(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    current_doc = db.get_document(document_id)
    if current_doc["library_id"] != library_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document does not belong to specified library"
        )

    success = db.update_document(
        document_id=document_id,
        title=document_update.title,
        metadata=document_update.metadata
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )

    return db.get_document(document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
        library_id: str = Path(..., description="The ID of the parent library"),
        document_id: str = Path(..., description="The ID of the document"),
        db: VectorDB = Depends(get_db)
):
    """
    Delete a document and all its chunks
    """
    document = db.get_document(document_id)
    if not document or document["library_id"] != library_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in specified library"
        )

    if not db.delete_document(document_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )