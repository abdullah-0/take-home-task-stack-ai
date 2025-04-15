from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.core.v_db import VectorDB
from app.schemas.document import Document, DocumentCreate, DocumentUpdate

router = APIRouter()
db = VectorDB()


@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
def create_document(doc: DocumentCreate):
    if not db.library_exists(doc.library_id):
        raise HTTPException(status_code=404, detail="Library not found")
    document_id = db.create_document(doc.library_id, doc.title, doc.metadata)
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=500, detail="Document creation failed")
    return document


@router.get("/", response_model=List[Document])
def list_documents():
    return db.get_all_documents()


@router.get("/{document_id}", response_model=Document)
def get_document(document_id: str = Path(..., description="The ID of the document")):
    doc = db.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/{document_id}", response_model=Document)
def update_document(document_id: str, doc_update: DocumentUpdate):
    if not db.document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    db.update_document(document_id, doc_update.title, doc_update.metadata)
    return db.get_document(document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str):
    if not db.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
