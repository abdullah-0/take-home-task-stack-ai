from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ChunkBase(BaseModel):
    content: str
    embedding: List[float]
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
