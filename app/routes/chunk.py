from typing import List

from fastapi import APIRouter, HTTPException, status, Path

from app.core.v_db import VectorDB
from app.schemas.chunk import Chunk, ChunkCreate, ChunkUpdate, SearchResultChunk, SearchRequestSchema
from app.services.cohere_embedding import get_embedding

router = APIRouter(prefix="/v1/chunk",tags=["Chunk"])
db = VectorDB()


@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
def create_chunk(chunk_in: ChunkCreate):
    try:
        chunk_id = db.create_chunk(
            document_id=chunk_in.document_id,
            content=chunk_in.content,
            metadata=chunk_in.metadata,
        )
        return db.get_chunk(chunk_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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



@router.post("/search", response_model=List[SearchResultChunk])
def search_chunks(request: SearchRequestSchema, vector_db=None):
    # Embed the query using Cohere
    try:
        query_embedding = get_embedding(request.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cohere embedding failed: {str(e)}")

    # Search in VectorDB
    results = vector_db.search_chunks(
        library_id=request.library_id,
        query_embedding=query_embedding,
        k=request.k
    )

    return [{"chunk": chunk, "score": score} for chunk, score in results]