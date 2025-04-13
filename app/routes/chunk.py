
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from app.core.v_db import VectorDB
from app.schemas import Chunk, ChunkCreate, ChunkUpdate
from app.utils import get_db

router = APIRouter()


@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
async def create_chunk(
        document_id: str = Path(..., description="The ID of the parent document"),
        chunk: ChunkCreate = ...,
        db: VectorDB = Depends(get_db)
):
    """
    Create a new text chunk with vector embedding
    """
    if not db.document_exists(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    chunk_id = db.create_chunk(
        document_id=document_id,
        text=chunk.text,
        embedding=chunk.embedding,
        metadata=chunk.metadata or {}
    )

    created_chunk = db.get_chunk(chunk_id)
    if not created_chunk:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chunk"
        )
    return created_chunk


@router.get("/", response_model=List[Chunk])
async def list_chunks(
        document_id: str = Path(..., description="The ID of the parent document"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: VectorDB = Depends(get_db)
):
    """
    List all chunks in a document with pagination
    """
    if not db.document_exists(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return db.get_chunks_in_document(
        document_id=document_id,
        skip=skip,
        limit=limit
    )


@router.get("/{chunk_id}", response_model=Chunk)
async def get_chunk(
        document_id: str = Path(..., description="The ID of the parent document"),
        chunk_id: str = Path(..., description="The ID of the chunk"),
        db: VectorDB = Depends(get_db)
):
    """
    Get a specific chunk by ID
    """
    chunk = db.get_chunk(chunk_id)
    if not chunk or chunk["document_id"] != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found in specified document"
        )
    return chunk


@router.put("/{chunk_id}", response_model=Chunk)
async def update_chunk(
        document_id: str = Path(..., description="The ID of the parent document"),
        chunk_id: str = Path(..., description="The ID of the chunk"),
        chunk_update: ChunkUpdate = ...,
        db: VectorDB = Depends(get_db)
):
    """
    Update a chunk's content or metadata
    """
    current_chunk = db.get_chunk(chunk_id)
    if not current_chunk or current_chunk["document_id"] != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found in specified document"
        )

    success = db.update_chunk(
        chunk_id=chunk_id,
        text=chunk_update.text,
        embedding=chunk_update.embedding,
        metadata=chunk_update.metadata
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chunk"
        )

    return db.get_chunk(chunk_id)


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(
        document_id: str = Path(..., description="The ID of the parent document"),
        chunk_id: str = Path(..., description="The ID of the chunk"),
        db: VectorDB = Depends(get_db)
):
    """
    Delete a chunk
    """
    chunk = db.get_chunk(chunk_id)
    if not chunk or chunk["document_id"] != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found in specified document"
        )

    if not db.delete_chunk(chunk_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chunk"
        )

#
# @router.post("/search", response_model=List[SearchResult])
# async def search_chunks(
#         document_id: str = Path(..., description="The ID of the parent document"),
#         search_query: SearchQuery = ...,
#         db: VectorDB = Depends(get_db)
# ):
#     """
#     Perform vector similarity search on chunks
#
#     Parameters:
#     - query_embedding: The embedding vector to compare against
#     - k: Number of nearest neighbors to return
#     - index_type: Which index to use (FLAT, IVF, HNSW)
#     - filters: Optional metadata filters
#     """
#     if not db.document_exists(document_id):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Document not found"
#         )
#
#     results = db.search_chunks(
#         document_id=document_id,
#         query_embedding=search_query.query_embedding,
#         k=search_query.k,
#         index_type=search_query.index_type,
#         filters=search_query.filters
#     )
#
#     return [
#         {
#             "chunk_id": result["chunk_id"],
#             "text": result["text"],
#             "score": result["score"],
#             "metadata": result["metadata"]
#         }
#         for result in results
#     ]