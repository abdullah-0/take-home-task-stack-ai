from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.chunk import Chunk


class DocumentBase(BaseModel):
    title: str
    metadata: Optional[dict] = None


class DocumentCreate(DocumentBase):
    library_id: str


class DocumentUpdate(DocumentBase):
    pass


class Document(DocumentBase):
    id: str
    library_id: str
    created_at: datetime
    chunks: List[Chunk] = Field(default_factory=list)
