from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChunkBase(BaseModel):
    content: str
    metadata: Optional[dict] = None


class ChunkCreate(ChunkBase):
    document_id: str


class ChunkUpdate(ChunkBase):
    pass


class Chunk(ChunkBase):
    id: str
    document_id: str
    library_id: str
    created_at: datetime


class SearchRequestSchema(BaseModel):
    library_id: str
    query: str
    k: int = 5

class SearchResultChunk(BaseModel):
    chunk: Chunk
    score: float


