from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.core.v_db import VectorDB
from app.schemas.chunk import Chunk, ChunkCreate, ChunkUpdate

router = APIRouter()
db = VectorDB()


@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
def create_chunk(chunk: ChunkCreate):
    if not db.document_exists(chunk.document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    chunk_id = db.create_chunk(
        document_id=chunk.document_id,
        content=chunk.content,
        embedding=chunk.embedding,
        metadata=chunk.metadata,
    )
    created = db.get_chunk(chunk_id)
    if not created:
        raise HTTPException(status_code=500, detail="Chunk creation failed")
    return created


@router.get("/", response_model=List[Chunk])
def list_chunks():
    return db.get_all_chunks()


@router.get("/{chunk_id}", response_model=Chunk)
def get_chunk(chunk_id: str = Path(..., description="The ID of the chunk")):
    chunk = db.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


@router.put("/{chunk_id}", response_model=Chunk)
def update_chunk(chunk_id: str, chunk_update: ChunkUpdate):
    if not db.chunk_exists(chunk_id):
        raise HTTPException(status_code=404, detail="Chunk not found")
    db.update_chunk(
        chunk_id,
        content=chunk_update.content,
        embedding=chunk_update.embedding,
        metadata=chunk_update.metadata,
    )
    return db.get_chunk(chunk_id)


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chunk(chunk_id: str):
    if not db.delete_chunk(chunk_id):
        raise HTTPException(status_code=404, detail="Chunk not found")
